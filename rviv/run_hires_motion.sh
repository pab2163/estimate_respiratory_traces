#!/bin/bash

NIFTI_IMAGE=$1
JSON_FILE="${NIFTI_IMAGE/.nii.gz/.json}"
ID=$(basename $NIFTI_IMAGE | awk -F_ 'BEGIN{OFS="_";} {print $1,$2}')

OUTPUT_STACKS=/tmp/stacks # CHANGE IF YOU WANT TO OUTPUT STACKS SOMEWHERE ELSE

#python stackify.py $NIFTI_IMAGE $JSON_FILE $OUTPUT_STACKS

#find $OUTPUT_STACKS -name *"$ID"*.nii.gz -type f | xargs -I {} -P 20 bash -c '3dvolreg -Fourier -1Dfile $(echo "{}"|sed '\''s/.nii.gz/.1D/'\'') -zpad 4 -prefix NULL "{}"'

python join_stacks.py $OUTPUT_STACKS $ID 16 404 rest-1400.1D
python notch_filter_stack.py "$ID"_rest-1400.1D 0.7 11.42857
