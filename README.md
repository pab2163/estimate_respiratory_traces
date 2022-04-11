Adapted from: Hocke, & Fredrick. (2020). Post‐hoc physiological waveform extraction from motion estimation in simultaneous multislice (SMS) functional MRI using separate stack processing

BreathLess is a script to extract a predicted respiratory waveform from fMRI data. The script takes an fMRI image in BIDS format with the proper json sidecar. If you do not have this, I suggest subclassing the BidsImg class to trick the Breathless script into thinking the file is in proper bids format. 

# Instructions

* System requirements - 3dvolreg
* Python requirements - in requirements.txt


1. Install dependencies with 'pip install -r requirements'

2. Run script with 'python breathless/breathless.py <name_of_bids_file>'

Requirements: 

    * Data must be in BIDS format

    * Data must have BIDS json sidecar containing: SliceTiming, RepetitionTime, PhaseEncodingDirection

