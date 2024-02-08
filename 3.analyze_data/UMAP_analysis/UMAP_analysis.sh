#!/bin/bash

# initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
conda init bash

# activate the R specific conda environment
conda activate R_jump_sc

# convert all notebooks to python files into the nbconverted folder
jupyter nbconvert --to script --output-dir=nbconverted/ *.ipynb

# run notebooks in order
python nbconverted/0.merge_JUMP_metadata_probab.py
python nbconverted/1.fs_all_JUMP_plates.py
python nbconverted/2.jump_UMAP.py
Rscript nbconverted/3.vis_mito_jump.r
Rscript nbconverted/4.vis_only_JUMP.r


