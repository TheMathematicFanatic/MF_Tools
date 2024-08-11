from manim import *

def Vcis(theta, clockwise=False):
    if clockwise:
        return np.sin(theta)*RIGHT + np.cos(theta)*UP
    else:
        return np.cos(theta)*RIGHT + np.sin(theta)*UP

class VT(ValueTracker):
    def __invert__(self):
        return self.get_value()
    def __matmul__(self, v):
        return self.animate.set_value(v)

def get_intersection(line1, line2):
    return line_intersection(
        line1.get_start(),
        line1.get_end(),
        line2.get_start(),
        line2.get_end()
    )
Line.get_intersection = get_intersection

