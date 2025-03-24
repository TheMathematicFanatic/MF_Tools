from .dual_compatibility import *

class Arc3d(VMobject): #Credit to @uwezi on Manim Discord
    def __init__(self, A=None, B=None, center=None, radius=1, segments=40, **kwargs):
        super().__init__(**kwargs)
        start = center + normalize(A-center)*radius
        end   = center + normalize(B-center)*radius
        self.set_points([start])
        for i in np.linspace(0,1,segments,endpoint=True):
            dotonline = start + i*(end-start)
            radline = dotonline-center
            dotonarc = center + normalize(radline)*radius
            self.add_smooth_curve_to(dotonarc)