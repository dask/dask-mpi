#!/bin/bash

set -e
set -eo pipefail

conda config --set always_yes true --set changeps1 false --set quiet true
conda clean --all
conda update --all
conda config --add channels conda-forge
conda env create -f .circleci/env-${PYTHON}-${MPI}.yml --name=${ENV_NAME} --quiet
conda env list
conda activate ${ENV_NAME}
pip install --no-deps --quiet -e .
conda list -n ${ENV_NAME}
