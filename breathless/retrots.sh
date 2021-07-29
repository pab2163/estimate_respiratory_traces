#!/bin/bash
set -e


PHYSIO_FILE=$1
IMAGE_FILE=$2
SLICE_ORDER_FILE=$3
HZ=$4
TR=$5
N_SLICES=$6
PREFIX=$(basename $IMAGE_FILE | cut -d"." -f1)

RetroTS.py -r $PHYSIO_FILE -p $HZ -n $N_SLICES -v $TR -cardiac_out 0 -slice_order $SLICE_ORDER_FILE -prefix $PREFIX
1dcat $PREFIX.slibase.1D | sponge $PREFIX.slibase.1D
3dDetrend -polort 9 -prefix rm.ricor.$PREFIX.1D $PREFIX.slibase.1D\'
1dtranspose rm.ricor.$PREFIX.1D rm.ricor_det_r.$PREFIX.1D
3dDeconvolve -polort 9 -input $IMAGE_FILE -x1D_stop -x1D $PREFIX.xmat.1D
3dREMLfit -input $IMAGE_FILE -matrix $PREFIX.xmat.1D -Obeta rm.$PREFIX.betas -Oerrts rm.$PREFIX.errts -slibase_sm rm.ricor_det_r.$PREFIX.1D -verb
3dSynthesize -matrix $PREFIX.xmat.1D -cbucket rm.$PREFIX.betas+orig'[0..9]' -select polort -prefix rm.$PREFIX.polort
3dcalc -a rm.$PREFIX.errts+orig -b rm.$PREFIX.polort+orig -datum short -nscale -expr a+b -prefix $PREFIX.ricor.nii.gz
