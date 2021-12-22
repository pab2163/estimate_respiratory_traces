from breathless.BreathLess import BreathLess, BidsImg


def read_img():
    return BidsImg("test_data/sub-A00085795_ses-BAS1_task-rest_acq-1400_bold.nii.gz")


def test_make_breathless():
    bl = BreathLess(read_img())
    assert bl is not None


def test_calc_slices():
    bl = BreathLess(read_img())
    so = bl.calc_slice_order()
    assert so[0] == [0, 16, 32, 48]


def test_print_meta_information():
    bl = BreathLess(read_img())
    bl.print_meta_information()


def test_reorder():
    from pathlib import Path

    bl = BreathLess(read_img())
    premade_stack = list(Path("test_data").glob("stack*1D"))
    premade_stack.sort()
    reordered_stack = bl.concat_stack(premade_stack)
    assert len(reordered_stack) == 48


def test_filtering():
    import numpy as np

    bl = BreathLess(read_img())
    reordered = (
        "test_data/sub-A00085795_ses-BAS1_task-rest_acq-1400_bold_stack_reordered.1D"
    )
    data = np.genfromtxt(reordered)
    filtered = bl.filter_pe(data)
    assert filtered is not None
    assert filtered.shape[0] == 48
