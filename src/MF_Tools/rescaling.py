from .dual_compatibility import *

def scale_to_fit(mobject:Mobject, len_x=None, len_y=None, len_z=None, buff=0.25, scale_stroke_width=False):
    fit_lengths = [len_ for len_ in [len_x, len_y, len_z] if len_ is not None and len_ > 1e-10]
    if any(fit_lengths):
        mobject_lengths = [mobject.get_width(), mobject.get_height(), mobject.get_depth()]
        scale_values = [(len_-2*buff) / mobject_lengths[i] for i,len_ in enumerate(fit_lengths)]
        mobject.scale_with_stroke_width(min(scale_values), scale_stroke_width)
    return mobject
Mobject.scale_to_fit = scale_to_fit

def scale_to_fit_mobject(mobject:Mobject, other_mobject:Mobject, **kwargs):
    mobject.scale_to_fit(len_x=other_mobject.get_width(), len_y=other_mobject.get_height(), len_z=other_mobject.get_depth(), **kwargs)
    return mobject
Mobject.scale_to_fit_mobject = scale_to_fit_mobject

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