from manim import *


def Vcis(theta, clockwise=False):
    if clockwise:
        return np.sin(theta)*RIGHT + np.cos(theta)*UP
    else:
        return np.cos(theta)*RIGHT + np.sin(theta)*UP


class VT(ValueTracker): #Credit to @Abulafia on Manim Discord
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


class SurroundingRectangleUnion(VGroup):
    def __init__(self, *mobjects, buff=0.1, corner_radius=0.0, stroke_color=YELLOW, **kwargs):
        polygons = []
        rectagles = VGroup(*[SurroundingRectangle(m, buff=buff) for m in mobjects])
        union = Union(*rectagles, **kwargs)
        beziers = [union.points[i:i+4] for i in range(0, len(union.points), 4)]
        current_polygon = []
        for bez in beziers:
            if len(current_polygon) == 0:
                current_polygon.append(bez[0])
            elif all(bez[-1] == current_polygon[0]):
                current_polygon.append(bez[0])
                polygons.append(current_polygon)
                current_polygon = []
            else:
                current_polygon.append(bez[0])
        
        for poly in polygons:
            pass # figure out orientation and then shift all the corners inward by the same amount (buff/2?)

        super().__init__(
            *[Polygon(*poly) for poly in polygons],
            stroke_color=stroke_color,
            **kwargs
        )
        if corner_radius > 0:
            for poly in self:
                poly.round_corners(corner_radius)




        # super().__init__(
        #     *[union.points[i] for i in range(0, len(union.points), 4)],
        #     stroke_color=stroke_color,
        #     )
        # if corner_radius > 0:
        #     self.round_corners(corner_radius)

# Needs to be a Polygram to use .round_corners
# Can't be a Polygram since sometimes it is disconnected
# Hmm...