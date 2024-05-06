from . import _version
from .core import initialize, send_close_signal
from .exceptions import WorldTooSmallException

__version__ = _version.get_versions()["version"]
