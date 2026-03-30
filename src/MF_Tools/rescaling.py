from .dual_compatibility import *


# Monkeypatching all these functions as Mobject methods so that they can be .animated

def maintain_apparent_stroke_width(mobject, camera, recursive=True):
    if len(mobject.submobjects) == 0 or not recursive:
        original_stroke_width = mobject.get_stroke_width()
        original_camera_width = camera.frame.get_width()
        def update_stroke_width(mob):
            mob.set_stroke(width = original_stroke_width * original_camera_width / camera.frame.get_width())
        mobject.add_updater(update_stroke_width)
    else:
        for submob in mobject.get_family():
            maintain_apparent_stroke_width(submob, camera, recursive=submob != mobject)
    return mobject
Mobject.maintain_apparent_stroke_width = maintain_apparent_stroke_width

def scale_with_stroke_width(mobject, scale_factor=1, scale_stroke_width=True):
    if scale_stroke_width:
        for submob in mobject.get_family():
            submob.set_stroke(width = submob.get_stroke_width() * scale_factor)
    mobject.scale(scale_factor)
    return mobject
Mobject.scale_with_stroke_width = scale_with_stroke_width


def scale_to_fit(
	mobject:Mobject,
	len_x = None,
	len_y = None,
	len_z = None,
	buff = 0,
	scaleback = 1,
	min_scale = None,
	max_scale = None,
	scale_stroke_width = False,
):
	fit_lengths = [len_ if len_ and len_ > 1e-6 else None for len_ in [len_x, len_y, len_z]]
	mobject_lengths = [mobject.get_width(), mobject.get_height(), mobject.get_depth()]
	scale_factors = []
	for dim in [0,1,2]:
		if fit_lengths[dim] is not None:
			scale_value = (fit_lengths[dim]-2*buff) / mobject_lengths[dim] * scaleback
			scale_value = np.clip(scale_value, min_scale, max_scale)
			scale_factors.append(scale_value)
	scale_value = min(scale_factors)
	scale_with_stroke_width(mobject, scale_value, scale_stroke_width)
	return mobject
Mobject.scale_to_fit = scale_to_fit


def scale_to_fit_mobject(mobject:Mobject, other_mobject:Mobject, **kwargs):
    scale_to_fit(
		mobject,
		len_x = other_mobject.get_width(),
		len_y = other_mobject.get_height(),
		len_z = other_mobject.get_depth(),
		**kwargs
	)
    return mobject
Mobject.scale_to_fit_mobject = scale_to_fit_mobject

