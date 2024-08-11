__version__ = '1.0.0'
__author__ = 'John Connell - The Mathematic Fanatic'
__description__ = 'Manim plugin with a variety of helpful utilities'

from .transforms import *
from .updaters import *
from .misc import *

#from manim_play_timeline import *

"""
.expressions contains the main mobject classes of the entire plugin
.actions contains the animation classes, not currently imported because they are not ready yet
.utils not imported because they are intended for internal use only
.nicknames not imported, they are intended to be optionally imported with * if desired.


from manim import *
import manim_smart_algebra as msa
from manim_smart_algebra.nicknames import * #optional

or something like that depending on preferences. I personally will do

from manim import *
from manim_smart_algebra import *
from manim_smart_algebra.nicknames import *
"""
