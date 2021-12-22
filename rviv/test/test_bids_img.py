from breathless.BreathLess import BidsImg
import pytest


def read_img():
    return BidsImg("test_data/sub-A00085795_ses-BAS1_task-rest_acq-1400_bold.nii.gz")


def test_bids_img():
    bi = read_img()
    assert bi is not None


def test_bids_img_not_found():
    with pytest.raises(FileNotFoundError):
        BidsImg("test_data/file-that-does-not-exist.nii.gz")


def test_read_sidecar():
    bi = read_img()
    bi.get_sidecar()


def test_read_TR():
    bi = read_img()
    tr = bi.get_bids_info("RepetitionTime")
    assert tr == 1.4


def test_read_SliceTiming():
    bi = read_img()
    st = bi.get_bids_info("SliceTiming")
    assert len(st) == 64

def test_num_vols():
    bi = read_img()
    vols = bi.get_nvols()
    assert vols == 3

def test_get_pe():
    bi = read_img()
    assert bi.get_bids_info("PhaseEncodingDirection") == "j-"


