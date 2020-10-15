import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tensorflow as tf
from sklearn.metrics import confusion_matrix, f1_score, fbeta_score
from tf_agents.trajectories import time_step as ts
from tf_agents.trajectories import trajectory
from tqdm import tqdm


def metrics_by_network(network, X, y):
    """Computes the confusion matrix for a given dataset."""
    q, _ = network(X)
    y_pred = np.argmax(q.numpy(), axis=1)  # Max action for each x in X

    return classify_metrics(y, y_pred)


def metrics_by_policy(X_val, y_val, policy):
    y_pred = []

    for x in X_val:
        tf_x = tf.constant(x, shape=(1, 29))
        time_step = ts.transition(observation=tf_x, reward=0.0, outer_dims=(1, 29,))
        action_step = policy.action(time_step)
        y_pred.append(action_step.action)

    y_pred = tf.stack(y_pred)
    return classify_metrics(y_val, y_pred)


def classify_metrics(y_true, y_pred):
    TN, FP, FN, TP = confusion_matrix(y_true, y_pred).ravel()

    recall = TP / denom if (denom := TP + FN) else 0  # Sensitivity, True Positive Rate (TPR)
    specificity = TN / denom if (denom := TN + FP) else 0  # Specificity, selectivity, True Negative Rate (TNR)

    G_mean = np.sqrt(recall * specificity)  # Geometric mean of recall and specificity
    Fdot5 = fbeta_score(y_true, y_pred, beta=0.5, zero_division=0)  # β of 0.5
    F1 = f1_score(y_true, y_pred, zero_division=0)  # Default F-measure
    F2 = fbeta_score(y_true, y_pred, beta=2, zero_division=0)  # β of 2

    return {"Gmean": G_mean, "Fdot5": Fdot5, "F1": F1, "F2": F2, "TP": TP, "TN": TN, "FP": FP, "FN": FN}


def plot_confusion_matrix(TP, FN, FP, TN):
    ticklabels = ("Minority", "Majority")
    sns.heatmap(((TP, FN), (FP, TN)), annot=True, fmt="_d", cmap="viridis", xticklabels=ticklabels, yticklabels=ticklabels)

    plt.title("Confusion matrix")
    plt.xlabel("Predicted labels")
    plt.ylabel("True labels")
    plt.show()


def collect_step(environment, policy, buffer):
    """Data collection for 1 step."""
    time_step = environment.current_time_step()
    action_step = policy.action(time_step)
    next_time_step = environment.step(action_step.action)
    traj = trajectory.from_transition(time_step, action_step, next_time_step)

    buffer.add_batch(traj)


def collect_data(env, policy, buffer, steps: int, logging: bool = False):
    """Collect data for a number of steps. Mainly used for warmup period."""
    if logging:
        for _ in tqdm(range(steps)):
            collect_step(env, policy, buffer)
    else:
        for _ in range(steps):
            collect_step(env, policy, buffer)


def split_csv(fp: str = "./data/creditcard.csv", fp_dest: str = "./data", name: str = "credit", chunksize: int = 220_000):
    """
    Splits a csv file every `chuncksize` lines.
    Based on https://stackoverflow.com/a/36644425/10603874
    """
    for i, chunk in enumerate(pd.read_csv(fp, chunksize=chunksize)):
        chunk.to_csv(f"{fp_dest}/{name}{i}.csv", index=False)


if __name__ == "__main__":
    import pickle

    from dqnimp.data import load_data

    imb_rate = 0.00173  # Imbalance rate
    min_class = [1]  # Minority classes, must be same as trained model
    maj_class = [0]  # Majority classes, must be same as trained model
    datasource = "credit"  # The dataset to be selected
    _, _, X_test, y_test, _, _ = load_data(datasource, imb_rate, min_class, maj_class)  # Load all data

    with open("./models/20201007_121850.pkl", "rb") as f:  # Load the Q-network
        network = pickle.load(f)

    metrics = metrics_by_network(network, X_test, y_test)
    print(*[(k, round(v, 6)) for k, v in metrics.items()])

    plot_confusion_matrix(metrics.get("TP"), metrics.get("FN"), metrics.get("FP"), metrics.get("TN"))