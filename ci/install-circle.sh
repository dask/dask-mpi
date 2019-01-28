#!/bin/bash

set -e
set -eo pipefail

export PATH="/opt/conda/bin:${PATH}"

conda config --set always_yes true --set changeps1 false --set quiet true
conda update -q conda
conda init bash # Initialize bash shell, this is new in conda 4.6
conda config --set pip_interop_enabled True # Enable pip interoperability
conda config --add channels conda-forge
conda env create -f ci/environment-dev-${PYTHON}-${MPI}.yml --name=${ENV_NAME} --quiet
conda env list
conda activate ${ENV_NAME}
pip install pip --upgrade
pip install --no-deps --quiet -e .
conda list -n ${ENV_NAME}
