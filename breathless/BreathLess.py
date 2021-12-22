import json
import nibabel as nib
from pathlib import Path
from AfniRunner import AfniRunner
from Filtering import Filtering
import numpy as np
import fire
import os

class BreathLess:
    """
    Runs the algorithm defined in:
    Hocke, & Fredrick. (2020).
    (BidsImg, output) -> np.array
    """

    def __init__(
        self,
        bids_img,
        runner=AfniRunner("/opt/afni/"),
        tmp_folder="/tmp/stacks",
        output_folder=".",
    ):
        """
        Initialize parameters
        """
        self.bids_img = bids_img
        self.slice_order = None
        self.tmp_folder = tmp_folder
        self.runner = runner
        self.output_folder = output_folder

    def calc_slice_order(self):
        slice_timing = self.bids_img.get_bids_info("SliceTiming")
        slice_order = [
            [ind for ind, x in enumerate(slice_timing) if x == time]
            for time in sorted(list(set(slice_timing)))
        ]
        return slice_order

    def print_meta_information(self):
        if self.slice_order is None:
            self.slice_order = self.calc_slice_order()
        tr = self.bids_img.get_bids_info("RepetitionTime")
        pe_direction = self.bids_img.get_bids_info("PhaseEncodingDirection")
        num_trs = self.bids_img.get_nvols()
        num_stacks = len(self.slice_order)
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
        print(
            """
            The slices at time 0 are: {}
            """.format(
                self.slice_order[0]
            )
        )

    def stackify(self):
        if self.slice_order is None:
            self.slice_order = self.calc_slice_order()
        outpath = Path(self.tmp_folder)
        outpath.mkdir(exist_ok=True)
        self.bids_img.read_image()
        self.bids_img.read_data()
        imname = self.bids_img.name
        stack_paths = []
        for ind, timeslice in enumerate(self.slice_order):
            stack = self.bids_img.img[:, :, timeslice, :]
            stack_img = nib.Nifti1Image(stack, self.bids_img.nii.affine)
            outname = Path(outpath) / "stack{:02d}_{}.nii.gz".format(ind, imname)
            nib.save(stack_img, str(outname))
            # multiply voxel thickenss of slices in stacks by the total # of stacks
            current_slice_thickness = self.bids_img.header['pixdim'][3]
            new_thickness = self.bids_img.header * len(self.slice_order)
            print(f'Updating I-S slice thickness from {current_slice_thickness} to {new_thickness}')
            refit_cmd = f'3drefit -zdel {new_thickness} {str(outname)}'
            os.system(refit_cmd)
            stack_paths.append(outname)
        return stack_paths

    def motion_correction(self, stack_paths):
        """ Uses the runner to run image motion correction """
        motion_paths = []
        for stack_image in stack_paths:
            ret, motion_path = self.runner.run_motion_correction(stack_image)
            if ret != 0:
                raise ValueError("There was an error in motion correction")
            else:
                motion_paths.append(motion_path)
        return motion_paths

    def concat_stack(self, motion_paths):
        if self.slice_order is None:
            self.slice_order = self.calc_slice_order()
        if motion_paths != sorted(motion_paths):
            print("motion paths weren't already sorted, are you sure this is right?")
            print("auto sorting motion paths")
            motion_paths.sort()

        assert len(motion_paths) == len(self.slice_order)
        full_stack = [np.genfromtxt(stack_entry) for stack_entry in motion_paths]
        stack_array = np.array(full_stack)
        try:
            # Reshape to time X 6
            stack_reordered = np.reshape(
                stack_array,
                (len(motion_paths) * self.bids_img.get_nvols(), 6),
                order="F",
            )
        except ValueError as e:
            print("reshaping motion paths has failed")
            raise ValueError
        outpath = Path(self.output_folder) / "{name}_stack_reordered.txt".format(
            name=self.bids_img.name
        )
        np.savetxt(str(outpath), stack_reordered, fmt="%.04f")
        return stack_reordered

    def filter_pe(self, data, lowcut=0.15, highcut=0.6):
        if self.slice_order is None:
            self.slice_order = self.calc_slice_order()
        pe_direction = self.bids_img.get_bids_info("PhaseEncodingDirection")
        if pe_direction[0] == "i":
            pe_vector = data[:, -2]  # should be x in AFNI (dL)
        elif pe_direction[0] == "j":
            pe_vector = data[:, -1]  # should be y in AFNI (dP)
        elif pe_direction[0] == "k":
            pe_vector = data[:, -3]  # should be z in AFNI (dS)
        else:
            raise ValueError("Unsupported PE direction {}".format(pe_direction))
        tr = float(self.bids_img.get_bids_info("RepetitionTime"))
        notch_val = 1 / tr
        num_stacks = len(self.slice_order)
        hz = 1 / (tr / num_stacks)
        print(
            "Notch filtering at {:.3f}, {:.3f}, {:.3f}".format(
                notch_val, notch_val * 2, notch_val * 3
            )
        )
        print("Hz is {:.3f}".format(hz))
        notch_filtered = Filtering().notch_harmonics(pe_vector, notch_val, hz)
        bandpass_filtered = Filtering().butter_bandpass(
            notch_filtered, lowcut, highcut, hz
        )
        return bandpass_filtered

    def __call__(self):
        self.slice_order = self.calc_slice_order()
        self.print_meta_information()
        stacks = self.stackify()
        motion = self.motion_correction(stacks)
        reordered = self.concat_stack(motion)
        filtered = self.filter_pe(reordered)
        output = Path(self.output_folder) / "{}_breathless.txt".format(
            self.bids_img.name
        )
        np.savetxt(str(output), filtered)


class BidsImg:
    """
    Reads in a filepath and gets corresponding bids files
    DOES NOT CHECK BIDS FORMAT IN GENERAL
    Override to pretend a dataset is in bids format that actually isn't
    (filepath) -> BidsImg
    """

    def __init__(self, path_to_nifti_image):
        im = Path(path_to_nifti_image)
        if not im.exists():
            raise FileNotFoundError("path to nifti image does not exist!")
        self.path_to_image = path_to_nifti_image
        self.path_to_json = self.get_sidecar_path(path_to_nifti_image)
        self.nii = None
        self.img = None
        self.sidecar = None
        self.name = im.name.split(".")[0]

    def read_image(self):
        """Read in image path with nibabel"""
        self.nii = nib.load(self.path_to_image)

    def read_data(self):
        """Read data from nifti **slow**"""
        if self.nii:
            self.img = self.nii.get_fdata()

    @staticmethod
    def get_sidecar_path(nifti_image_path):
        """Transform nifti file path to json file path"""
        if nifti_image_path.endswith(".nii.gz"):
            json_path = nifti_image_path.replace(".nii.gz", ".json")
        elif nifti_image_path.endswith(".nii"):
            json_path = nifti_image_path.replace(".nii", ".json")
        else:
            raise ValueError("Nifti file must end with .nii.gz or .nii")
        if not Path(json_path).exists():
            raise FileNotFoundError(
                "The json sidecar was not found: {}".format(json_path)
            )
        return json_path

    def get_sidecar(self):
        with open(self.path_to_json) as f:
            nifti_json = json.load(f)
        if not (nifti_json.get("RepetitionTime") and nifti_json.get("SliceTiming")):
            raise ValueError(
                "JSON sidecar is either missing the RepetitionTime or SliceTiming \n "
                "Is this BIDS?"
            )
        else:
            self.sidecar = nifti_json

    def get_bids_info(self, key):
        if not self.sidecar:
            self.get_sidecar()
        res = self.sidecar.get(key)
        if res:
            return res
        else:
            print("Key was not found! Check whether it exists")
            return None

    def get_nvols(self):
        if self.nii is None:
            self.read_image()
        return self.nii.shape[-1]


def run(path, path_to_afni="/opt/afni", tmp_folder="/tmp/stacks", output_folder="."):
    runner = AfniRunner(path_to_afni)
    bl = BreathLess(
        BidsImg(path), runner=runner, tmp_folder=tmp_folder, output_folder=output_folder
    )
    bl()


if __name__ == "__main__":
    fire.Fire(run)
