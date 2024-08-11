from manim import *


def keep_orientation(scene, *mobjects):
    for mob in mobjects:
        mob.orientation_line = Line().set_opacity(0).move_to(mob.get_center())
        mob.add(mob.orientation_line)
    def keep_orientation_updater(dt):
        for mob in mobjects:
            mob[:-1].rotate(-mob[-1].get_angle(), about_point=mob[:-1].get_center())
    scene.add_updater(keep_orientation_updater)
Scene.keep_orientation = keep_orientation


