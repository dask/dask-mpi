from ._version import get_versions
from .exceptions import WorldTooSmallException  # noqa
from .execute import execute, send_close_signal  # noqa
from .initialize import initialize  # noqa

__version__ = get_versions()["version"]
del get_versions
