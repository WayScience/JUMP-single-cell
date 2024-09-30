# justfile for common project commands
# see here for more information: https://github.com/casey/just

# find system default shell
hashbang := if os() == 'macos' {
	'#!/usr/bin/env zsh'
} else {
	'#!/usr/bin/env bash'
}

# show a list of just commands for this project
default:
  @just --list

# setup conda envs
@setup-conda-envs:
    #!{{hashbang}}
    conda remove -n jump_sc --all
    conda remove -n R_jump_sc --all
    conda env create -n jump_sc -f environment.yml
    conda env create -n R_jump_sc -f R_environment.yml
