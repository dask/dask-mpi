from ._version import get_versions
from .core import initialize, send_close_signal

__version__ = get_versions()["version"]
del get_versions
