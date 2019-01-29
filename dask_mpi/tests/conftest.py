import pytest
import os


@pytest.fixture
def allow_run_as_root():
    try:
        ALLOW_RUN_AS_ROOT = bool(os.environ.get("ALLOW_RUN_AS_ROOT"))
    except:
        ALLOW_RUN_AS_ROOT = False

    return ALLOW_RUN_AS_ROOT
