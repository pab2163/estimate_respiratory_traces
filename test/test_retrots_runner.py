from breathless.RunRetroTS import run_retrots

def test_retrots_runner():
    breathless = "/tmp/full_img/sub-A00085795_ses-BAS1_task-rest_acq-1400_bold_breathless.txt"
    nifti = "/tmp/full_img/sub-A00085795_ses-BAS1_task-rest_acq-1400_bold.nii.gz"
    run_retrots(breathless, nifti)

