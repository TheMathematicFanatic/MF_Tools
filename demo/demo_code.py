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
        pass
        


class Demo_indexx_labels(Scene):
    def construct(self):
        M1 = MathTex("a^2+b^2=c^2")
        M2 = MathTex("\\sin \\left(", "{a^2+b^2}", "\\over", "{3n+1}", "\\right)")
        self.add(VGroup(M1, M2.scale(2)).arrange(DOWN, buff=1))
        self.add(indexx_labels(M1), indexx_labels(M2))


