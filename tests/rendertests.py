from manim import *
import sys
import os
# Add the src directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from MF_Tools.transforms import *


class TransformTest(Scene):
    def construct(self):
        exp1 = MathTex("{ 3x+2y } \\over { 2x+y }")
        exp2 = MathTex("\\left( { 2x+y } \\over { 3x+2y } \\right) ^-1")
        self.add(exp1)
        self.play(TransformByGlyphMap(exp1, exp2,
        
        ))