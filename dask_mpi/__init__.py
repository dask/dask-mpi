from ._version import get_versions
from .core import MPIRunner, initialize

__version__ = get_versions()["version"]
del get_versions
