from breathless.BreathLess import BidsImg
from pathlib import Path
import argparse
import numpy as np
import subprocess
import os

dir_path = os.path.dirname(os.path.realpath(__file__))


def run_retrots(respiration, nifti, afni_folder="/opt/afni"):
    bi = BidsImg(nifti)
    tr = bi.get_bids_info("RepetitionTime")
    slice_timing = bi.get_bids_info("SliceTiming")
    np.savetxt(Path(dir_path)/"st.txt", slice_timing, fmt="%.05f")
    slice_order = [
        [ind for ind, x in enumerate(slice_timing) if x == time]
        for time in sorted(list(set(slice_timing)))
    ]
    physio_hz = 1 / (tr / len(slice_order))
    num_slices = len(slice_timing)
    myenv = os.environ.copy()
    myenv["PATH"] = ":".join([myenv["PATH"], dir_path, afni_folder])
    cmd = "retrots.sh {phys} {nifti} {st_file} {hz} {tr} {nslices}".format(
        dirpath=dir_path,
        phys=respiration,
        nifti=nifti,
        st_file=Path(dir_path)/"st.txt",
        hz=round(physio_hz, 4),
        tr=tr,
        nslices=num_slices,
    )
    print("Running command: \n", cmd)
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, env=myenv)
    output, error = process.communicate()
    print(output, error)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the afni procedure for RVT+Retroicor using RetroTS"
    )
    parser.add_argument(
        "respiration",
        help="the respiration for a subject (e.g. the *breathless.txt file)",
    )
    parser.add_argument("nifti", help="path to a bids formatted image with sidecar")
    args = parser.parse_args()
