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

# run all steps
@run-all-steps:
    #!{{hashbang}}
    source 0.download_data/run.sh

# run step 0.download_data
@run-step-0:
    #!{{hashbang}}
    source 0.download_data/run.sh
