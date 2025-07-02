from os.path import dirname, basename, isfile, join
import glob
from importlib import import_module
modules = glob.glob(join(dirname(__file__), "*.py"))
files = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py') and not f.startswith('base')]

from .base import Notifier
notifiers = []
for file in files:
    module = import_module(f'.{file}', __package__)
    for x in filter(lambda x: not x.startswith('__'), dir(module)):
        clazz = getattr(module, x)
        if issubclass(clazz, Notifier) and clazz is not Notifier:
            notifiers.append(clazz)