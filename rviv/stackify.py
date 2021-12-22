import nibabel as nib
from pathlib import Path
import json
import os
import fire


def stackify(impath, jsonpath, outpath):
    outpath = Path(outpath)
    outpath.mkdir(exist_ok=True)
    with open(jsonpath) as f:
        header = json.load(f)
    slices = [
        [ind for ind, x in enumerate(header["SliceTiming"]) if x == time]
        for time in sorted(list(set(header["SliceTiming"])))
    ]
    nii = nib.load(impath)
    img = nii.get_fdata()
    imname = impath.split(os.path.sep)[-1]
    stack_paths = []
    for ind, timeslice in enumerate(slices):
        stack = img[:, :, timeslice, :]
        stack_img = nib.Nifti1Image(stack, nii.affine)
        outname = Path(outpath) / "stack{:02d}_{}".format(ind, imname)
        nib.save(stack_img, str(outname))
        stack_paths.append(outname)
    return stack_paths


if __name__ == "__main__":
    fire.Fire(stackify)
