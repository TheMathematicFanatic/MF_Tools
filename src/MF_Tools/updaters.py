from .dual_compatibility import *


def keep_orientation(scene, *mobjects):
    for mob in mobjects:
        mob.orientation_line = Line().set_opacity(0).move_to(mob.get_center())
        mob.add(mob.orientation_line)
    def keep_orientation_updater(dt):
        for mob in mobjects:
            mob[:-1].rotate(-mob[-1].get_angle(), about_point=mob[:-1].get_center())
    scene.add_updater(keep_orientation_updater)
Scene.keep_orientation = keep_orientation

"""
Idk about these, should rethink...
Possibly should go in geometry also

def always_label_tippable(tippable, distance=0.5):
    def updater(mob, dt):
        start_to_end_vect = tippable.get_end() - tippable.get_start()
        center_point = tippable.point_from_proportion(0.5)
        start_to_end_vect /= np.linalg.norm(start_to_end_vect)
        normal = np.array([-start_to_end_vect[1], start_to_end_vect[0], 0])
        mob.move_to(center_point + normal*distance)
    return updater
always_label_line = always_label_tippable
always_label_arc = always_label_tippable
always_label_arrow = always_label_tippable


def always_label_edge(polygram, edge_number, distance=0.5):
    def updater(mob, dt):
        vertices = polygram.get_vertices()
        edge = vertices[edge_number-1] - vertices[edge_number]
        edge_center = vertices[edge_number] + edge/2
        edge /= np.linalg.norm(edge)
        edge_normal = np.array([-edge[1], edge[0], 0])
        mob.move_to(edge_center + edge_normal*distance)
    return updater


def always_label_vertex(polygram, vertex_number, distance=0.5):
    def updater(mob, dt):
        vertices = polygram.get_vertices()
        center_point = center_of_mass(vertices)
        vertex_direction = vertices[vertex_number] - center_point
        vertex_direction /= np.linalg.norm(vertex_direction)
        mob.move_to(vertices[vertex_number] + vertex_direction*distance)
    return updater
"""