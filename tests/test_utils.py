import pytest
import dqnimp.utils as utils


def test_plot_confusion_matrix():
    """Tests dqnimp.utils.plot_confusion_matrix."""
    with pytest.raises(ValueError) as exc:
        utils.plot_confusion_matrix(1, 2, 3, "test")
    assert "Not all arguments are integers" in str(exc.value)


def test_split_csv(tmp_path):
    """Tests dqnimp.utils.split_csv."""
    cols = "Time,V1,V2,V3,V4,V5,V6,V7,V8,V9,V10,V11,V12,V13,V14,V15,V16,V17,V18,V19,V20,V21,V22,V23,V24,V25,V26,V27,V28,Amount,Class\n"
    row = str(list(range(31))).strip("[]") + "\n"

    with pytest.raises(FileNotFoundError) as exc:
        utils.split_csv(fp=tmp_path / "thisfiledoesnotexist.csv", fp_dest=tmp_path)
    assert "File at" in str(exc.value)

    with open(data_file := tmp_path / "data_file.csv", "w") as f:
        f.writelines([cols, row, row])

    with pytest.raises(ValueError) as exc:
        utils.split_csv(fp=data_file, fp_dest=tmp_path / "thisfolderdoesnotexist")
    assert "Directory at" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        utils.split_csv(fp=data_file, fp_dest=tmp_path, test_size=0.0)
    assert "is not in interval" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        utils.split_csv(fp=data_file, fp_dest=tmp_path, test_size=1)
    assert "is not in interval" in str(exc.value)