# Welcome!
MF-Tools is a collection of various utilities that are helpful for creating Manim scenes.

The most significant among them is TransformByGlyphMap, but there are also several other small tools in the collection, and I expect to continue to grow the collection over time.

I recommend installing with `pip install MF_Tools`


## Recent changes:
- Major refactor for my personal satisfaction and use in a future library.
- The "delay" kwarg now alters the rate_func and run_time behind the scenes, instead of using Succession and Wait, so all Succession-related problems should be resolved.
- An alternative mode, in which the unmentioned glyphs are simply introduced/removed (default is fades) instead of transformed into one another, can now be activated by the `auto_fade` parameter.
- For both the original and this new alternative mode, the parameter `auto_resolve_delay` controls the delay before the unmentioned glyphs are dealt with.


# Transforms

## TransformByGlyphMap

Video demonstration: https://youtu.be/IbVymn040T4

This animation class dramatically simplifies the process and syntax of animating complicated transformations of complicated mobjects. It can be used on any VMobjects, but it was conceived to be used with MathTex for things like algebra animations. Thus, many of the default parameters are specific to this use case, and some of the language I use in this documentation is specific to this use case, such as using "glyph" and "submobject" interchangeably.

Like all Transforms, it receives two mobjects, but its primary parameter after that is its glyph_map. This consists of an arbitrary number of 2-tuples of lists of integers, such as

`([3,4,8,9], [0,1,3]),` <br>
`([0], [5]),` <br>
`([1,2], [2,4])` <br>

Each tuple will send the VGroup of glyphs/submobjects at the first list of indices in the starting mobject, to the VGroup of glyphs/submobjects at the second list of indices in the target mobject, with a simple `ReplacementTransform`.

If one of the lists is empty, such as

`([], [1,4]),` <br>
`([8,9,10], [])`

it will instead trigger an introducer (default `FadeIn`) or a remover (default `FadeOut`) to act on that VGroup of glyphs. If you would prefer a different introducer/remover, you can replace the empty list with the animation of your choice, such as

`(Write, [5,6,7,8])`

Each glyph_map entry can receive an optional third element, which is a dictionary of kwargs to be passed to the corresponding animation. For example,

`([3,4,5], [5,6,7], {"path_arc":PI/2}),` <br>
`([7,8,9,10,11], [], {"run_time":1.5, "delay":0.5})`

`delay` is a special kwarg which will cause the animation produced by that entry to wait for that many seconds before starting.

TransformByGlyphMap has two modes: its regular mode, which transforms mobject glyphs into one another, and its alternate `show_indices` mode, which places both the original and target mobjects vertically next to each other and reveals the index labels of the submobjects. This mode is intended to assist the user in filling out the indices of the glyph_map, without requiring them to call and then delete a different function (namely `index_labels`) to do so. The alternate mode can be triggered in several ways, including with the parameter `show_indices=True`, or by passing an empty glyph_map, or an empty glyph_map entry `([], [])`.

As the glyph_map is parsed, all of the indices that are mentioned are recorded for both the original and target mobjects. If a glyph_map entry contains an index from the original mobject that has already occurred, a copy of that glyph is given to the corresponding animation so as not to disturb the action of the other animations already acting on that glyph. When the entire glyph_map has been parsed and converted into animations, it is expected that the all of the indices that have NOT been mentioned will be equally numerous between the original and target mobjects. If so, each of those glyphs will be `ReplacementTransform`ed into one another, in order, so that every single glyph of the original is accounted for and transformed into a glyph of the target. If the unmentioned indices are not equally numerous, it will switch to `show_indices` mode. This is intended to help the user in correcting an index mistake.

If you're still awake after all that, here is a demonstration:
```py
class Demo_TransformByGlyphMap0(Scene):
    def construct(self):
        exp1 = MathTex("f(x) = 4x^2 + 5x + 6").scale(2)
        exp2 = MathTex("f(-3) = 4(-3)^2 + 5(-3) + 6").scale(2)
        self.add(exp1)
        self.wait()
        self.play(TransformByGlyphMap(exp1, exp2))
        self.wait()
```
![](/demo/resources/Demo_TransformByGlyphMap0.gif)

I recommend one first pass no glyph_map to trigger the `show_indices` mode. By inspecting the indices, the user can then fill in the glyph_map. Notice how only the "active" indices need to be mentioned in the glyph_map. All of the inactive indices automatically know where to go, because they are equally numerous between the two mobjects and so are just transformed into each other in order, resulting in the inactive glyphs sliding over to their new positions without any specific direction from the user.

```py
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
```
![](/demo/resources/Demo_TransformByGlyphMap1.gif)

TransformByGlyphMap can accept many additional parameters to control its behavior. The following is an exhaustive list of its parameters and what they do:

- **mobA -** Starting mobject (required)
- **mobB -** Target mobject (required)
- **\*glyph_map -** Arbitrarily long sequence of tuples of lists of integers. Each one can have an optional third element which is a dictionary of kwargs. This is certainly the most important parameter and controls almost everything that happens. See above for a detailed explanation.
- **auto_fade -** Boolean, defaults to False. When False, the unmentioned indices will be ReplacementTransformed into one another if they are the same length, or will trigger show_indices mode if they are not the same length. If True, then an alternative mode is used: unmentioned_indices will be introduced/removed by the default introducer/remover, and there is no need or check for the unmentioned indices to be the same length.
- **from_copy -** Boolean, defaults to False. If True, then the original mobA will be left alone while a copy of it is transformed into mobB.
- **mobA_submobject_index -** List of integers. Determines which submobject of mobA, or which submobject of which submobject of mobA, etc., upon which to act. For example, [0,3,1] will cause it to act on mobA[0][3][1].Defaults to [0], which is perfect for the structure of MathTex mobjects.
- **mobB_submobject_index -** List of integers, defaults to [0]. Same as mobA_submobject_index, but for the target mobject.
- **default_introducer -** Animation, defaults to FadeIn. The introducer to use when the first list of indices in a glyph_map entry is empty.
- **default_remover -** Animation, defaults to FadeOut. The remover to use when the second list of indices in a glyph_map entry is empty.
- **introduce_individually -** Boolean, defaults to False. If True, then introducers will be applied individually to each submobject mentioned by a glyph_map entry, rather than to them all as a VGroup. Makes no difference for FadeIn, but can be nicer for Write or GrowFromPoint.
- **remove_individually -** Boolean, defaults to False. Same as introduce_individually, but for the removal animations.
- **shift_fades -** Boolean, defaults to True. If True, then the introducers and removers will receive a shift parameter in the general direction of motion between the two mobjects being operated on. Really only noticeable if the two mobjects are in substantially different positions, it can be jarring for most glyphs to travel far but the fades stay in place. This shift can be overwritten by glyph_map kwargs.
- **auto_resolve_delay -** Float, defaults to 0.5. The delay applied to the introducers/removers that are applied to the unmentioned indices when auto_resolve is True, or to the ReplacementTransforms that are applied to the unmentioned indices when auto_resolve is False.
- **show_indices -** Boolean, defaults to False. If True, then the results of the glyph_map are ultimately discarded (although it is still processed) and the indices of the submobjects being operated on are shown. This is useful for writing the glyph_map in the first place, making it easy to see which indices need to go where and in what way. This mode can also be triggered by an empty glyph_map, by the presence of an empty glyph_map entry `([], [])`, or by a mismatch in the number of indices not mentioned in the glyph_map (if auto_fade is False).
- **A_index_labels_color -** Color, defaults to RED_D. The color of the index labels of the submobjects of mobA. Does nothing if show_indices is False and the animation proceeds successfully. The show_indices mode is only intended to be shown to the programmer and not the final viewer; I encourage you change it in the source code to your taste.
- **B_index_labels_color -** Color, defaults to BLUE_D. Same as A_index_labels_color, but for mobB.
- **index_label_height -** Float, defaults to 0.18. Determines the size of the index_labels. This is just the size I thought was nicest; change in the source code to your taste.
- **printing -** Boolean, defaults to False. If True, then each entry of the glyph_map is printed to the console, followed by the lists of all mentioned and unmentioned indices from both mobA and mobB.
- **\*\*kwargs -** Arbitrary keyword arguments. These are passed to the ReplacementTransforms of the unmentioned indices, and to the final AnimationGroup of everything. Also passed to the animations generated by mentioned indices, but are overwritten by any kwargs in the entry.

Here are a few more examples of how you can use TransformByGlyphMap:

```py
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
```
![](/demo/resources/Demo_TransformByGlyphMap2.gif)

```py
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
```
![](/demo/resources/Demo_TransformByGlyphMap3.gif)

```py
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
```
![](/demo/resources/Demo_TransformByGlyphMap4.gif)

```py
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
```
![](/demo/resources/Demo_TransformByGlyphMap5.gif)

```py
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
```
![](/demo/resources/Demo_TransformByGlyphMap6.gif)

```py
class Demo_TransformByGlyphMap7(Scene):
    def construct(self):
        exp1 = MathTex("1 \\over x").scale(1.8)
        exp2 = MathTex("{ { 1 \\over x } - { 1 \\over x } } + 10").scale(1.8)
        self.add(exp1)
        self.wait()
        self.play(TransformByGlyphMap(exp1, exp2,
            ([0,1,2], [0,1,2]),
            ([0,1,2], [4,5,6]),
            default_introducer=Write,
            auto_fade=True
        ))
        self.wait()
```
![](/demo/resources/Demo_TransformByGlyphMap7.gif)


# Common Updaters

## Scene.keep_orientation()
***WARNING: Currently bugged/incomplete, as can be seen in the demo below***

Within a Scene one can perform

`self.keep_orientation(mob1, mob2, ...)`

This creates a scene updater which will maintain the orientation of all the passed mobjects, even if the higher mobject they may be a part of is rotated.
It achieves this by giving each mobject an invisible line as a submobject, and uses this line to measure and reset the mobject's angle.
Do not use this if the presence of this new submobject would disturb other code.

In this example, `side_length` is added as a submobject to `square`, so normally it would rotate with it.
Indeed, its position is rotated with the square, but because of `self.keep_orientation`, it remains upright.

```py
def construct(self):
    square = Square()
    side_length = MathTex("1.8").next_to(square, RIGHT)
    square.add(side_length)
    self.add(square)
    self.keep_orientation(side_length)
    self.play(Write(side_length))
    self.play(Rotate(square, 3*PI/2, about_point=ORIGIN, run_time=2))
    self.wait()
```
![](/demo/resources/Demo_keep_orientation.gif)


# Geometry

## Arc3d
Simple 3D arc for any orientation, invented by @uwezi. Receives three points as the start, end, and center.

```py
class Demo_Arc3d(ThreeDScene):
    def construct(self):
        cs = ThreeDAxes().set_color(GRAY)
        self.add(cs)
        C = Dot3D([1,3,1])
        self.add(C)
        self.move_camera(phi=75 * DEGREES, theta=25 * DEGREES)
        self.begin_ambient_camera_rotation(rate=0.2)
        A = Dot3D([2,0,3]).set_color(RED)
        B = Dot3D([-2,-2,-2]).set_color(BLUE)
        CA = Line(C.get_center(), A.get_center())
        CB = Line(C.get_center(), B.get_center())      
        self.add(A,B)
        self.play(Create(CA), Create(CB))
        self.play(Create(Arc3d(A=A.get_center(), B=B.get_center(), center=C.get_center(), radius=1.5, segments=30)))
        self.wait(6)
```
![](/demo/resources/Demo_Arc3d.gif)


# Miscellaneous

## Vcis(angle)
Have you ever found yourself writing the idiom `np.cos(angle)*RIGHT + np.sin(angle)*UP`? No longer!

This simple function returns the unit vector pointing in the direction of the given angle, measured counterclockwise from the positive x-axis. If `clockwise=True` is passed, instead the angle is measured clockwise from the positive y-axis.

Its name means the vector version of the cis function, or the cos + i*sin function.

```py
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
```
![](/demo/resources/Demo_Vcis.png)


## VT(number)
Shorthand subclass of Manim's ValueTracker, invented by @Abulafia.
It has the following shorthands compared to its superclass:

| VT Shorthand            | ValueTracker Longhand                              |
| ----------------------- | -------------------------------------------------- |
| `val = VT(5)`           | `val = ValueTracker(5)`                            |
| `~val`                  | `val.get_value()`                                  |
| `val @= 3`              | `val.set_value(3)`                                 |
| `self.play(val @ 9)`    | `self.play(val.animate.set_value(9))`              |
| `val += 4`              | `val.increment_value(4)`                           |
| `self.play(val + 4)`    | `self.play(val.animate.increment_value(4))`        |
| `val -= 4`              | `val.increment_value(-4)`                          |
| `self.play(val - 4)`    | `self.play(val.animate.increment_value(-4))`       |

The original syntax still works fine with it as well.

```py
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
```
![](/demo/resources/Demo_VT.gif)


## DN(callable)
Shorthand for Manim's DecimalNumber with automatic updaters.
Receives a ValueTracker or callable as its first argument, followed by any other arguments accepted by Manim's DecimalNumber class.
Automatically receives an updater which will keep it accurate to the current state of its ValueTracker or callable.
```py
class Demo_DN(Scene):
    def construct(self):
        r = VT(1)
        circ = always_redraw(lambda: Circle(~r))
        r_dec = DN(r)
        d_dec = DN(lambda: circ.width)
        A_dec = DN(lambda: PI*(~r)**2)
        Nums = VGroup(r_dec, d_dec, A_dec).arrange(down)
        self.add(circ, Nums)
        self.wait()
        self.play(r@3)
        self.wait()
```
![](/demo/resources/Demo_DN.gif)

## bounding_box(mobject)
This function returns a VGroup of Dots and Lines which represent the critical points and bounding box of a mobject. Helpful as a debugging or explanatory tool for stuff that depends on alignment with critical points.

The optional `always` parameter can be set to True in order for it to receive an updater which will always keep it accurate to the current state of its mobject.

The optional `include_center` parameter can be set to True if you'd like a dot for the center of the bounding box.
```py
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
```
![](/demo/resources/Demo_bounding_box.gif)


## indexx_labels(mobject)
This is an upgrade to Manim's `index_labels`.

It uses multiple colors to show the indices of two layers of submobjects instead of just one, very useful for multi-string Tex mobjects. By default it cycles through the six standard rainbow colors, but you can pass your own list of colors as the `colors` parameter.

The height of the labels changes proportionally to the height of the mobject. If you'd prefer a certain size, you can pass it as the `label_height` parameter.

```py
class Demo_indexx_labels(Scene):
    def construct(self):
        M1 = MathTex("a^2+b^2=c^2")
        M2 = MathTex("\\sin \\left(", "{a^2+b^2}", "\\over", "{3n+1}", "\\right)")
        self.add(VGroup(M1, M2.scale(2)).arrange(DOWN, buff=1))
        self.add(indexx_labels(M1), indexx_labels(M2))
```
![](demo/resources/Demo_indexx_labels.png)


## SurroundingRectangleUnion(*mobjects)
Takes several mobjects and returns a VMobject that surrounds them. Inspired by @Viks on Manim Discord.

First it constructs SurroundingRectangles around each mobject with the given `buff` parameter and then Unions them all together. This may result in a single polygon, or multiple polygons, up to one for each mobject if none intersect. Tune so that as many of them merge as you desire.

Next it pulls in all the sides by the distance specified by the `unbuff` parameter. Tune so that adjacent SurroundingRectangleUnions of different objects don't intersect each other.

Finally it rounds all of the corners according to the `corner_radius` parameter. Tune to your liking.

It can accept any kwargs that VMobjects accept, such as stroke_color and stroke_width.

```py
class Demo_SurroundingRectangleUnion1(Scene):
    def construct(self):
        V = VGroup(*[Circle(0.5, color=GRAY) for _ in range(36)]).arrange_in_grid(rows=4, cols=9)
        self.add(V, index_labels(V))
        groups = [
            [0,1,2,9,10],
            [3,4,5,11,12,13,14,15,21,30,33,34,35],
            [24,25,16,17,8,27,28,29]
        ]
        for group, color in zip(groups, [RED, GREEN, BLUE]):
            self.add(SurroundingRectangleUnion(*[V[i] for i in group], buff=0.2, unbuff=0.12, corner_radius=0.25, stroke_color=color))
```
![](/demo/resources/Demo_SurroundingRectangleUnion1.png)

This next one uses ValueTrackers to sorta demonstrate how the shapes are constructed.

```py
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
```
![](/demo/resources/Demo_SurroundingRectangleUnion2.gif)

It can be used on any mobjects. I like how it looks with an updater.

```py
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
```
![](/demo/resources/Demo_SurroundingRectangleUnion3.gif)
