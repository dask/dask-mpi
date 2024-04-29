from .core import initialize, send_close_signal
from .exceptions import WorldTooSmallException
from . import _version

__version__ = _version.get_versions()["version"]
