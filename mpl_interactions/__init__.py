try:
    from ._version import __version__
except ImportError:
    __version__ = "unkown"
from .generic import *
from .helpers import *
from .pyplot import *
from .utils import *
