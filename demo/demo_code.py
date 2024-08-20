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
        r = VT(1)
        circ = always_redraw(lambda: Circle(~r))
        r @= 2
        self.add(circ)
        self.play(r@3)
        self.wait()
        self.play(r-1)
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
        coord = CoordPair(dot, next_to_dir=DOWN, size=0.5, background_rectangle=True, decimal_number_kwargs={"num_decimal_places": 1})
        dumb_coord = MathTex("(-2,3)")
        dumb_coord.to_edge(DOWN)
        self.add(NumberPlane())
        self.add(dot, coord, dumb_coord)
        self.wait()
        self.play(dot.animate.move_to([5.5, -3, 0]), run_time=0.5)
        self.wait()


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


class Demo_SurroundingRectangleUnion(Scene):
    def construct(self):
        V_mobs = VGroup(
            C := Circle().shift(DL*2),
            T := Text("Hello"),
            M := MathTex("a^2+b^2=c^2").shift(2*UP),
        )
        buffvt, unbuffvt, cornervt = VT(1), VT(0.2), VT(0.25)
        V_dec = VGroup(
            buff_dec := DN(buffvt),
            unbuff_dec := DN(unbuffvt),
            corner_dec := DN(cornervt),
        ).arrange(RIGHT).to_edge(DOWN)
        self.add(V_mobs, V_dec)
        self.add(
            always_redraw(lambda: 
                SurroundingRectangleUnion(
                    *V_mobs,
                    buff=~buffvt,
                    unbuff=~unbuffvt,
                    corner_radius=~cornervt,
                    stroke_color=GREEN,
                )
            )
        )
        self.play(buffvt @ 3)
        self.wait()
        self.play(unbuffvt @ 0)
        self.wait()
        self.play(cornervt @ 0)
        self.wait()
        self.play(unbuffvt @ 0.5)
        self.wait()
        self.play(buffvt@1)
        self.wait()
        self.play(unbuffvt @ 0)
        self.wait()
        self.play(cornervt @ 0.1)
        self.wait()
        self.play(buffvt @ 0)
        self.wait()
        self.play(C.animate.shift(UR*5), run_time=4)
        self.wait()


class Demo_SurroundingRectangleUnion2(Scene):
    def construct(self):
        V = VGroup(*[Circle(0.5) for _ in range(36)]).arrange_in_grid(rows=4, cols=9)
        self.add(V)
        self.add(SurroundingRectangleUnion(*V[0:3], *V[9:11], buff=0.2, unbuff=0.18, corner_radius=0.25, stroke_color=GREEN))
        self.add(SurroundingRectangleUnion(*V[3:6], *V[11:16], V[21], V[30], *V[33:36], buff=0.2, unbuff=0.18, corner_radius=0.25, stroke_color=BLUE))
        self.add(index_labels(V))




