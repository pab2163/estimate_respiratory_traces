import pandas as pd
import numpy as np
import re
from pathlib import Path
import json
import fire
from scipy import signal
import matplotlib.pyplot as plt

warehouse_path = Path("/projects/public_warehouse/bids_warehouse/")


def correl_physio(file):
    filtered = np.genfromtxt(file)
    name = Path(file).name
    a_number, visit, imtype = re.match(
        r"(sub-A000\d\d\d\d\d)_(ses-\w+)_task-rest_(acq-\d+)_bold_full_filtered.1D",
        name,
    ).groups()
    phys_path = (
        warehouse_path
        / a_number
        / visit
        / "func"
        / "{}_{}_task-rest_{}_physio.tsv.gz".format(a_number, visit, imtype)
    )
    json_path = (
        warehouse_path
        / a_number
        / visit
        / "func"
        / "{}_{}_task-rest_{}_physio.json".format(a_number, visit, imtype)
    )
    with open(json_path) as f:
        j = json.load(f)
    resp = np.genfromtxt(phys_path)[:, j["Columns"].index("respiratory")]
    resp_resampled = signal.resample(resp, len(filtered))
    df = pd.DataFrame(np.concatenate((resp_resampled.reshape((-1, 1)).T, filtered.T)).T)
    df.columns = ["resp", "roll", "pitch", "yaw", "dS", "dL", "dP"]
    print(df.corr())


if __name__ == "__main__":
    fire.Fire(correl_physio)
