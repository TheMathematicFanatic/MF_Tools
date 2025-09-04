from .dual_compatibility import *


def debug_glyph(
        scene,
        glyph_mobject,
        writing_dot=True,
        writing_cycle_length=5,
        writing_dot_color=BLUE,
        show_dot_count=False,
		dot_count_direction=DOWN
    ):
	glyph_mobject.data_dots = VGroup([
		Dot(d[0], radius=0.01*max(glyph_mobject.get_width(), glyph_mobject.get_height()))
		for d in glyph_mobject.data
	])
	glyph_mobject.data_dots[::2].set_opacity(0.25)
	glyph_mobject.data_dots[1::2].set_opacity(0.1)
	glyph_mobject.set_opacity(0.1)
	scene.add(glyph_mobject.data_dots)
	if writing_dot:
		glyph_mobject.writing_dot = GlowDot(color=writing_dot_color, radius=0.06*max(glyph_mobject.get_width(), glyph_mobject.get_height()))
		writing_dot_anim = MoveAlongPath(glyph_mobject.writing_dot, glyph_mobject, run_time=writing_cycle_length)
		scene.add(glyph_mobject.writing_dot)
		turn_animation_into_updater(writing_dot_anim, cycle=True)
	if show_dot_count:
		num_dots = len(glyph_mobject.data_dots)
		glyph_mobject.dot_count = Text('Data points: ' + str(num_dots))
		#glyph_mobject.dot_count.scale_to_fit(len_x=glyph_mobject.get_width())
		glyph_mobject.dot_count.scale(max(0.1,glyph_mobject.get_width()/glyph_mobject.dot_count.get_width()))
		glyph_mobject.dot_count.next_to(glyph_mobject, dot_count_direction, buff=glyph_mobject.get_height()/4)
		scene.add(glyph_mobject.dot_count)
Scene.debug_glyph = debug_glyph

def debug_glyphs(scene, *mobjects, **kwargs):
	for M in mobjects:
		for g in M:
			debug_glyph(scene, g, **kwargs)
Scene.debug_glyphs = debug_glyphs


def bounding_box(mobject, always=False, include_center=False):
    if always:
        return always_redraw(lambda: bounding_box(mobject, always=False, include_center=include_center))
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
        for i in range(len(mobject.submobjects))
    ])