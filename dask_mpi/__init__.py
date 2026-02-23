from importlib.metadata import version

from .exceptions import WorldTooSmallException  # noqa
from .execute import execute, send_close_signal  # noqa
from .initialize import initialize  # noqa

__version__ = version("dask-mpi")
