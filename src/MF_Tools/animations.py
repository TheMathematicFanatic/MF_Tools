from .dual_compatibility import Animation, ORIGIN

class GhostSlideFade(Animation):
    def __init__(self, mob, scale_factor=1, shift_vector=ORIGIN, rotate_amount = 0, fade_in_time=1, fade_out_time=1, lifetime=3, living_stroke_opacity=1, living_fill_opacity=0, **kwargs):
        self.mobject = mob
        self.scale_factor = scale_factor
        self.shift_vector = shift_vector
        self.rotate_amount = rotate_amount
        self.fade_in_time = fade_in_time
        self.fade_out_time = fade_out_time
        self.lifetime = lifetime
        self.living_stroke_opacity = living_stroke_opacity
        self.living_fill_opacity = living_fill_opacity
        super().__init__(mob, **kwargs)

    def begin(self):
        super().begin()

    def clean_up_from_scene(self, scene):
        super().clean_up_from_scene(scene)
        scene.remove(self.mobject)

    def interpolate_mobject(self, alpha):
        alpha = self.rate_func(alpha)
        total_time = self.fade_in_time + self.lifetime + self.fade_out_time
        self.mobject.become(self.starting_mobject)
        self.mobject.scale(self.scale_factor**alpha)
        self.mobject.shift(self.shift_vector * alpha)
        self.mobject.rotate(self.rotate_amount * alpha, about_point=self.mobject.get_center_of_mass())
        if alpha <= self.fade_in_time / total_time:
            factor = alpha / (self.fade_in_time / total_time)
        elif alpha > self.fade_in_time / total_time and alpha < 1 - self.fade_out_time / total_time:
            factor = 1
        elif alpha >= 1 - self.fade_out_time / total_time:
            factor = (1 - alpha) / (self.fade_out_time / total_time)
        self.mobject.set_fill(opacity = self.living_fill_opacity * factor)
        self.mobject.set_stroke(opacity = self.living_stroke_opacity * factor)
