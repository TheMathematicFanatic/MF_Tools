from manim import *
from .updaters import keep_orientation


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
    def __imatmul__(self, v):
        self.set_value(v)


def bounding_box(mobject, always=False):
    if always:
        return always_redraw(lambda: bounding_box(mobject))
    size = min(mobject.get_width(), mobject.get_height())
    dot_size = np.clip(size/12, 0.02, 0.06)
    critical_dots = VGroup(
        *[Dot(mobject.get_critical_point(v), radius=dot_size, color=GREEN_D) for v in [UL, UR, DR, DL]],
        *[Dot(mobject.get_critical_point(v), radius=dot_size, color=RED_B) for v in [LEFT, RIGHT, UP, DOWN]]
    )
    edges = VGroup(*[
        Line(critical_dots[i].get_center(), critical_dots[(i+1)%4].get_center(),
            buff=0, stroke_width=2, stroke_opacity=0.5
            )
        for i in range(4)
    ])
    return VGroup(edges, critical_dots)

    