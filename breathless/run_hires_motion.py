import argparse
from pathlib import Path
from stackify import stackify
from join_stacks import reshape_stacks
from notch_filter_stack import run_filter
import nibabel as nib
import json
import subprocess
import os


class HiresPhysioHelper:
    # Reads in bids information and runs registration
    def __init__(self, nifti_image_path, tmp_path):
        self.nifti_image_path = nifti_image_path
        self.nifti_json_path = self.get_json()
        self.tmp_path = tmp_path

    def get_json(self):
        abspath = Path(self.nifti_image_path).resolve()
        nifti_noext = str(abspath).split(".")[0]
        return "{}.json".format(nifti_noext)

    def run_registration(self, stackpaths):
        # TODO run in parallel
        env = os.environ.copy()
        env["PATH"] = (
            env["PATH"] + ":/opt/afni:/usr/share/fsl/5.0/bin:/usr/lib/fsl/5.0:"
            "/opt/c3d-1.1.0-Linux-gcc64/bin:/opt/c3d/bin"
        )
        motion_paths = []
        processes = []
        for stackpath in stackpaths:
            stack_name = str(stackpath).split(".")[0]
            motion_path = "{}.1D".format(stack_name)
            bashCommand = "3dvolreg -Fourier -1Dfile {} -zpad 4 -prefix NULL {}".format(
                motion_path, stackpath
            )
            print(bashCommand)
            process = subprocess.Popen(
                bashCommand.split(), stdout=subprocess.PIPE, env=env
            )
            processes.append(process)
            motion_paths.append(Path(motion_path))

        for process in processes:
            process.wait()

        return motion_paths

    def get_meta_information(self, num_stacks):
        # TODO: refactor so that stack order is calculated here
        with open(self.nifti_json_path) as f:
            nifti_json = json.load(f)
        tr = nifti_json["RepetitionTime"]
        pe_direction = nifti_json["PhaseEncodingDirection"]
        num_trs = nib.load(self.nifti_image_path).shape[-1]
        print(
            """
            SCAN INFO
            tr is: {},
            phase_encoding_direction (support j+-) is: {}, 
            tr count is: {}, 
            number of timepoints per tr is: {}
            """.format(
                tr, pe_direction, num_trs, num_stacks
            )
        )
        return tr, pe_direction, num_trs, num_stacks


def run_hires(nifti_image, tmp_path="/tmp/stacks"):
    hires = HiresPhysioHelper(nifti_image, tmp_path=tmp_path)
    stack_paths = stackify(
        hires.nifti_image_path, hires.nifti_json_path, hires.tmp_path
    )
    tr, pe_direction, num_trs, num_stacks = hires.get_meta_information(len(stack_paths))
    motion_paths = hires.run_registration(stack_paths)
    filename = "_".join(motion_paths[0].name.split(".")[0].split("_")[3:])
    # get ids
    # TODO refactor this out
    ids = set()
    for motion_path in motion_paths:
        imid = "_".join(motion_path.name.split("_")[1:3])
        ids.add(imid)
    hires_motion = reshape_stacks(
        ids=ids,
        files=motion_paths,
        TIMESLICES=num_stacks,
        SCANS=num_trs,
        FILENAME=filename,
    )
    filtered_hires = run_filter(hires_motion, 1/tr, 1/(tr/num_stacks))
    print(filtered_hires)


if __name__ == "__main__":
    parse = argparse.ArgumentParser("Parse hi-res motion arguments")
    parse.add_argument("nifti_image", help="path to nifti image")
    args = parse.parse_args()
    run_hires(nifti_image=args.nifti_image)
