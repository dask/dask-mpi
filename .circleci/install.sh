#!/bin/bash

set -e
set -eo pipefail

conda config --set always_yes true --set changeps1 false --set quiet true
conda update -q conda
conda config --set pip_interop_enabled True # Enable pip interoperability
conda config --add channels conda-forge
conda env create -f .circleci/env-${PYTHON}-${MPI}.yml --name=${ENV_NAME} --quiet
conda env list
source activate ${ENV_NAME}
pip install pip --upgrade
pip install --no-deps --quiet -e .
conda list -n ${ENV_NAME}
