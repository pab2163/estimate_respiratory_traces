from run_hires_motion import HiresPhysioHelper
from join_stacks import reshape_stacks
from notch_filter_stack import run_filter
import nibabel as nib
import argparse
from pathlib import Path
import json
import os

st = [
    0.0,
    390.0,
    77.5,
    467.5,
    157.5,
    545.0,
    235.0,
    622.5,
    312.5,
    0.0,
    390.0,
    77.5,
    467.5,
    157.5,
    545.0,
    235.0,
    622.5,
    312.5,
    0.0,
    390.0,
    77.5,
    467.5,
    157.5,
    545.0,
    235.0,
    622.5,
    312.5,
    0.0,
    390.0,
    77.5,
    467.5,
    157.5,
    545.0,
    235.0,
    622.5,
    312.5,
    0.0,
    390.0,
    77.5,
    467.5,
    157.5,
    545.0,
    235.0,
    622.5,
    312.5,
    0.0,
    390.0,
    77.5,
    467.5,
    157.5,
    545.0,
    235.0,
    622.5,
    312.5,
    0.0,
    390.0,
    77.5,
    467.5,
    157.5,
    545.0,
    235.0,
    622.5,
    312.5,
    0.0,
    390.0,
    77.5,
    467.5,
    157.5,
    545.0,
    235.0,
    622.5,
    312.5,
]


def stackify(impath, outpath):
    outpath = Path(outpath)
    outpath.mkdir(exist_ok=True)
    slices = [
        [ind for ind, x in enumerate(st) if x == time] for time in sorted(list(set(st)))
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


class HCPHires(HiresPhysioHelper):
    def get_meta_information():
        pass


def run_hires(nifti_image, tmp_path="/tmp/stacks"):
    hires = HCPHires(nifti_image, tmp_path=tmp_path)
    stack_paths = stackify(hires.nifti_image_path, hires.tmp_path)
    tr, pe_direction, num_trs, num_stacks = 0.72, "x", 1200, 9
    motion_paths = hires.run_registration(stack_paths)
    filename = "_".join(motion_paths[0].name.split(".")[0].split("_")[3:])
    print(filename)
    # get ids
    # TODO refactor this out
    ids = set()
    for motion_path in motion_paths:
        imid = "_".join(motion_path.name.split("_")[1:3])
        ids.add(imid)
    print(ids)
    hires_motion = reshape_stacks(
        ids=ids,
        files=motion_paths,
        TIMESLICES=num_stacks,
        SCANS=num_trs,
        FILENAME=filename,
    )
    filtered_hires = run_filter(hires_motion, 1 / tr, 1 / (tr / num_stacks))
    print(filtered_hires)


if __name__ == "__main__":
    parse = argparse.ArgumentParser("Parse hi-res motion arguments")
    parse.add_argument("nifti_image", help="path to nifti image")
    args = parse.parse_args()
    run_hires(nifti_image=args.nifti_image)
