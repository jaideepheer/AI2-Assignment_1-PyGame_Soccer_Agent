__version__ = '0.1.0'

# Load entry point `main`
from .main import *

# GLOBAL logger
from loguru import logger
LOG = logger.opt(colors=True)

# Log tag decorator
from functools import wraps
class LogTag:
    def __init__(self, logger=LOG, tag=None):
        self.lg = logger
        self.tag = tag
    def __call__(self, fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            with self.lg.contextualize(tag=self.tag):
                return fn(*args, *kwargs)
        return decorated