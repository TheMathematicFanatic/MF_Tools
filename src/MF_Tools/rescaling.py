from .dual_compatibility import *

def scale_to_fit(mobject:Mobject, len_x=None, len_y=None, len_z=None, buff=0.25):
    fit_lengths = [len_ for len_ in [len_x, len_y, len_z] if len_ is not None and len_ > 1e-10]
    if any(fit_lengths):
        mobject_lengths = [mobject.get_width(), mobject.get_height(), mobject.get_depth()]
        scale_values = [(len_-2*buff) / mobject_lengths[i] for i,len_ in enumerate(fit_lengths)]
        mobject.scale(min(scale_values))
Mobject.scale_to_fit = scale_to_fit

def scale_to_fit_mobject(mobject:Mobject, other_mobject:Mobject, buff=0.25):
    mobject.scale_to_fit(len_x=other_mobject.get_width(), len_y=other_mobject.get_height(), len_z=other_mobject.get_depth(), buff=buff)
Mobject.scale_to_fit_mobject = scale_to_fit_mobject

