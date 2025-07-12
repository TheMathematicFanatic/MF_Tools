from .dual_compatibility import *
from .misc import VT

class VT_Slider(Group):
    def __init__(self, vt=None, min=0, max=1, dot_color=WHITE, **kwargs):
        if vt is not None:
            self.vt = vt
        else:
            self.vt = VT(min)
        self.min = min
        self.max = max

        self.radius = 1/8
        self.length = 4
        self.bar = RoundedRectangle(width=self.length+2*self.radius, height=2*self.radius, corner_radius=self.radius, fill_opacity=0.5, fill_color=GREY)
        self.slider = Dot(radius=self.radius).move_to(self.bar.get_center() + self.length/2*LEFT).set_color(dot_color)

        super().__init__(self.bar, self.slider, self.vt, **kwargs)

        self.vt.add_updater(lambda v: v.set_value(self.get_current_value()))

    def get_current_value(self):
        percentage = (self.slider.get_center()[0] - self.bar.get_center()[0])/self.length + 0.5
        return self.min + percentage*(self.max - self.min)

