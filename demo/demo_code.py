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



class Demo_SurroundingRectangleUnion1(Scene):
    def construct(self):
        V = VGroup(*[Circle(0.5, color=GRAY) for _ in range(36)]).arrange_in_grid(rows=4, cols=9)
        self.add(V, index_labels(V))
        groups = [
            [0,1,2,9,10],
            [3,4,5,11,12,13,14,15,21,30,33,34,35],
            [24,25,16,17,8,27,28,29]
        ]
        for group, color in zip(groups, [GREEN, BLUE, RED]):
            self.add(SurroundingRectangleUnion(*[V[i] for i in group], buff=0.2, unbuff=0.12, corner_radius=0.25, stroke_color=color))


class Demo_SurroundingRectangleUnion2(Scene):
    def construct(self):
        voters = VGroup(*[Circle(radius=0.6, stroke_color=WHITE, fill_opacity=1, fill_color=BLUE) for _ in range(15)])
        voters.arrange_in_grid(rows=3, cols=5, buff=(0.6, 0.6))
        [voters[i].set(fill_color=GOLD) for i in [0,1,2,5,6,10]]      
        Districts = VGroup(
            VGroup(*[voters[i] for i in [0,1,2,3,4]]),
            VGroup(*[voters[i] for i in [5,6,7,10,11]]),
            VGroup(*[voters[i] for i in [8,9,12,13,14]])
        )
        buffvt, unbuffvt, cornervt = VT(0.1), VT(0), VT(0)
        Borders = VGroup(*[
            always_redraw(lambda district=district:
                SurroundingRectangleUnion(*district, stroke_color=YELLOW, buff=~buffvt, unbuff=~unbuffvt, corner_radius=~cornervt)
            )
            for district in Districts
        ])
        self.add(voters)
        self.play(Create(Borders))
        self.wait()
        self.play(buffvt@0.4)
        self.wait()
        self.play(unbuffvt@0.2)
        self.wait()
        self.play(cornervt@0.3)
        self.wait()


class Demo_SurroundingRectangleUnion3(Scene):
    def construct(self):
        A = Circle().move_to(DL)
        B = Text("Hello").move_to(UP)
        C = MathTex("a^2 + b^2").move_to(RIGHT)
        SR = always_redraw(lambda:
            SurroundingRectangleUnion(A, B, C, buff=0.5, corner_radius=0.1, stroke_color=GREEN)
        )
        self.add(A, B, C, SR)
        self.wait()
        self.play(A.animate.shift(2*LEFT), run_time=2, rate_func=there_and_back)
        self.wait()
        self.play(Rotate(VGroup(A,B,C), TAU), run_time=2)
        self.wait()



class Demo_TransformByGlyphMap0(Scene):
    def construct(self):
        exp1 = MathTex("f(x) = 4x^2 + 5x + 6").scale(2)
        exp2 = MathTex("f(-3) = 4(-3)^2 + 5(-3) + 6").scale(2)
        self.add(exp1)
        self.wait()
        self.play(TransformByGlyphMap(exp1, exp2))
        self.wait()


class Demo_TransformByGlyphMap1(Scene):
    def construct(self):
        exp1 = MathTex("f(x) = 4x^2 + 5x + 6").scale(2)
        exp2 = MathTex("f(-3) = 4(-3)^2 + 5(-3) + 6").scale(2)
        self.add(exp1)
        self.wait()
        self.play(TransformByGlyphMap(exp1, exp2,
            ([2], [2,3]),
            ([6], [7,8,9,10]),
            ([10], [14,15,16,17])
        ))
        self.wait()


class Demo_TransformByGlyphMap2(Scene):
    def construct(self):
        exp1 = MathTex("ax^2 + bx + c = 0").scale(2)
        exp2 = MathTex("x^2 + \\frac{b}{a}x + \\frac{c}{a} = 0").scale(2)
        self.add(exp1)
        self.wait()
        self.play(TransformByGlyphMap(exp1, exp2,
            ([0], [5], {"path_arc":2/3*PI}),
            ([0], [10], {"path_arc":1/2*PI}),
            ([], [4,9]),
            run_time=2
        ))
        self.wait()


class Demo_TransformByGlyphMap3(Scene):
    def construct(self):
        exp1 = MathTex("\\frac{x^2y^3}{w^4z^{-8}}").scale(2)
        exp2 = MathTex("\\frac{x^2y^3z^8}{w^4}").scale(2)
        self.add(exp1)
        self.wait()
        self.play(TransformByGlyphMap(exp1, exp2,
            ([7,9], [4,5]),
            ([8], [], {"shift":UP}),
        ))
        self.wait()


class Demo_TransformByGlyphMap4(Scene):
    def construct(self):
        exp1 = MathTex("{ { 3x+2y \\over 2x+y } + 12z").scale(1.8)
        exp2 = MathTex("\\left( { 2x+y \\over 3x+2y } \\right) ^ {-1} + 12z").scale(1.8)
        self.add(exp1)
        self.wait()
        self.play(TransformByGlyphMap(exp1, exp2,
            ([0,1,2,3,4], [6,7,8,9,10], {"path_arc": PI}),
            ([6,7,8,9], [1,2,3,4], {"path_arc": PI}),
            ([], [0], {"delay":0.5}),
            ([], [11], {"delay":0.5}),
            ([], [12,13], {"delay":0.5}),
            default_introducer=Write
        ))
        self.wait()


class Demo_TransformByGlyphMap5(Scene):
    def construct(self):
        exp1 = MathTex("1 \\over 3r+\\theta").scale(2)
        exp2 = MathTex("\\left( 3r+\\theta \\right) ^ {-1}").scale(2)
        self.add(exp1)
        self.wait()
        self.play(TransformByGlyphMap(exp1, exp2,
            ([2,3,4,5], [1,2,3,4], {"path_arc": -2/3*PI}),
            ([0,1], FadeOut, {"run_time": 0.5}),
            (GrowFromCenter, [0,5,6,7], {"delay":0.25}),
            introduce_individually=True,
        ))
        self.wait()


class Demo_TransformByGlyphMap6(Scene):
    def construct(self):
        exp1 = MathTex("4x^2 - x^2 + 5x + 3x - 7")
        exp2 = MathTex("3x^2 + 8x - 7")
        VGroup(exp1, exp2).arrange(DOWN, buff=1).scale(2)
        self.add(exp1)
        self.wait()
        self.play(TransformByGlyphMap(exp1, exp2,
            ([0,3], [0]),
            ([1,2], [1,2]),
            ([4,5], [1,2]),
            ([7,8,9,10,11], [4,5]),
            from_copy=True
        ))
        self.wait()
