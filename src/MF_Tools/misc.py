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
        return self


def bounding_box(mobject, always=False, include_center=False):
    if always:
        return always_redraw(lambda: bounding_box(mobject))
    size = min(mobject.get_width(), mobject.get_height())
    dot_size = np.clip(size/12, 0.02, 0.06)
    critical_dots = VGroup(
        *[Dot(mobject.get_critical_point(v), radius=dot_size, color=GREEN_D) for v in [UL, UR, DR, DL]],
        *[Dot(mobject.get_critical_point(v), radius=dot_size, color=RED_B) for v in [LEFT, RIGHT, UP, DOWN]]
    )
    if include_center:
        critical_dots += Dot(mobject.get_critical_point(ORIGIN), radius=dot_size, color=BLUE_D)
    edges = VGroup(*[
        Line(critical_dots[i].get_center(), critical_dots[(i+1)%4].get_center(),
            buff=0, stroke_width=2, stroke_opacity=0.5
            )
        for i in range(4)
    ])
    return VGroup(edges, critical_dots)


def indexx_labels(
    mobject,
    colors = [RED_D, ORANGE, YELLOW, GREEN_D, BLUE_D, PURPLE],
    label_height=None,
    **kwargs
    ):
    if label_height is None:
        label_height = max(mobject.get_height()/8, 0.18)
    return VGroup(*[
        index_labels(mobject[i],
            color=colors[i%len(colors)],
            label_height=label_height,
            **kwargs
            )
        for i in range(len(mobject))
    ])