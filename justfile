# justfile for common project commands
# see here for more information: https://github.com/casey/just

# find system default shell
hashbang := if os() == 'macos' {
	'/usr/bin/env zsh'
} else {
	'/usr/bin/env bash'
}

# show a list of just commands for this project
default:
  @just --list

# setup conda envs for this project
@setup-conda-envs:
    #!{{hashbang}}
    # initialize the correct shell for your machine to allow conda to work (see README for note on shell names)
    conda init bash

    # Check if the 'jump_sc' environment exists, and update or create accordingly
    if conda env list | grep -q 'jump_sc'; then
        echo "Updating 'jump_sc' environment"
        conda env update -n jump_sc -f environment.yml --prune
    else
        echo "Creating 'jump_sc' environment"
        conda env create -n jump_sc -f environment.yml
    fi

    # Check if the 'R_jump_sc' environment exists, and update or create accordingly
    if conda env list | grep -q 'R_jump_sc'; then
        echo "Updating 'R_jump_sc' environment"
        conda env update -n R_jump_sc -f R_environment.yml --prune
    else
        echo "Creating 'R_jump_sc' environment"
        conda env create -n R_jump_sc -f R_environment.yml
    fi

    # install kernel for use with jupyter envs
    conda run -n jump_sc python -m ipykernel install --user --name jump_sc --display-name "jump_sc (Python)"


# run jupyter lab through project conda env
@run-jupyter:
    #!{{hashbang}}

    # open a jupyter lab session through conda env
    conda run -n jump_sc jupyter lab

# run all steps
@run-all-steps:
    #!{{hashbang}}

    # setup conda environments
    just setup-conda-envs

    # run step 0.download_data
    source 0.download_data/run.sh

# run step 0.download_data
@run-step-0:
    #!{{hashbang}}

    # run step 0.download_data
    source 0.download_data/run.sh

# run step 0.5.quality_control
@run-step-0-5:
    #!{{hashbang}}

    # run step 0.5.quality_control
    source 0.5.quality_control/run.sh
