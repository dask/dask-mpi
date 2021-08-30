import os

import pytest


@pytest.fixture
def allow_run_as_root():
    try:
        ALLOW_RUN_AS_ROOT = bool(os.environ.get("ALLOW_RUN_AS_ROOT"))
    except Exception:
        ALLOW_RUN_AS_ROOT = False

    return ALLOW_RUN_AS_ROOT


@pytest.fixture
def mpirun(allow_run_as_root):
    if allow_run_as_root:
        return ["mpirun", "--allow-run-as-root"]
    else:
        return ["mpirun"]
