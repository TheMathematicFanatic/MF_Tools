__version__ = '1.2.0'
__author__ = 'John Connell - The Mathematic Fanatic'
__description__ = 'Collection of helpful utilities for Manim'


try:
    from manim import Scene
except:
    from manimlib import Scene




from .transforms import *
from .updaters import *
from .geometry import *
from .misc import *
from .animations import *

