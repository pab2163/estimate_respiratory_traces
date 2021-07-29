from breathless.BreathLess import BreathLess, BidsImg
from breathless.AfniRunner import AfniRunner
import nibabel as nib
import numpy as np

def test_stackify():
    bl = BreathLess(BidsImg("test_data/sub-A00085795_ses-BAS1_task-rest_acq-1400_bold.nii.gz"))
    stacks = bl.stackify()
    assert len(stacks) == 16
    assert nib.load(stacks[0]) is not None

def test_3dvolreg():
    bl = BreathLess(
        BidsImg("test_data/sub-A00085795_ses-BAS1_task-rest_acq-1400_bold.nii.gz"),
        runner=AfniRunner(num_processes=8)
    )
    stacks = bl.stackify()
    motion = bl.motion_correction(stacks)
    assert len(motion) == 16
    assert np.genfromtxt(motion[0]) is not None

def test_reorder():
    bl = BreathLess(
        BidsImg("test_data/sub-A00085795_ses-BAS1_task-rest_acq-1400_bold.nii.gz"),
        runner=AfniRunner(num_processes=8)
    )
    stacks = bl.stackify()
    motion = bl.motion_correction(stacks)
    reordered = bl.concat_stack(motion)
    assert reordered is not None
    assert reordered.shape[0] == 48

def test_full_workflow():
    bl = BreathLess(
        BidsImg("test_data/sub-A00085795_ses-BAS1_task-rest_acq-1400_bold.nii.gz"),
        runner=AfniRunner(num_processes=8)
    )
    bl()

