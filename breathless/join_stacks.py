import pandas as pd
import numpy as np
from pathlib import Path
import os
import matplotlib.pyplot as plt
from scipy import signal
import fire



def getids(filepath, image_id):
    files = list(Path(filepath).glob("*{}*1D".format(image_id)))
    ids = set()
    for file in files:
        imid = "_".join(str(file).split("_")[1:3])
        ids.add(imid)
    return ids, files


def reshape_stacks(ids, files, TIMESLICES, SCANS, FILENAME):
    for imid in ids:
        stack = [stack_entry for stack_entry in files if imid in str(stack_entry)]
        stack = sorted(stack)
        assert len(stack) == TIMESLICES
        full_stack = [np.genfromtxt(stack_entry) for stack_entry in stack]
        stack_array = np.array(full_stack)
        try:
            stack_reordered = np.reshape(
                stack_array, (TIMESLICES * SCANS, 6), order="F"
            )
        except ValueError as e:
            print(e)
            continue
        np.savetxt("{}_{}.txt".format(imid, FILENAME), stack_reordered, fmt="%.04f")
    return "{}_{}".format(imid, FILENAME)


def run(filepath, image_id, timeslices, scans, filename):
    filepath = Path(filepath)
    ids, files = getids(filepath, image_id)
    reshape_stacks(ids, files, timeslices, scans, filename)


if __name__ == "__main__":
    fire.Fire(run)
