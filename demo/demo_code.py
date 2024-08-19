import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from manim import *
from MF_Tools import *

class Demo_keep_orientation(Scene):
    def construct(self):
        square = Square()
        side_length = MathTex("1.8").next_to(square, RIGHT)
        square.add(side_length)
        self.add(square)
        self.keep_orientation(side_length)
        self.play(Write(side_length))
        self.play(Rotate(square, 3*PI/2, about_point=ORIGIN, run_time=2))
        self.wait()


class Demo_Vcis(Scene):
    def construct(self):
        Clock = VGroup(*[
            MathTex(f"{n if n != 0 else 12}").scale(1.5).move_to(3*Vcis(n*PI/6, clockwise=True))
            for n in range(12)
        ])
        hour_hand = Arrow(ORIGIN, 1.5*Vcis(145*DEGREES), buff=0)
        minute_hand = Arrow(ORIGIN, 2.5*Vcis(30*DEGREES), buff=0)
        border = Circle(radius=3.6, color=WHITE)
        self.add(Clock, hour_hand, minute_hand, border)


class Demo_VT(Scene):
    def construct(self):
        r = VT(2)
        r @= 1
        circ = always_redraw(lambda: Circle(~r))
        self.add(circ)
        self.wait()
        self.play(r@3)
        self.wait()


class Demo_DN(Scene):
    def construct(self):
        r = VT(1)
        circ = always_redraw(lambda: Circle(~r))
        r_dec = DN(r)
        d_dec = DN(lambda: circ.width)
        A_dec = DN(lambda: PI*(~r)**2, num_decimal_places=3)
        Nums = VGroup(r_dec, d_dec, A_dec).arrange(DOWN)
        self.add(circ, Nums)
        self.wait()
        self.play(r@3)
        self.wait()


class Demo_CoordPair(Scene):
    def construct(self):
        dot = Dot([-2,3,0])
        coord = CoordPair(dot)
        dumb_coord = MathTex("(-2,3)")
        VGroup(coord, dumb_coord).arrange(RIGHT).to_edge(DOWN)
        self.add(dot, coord, dumb_coord)


        


class Demo_indexx_labels(Scene):
    def construct(self):
        M1 = MathTex("a^2+b^2=c^2")
        M2 = MathTex("\\sin \\left(", "{a^2+b^2}", "\\over", "{3n+1}", "\\right)")
        self.add(VGroup(M1, M2.scale(2)).arrange(DOWN, buff=1))
        self.add(indexx_labels(M1), indexx_labels(M2))


class Demo_bounding_box(Scene):
    def construct(self):
        L = Line(2*DL, 3*RIGHT+UP)
        l = Text("l")
        T = MathTex("a^2 + b^2")
        Tr = T.copy().rotate(PI/4)
        VG = VGroup(L, l, T, Tr).arrange(RIGHT, buff=1)
        self.add(VG)
        for mob in VG:
            self.add(bounding_box(mob, always=True))
        self.wait()
        self.play(*[
            Rotate(mob, TAU, run_time=10) for mob in VG
        ])
