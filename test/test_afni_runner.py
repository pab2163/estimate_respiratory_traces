from breathless.AfniRunner import AfniRunner
import pytest

def test_afni_test():
    ar = AfniRunner()
    ret = ar.test_afni()
    assert ret == 0


def test_afni_volreg():
    ar = AfniRunner()
    img = "test_data/sub-A00085795_ses-BAS1_task-rest_acq-1400_bold.nii.gz"
    ret, _ = ar.run_motion_correction(img)
    assert ret == 0



def test_afni_volreg_fail():
    ar = AfniRunner('/opt/notafni')
    with pytest.raises(FileNotFoundError):
        ret, _ = ar.run_motion_correction("test_data/sub-A00085795_ses-BAS1_task-rest_acq-1400_bold.nii.gz")
        assert ret == 1