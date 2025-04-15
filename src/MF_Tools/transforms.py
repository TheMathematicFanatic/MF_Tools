from .dual_compatibility import *


def ir(a,b): #inclusive_range
    return list(range(a,b+1))


def VG(mob, index_list):
    return VGroup(*[mob[i] for i in index_list])


class TransformByGlyphMap(AnimationGroup):
    def __init__(
        self,
        mobA,
        mobB,
        *glyph_map,
        from_copy=False,
        mobA_submobject_index=[] if MANIM_TYPE == 'GL' else [0],
        mobB_submobject_index=[] if MANIM_TYPE == 'GL' else [0],
        default_introducer=FadeIn,
        default_remover=FadeOut,
        introduce_individually=False,
        remove_individually=False,
        shift_fades=False,
        auto_fade=False,
        auto_resolve_delay=0,
        show_indices=False,
        A_index_labels_color=RED_D,
        B_index_labels_color=BLUE_D,
        index_label_height=0.2,
        printing=False,
        **kwargs
        ):

        self.mobA = mobA
        self.mobB = mobB

        self.default_introducer = default_introducer
        self.default_remover = default_remover
        self.introduce_individually=introduce_individually
        self.remove_individually=remove_individually
        self.shift_fades=shift_fades

        self.show_indices = show_indices or len(glyph_map)==0
        self.printing = printing

        A = self.mobA.copy() if from_copy else mobA
        for i in mobA_submobject_index:
            A = A[i]

        B = self.mobB
        for i in mobB_submobject_index:
            B = B[i]
    
        self.animations = []
        self.mentioned_from_indices = []
        self.mentioned_to_indices = []

        for entry in glyph_map:
            self.process_entry(A, B, entry)
        
        self.check_indices(A, B, auto_fade)
        
        if self.show_indices:
            self.show_indices_animations(A, B, index_label_height, A_index_labels_color, B_index_labels_color)
            return

        if auto_fade:
            self.process_auto_fade(A, B, auto_resolve_delay)
        else:
            self.process_auto_transform(A, B, auto_resolve_delay)

        super().__init__(*self.animations, **kwargs)

    def process_entry(self, A, B, entry):
        assert len(entry) in [2, 3], "Invalid glyph_map entry: " + str(entry)
        if self.printing: print("Glyph map entry: ", entry)

        if len(entry) == 2:
            entry = (*entry, {})
        self.interpret_delay(entry[2])

        if not entry[0] and not entry[1]:
            self.process_empty_entry()
        elif not entry[0] or (isinstance(entry[0], type) and issubclass(entry[0], Animation)):
            self.process_introducer_entry(A, B, entry)
        elif not entry[1] or (isinstance(entry[1], type) and issubclass(entry[1], Animation)):
            self.process_remover_entry(A, B, entry)
        elif entry[0] and entry[1]:
            self.process_double_entry(A, B, entry)
        else:
            raise ValueError("Invalid glyph_map entry: " + str(entry))

    def process_empty_entry(self):
        if self.printing:
            print("Empty glyph_map entry.")
        # self.show_indices = True
        # Disabling because this will happen sometimes in SmartAlgebra

    def process_introducer_entry(self, A, B, entry):
        Introducer = entry[0] if entry[0] else self.default_introducer
        if Introducer == FadeIn and self.shift_fades and "shift" not in entry[2]:
            entry[2]["shift"] = B.get_center() - A.get_center()
        introduced_mobs = [B[i] for i in entry[1]] if self.introduce_individually else [VG(B,entry[1])]
        for mob in introduced_mobs:
            self.animations.append(Introducer(mob, **entry[2]))
        self.mentioned_to_indices += entry[1]

    def process_remover_entry(self, A, B, entry):
        Remover = entry[1] if entry[1] else self.default_remover
        if Remover == FadeOut and self.shift_fades and "shift" not in entry[2]:
            entry[2]["shift"] = B.get_center() - A.get_center()
        removed_mobs = [A[i] for i in entry[0]] if self.remove_individually else [VG(A,entry[0])]
        for mob in removed_mobs:
            self.animations.append(Remover(mob, **entry[2]))
        self.mentioned_from_indices += entry[0]

    def process_double_entry(self, A, B, entry):
        from_mob = VGroup(*[A[i].copy() if i in self.mentioned_from_indices else A[i] for i in entry[0]])
        to_mob = VG(B,entry[1])
        self.animations.append(ReplacementTransform(from_mob, to_mob, **entry[2]))
        self.mentioned_from_indices += entry[0]
        self.mentioned_to_indices += entry[1]

    def interpret_delay(self, dict):
        delay = dict.pop("delay", 0)
        if delay == 0:
            return dict
        run_time = dict.pop("run_time", 1)
        new_run_time = delay + run_time
        rate_func = dict.pop("rate_func", smooth)
        def new_rate_func(t): #https://www.desmos.com/calculator/4hphvny63n
            a = delay / new_run_time
            if t < a:
                return 0
            else:
                return rate_func((t-a)/(1-a))
        dict["rate_func"] = new_rate_func
        dict["run_time"] = new_run_time
        return dict

    def check_indices(self, A, B, auto_fade):
        self.remaining_from_indices = [i for i in range(len(A)) if i not in self.mentioned_from_indices]
        self.remaining_to_indices = [i for i in range(len(B)) if i not in self.mentioned_to_indices]
        if self.printing:
            print("All mentioned from indices: ", self.mentioned_from_indices)
            print("All mentioned to indices: ", self.mentioned_to_indices)
            print(f"All remaining from indices (length {len(self.remaining_from_indices)}): ", self.remaining_from_indices)
            print(f"All remaining to indices (length {len(self.remaining_to_indices)}):", self.remaining_to_indices)
        if not len(self.remaining_from_indices) == len(self.remaining_to_indices) and not auto_fade:
            print("Error: lengths of unmentioned indices do not match.")
            self.show_indices = True

    def show_indices_animations(self, A, B, index_label_height, A_index_labels_color, B_index_labels_color):
        B.next_to(A, DOWN)

        if MANIM_TYPE == 'GL':
            index_labels_A = index_labels(A, label_height=index_label_height).set_color(A_index_labels_color).set_z_index(10).set_stroke(color=BLACK, width=3)
            index_labels_B = index_labels(B, label_height=index_label_height).set_color(B_index_labels_color).set_z_index(10).set_stroke(color=BLACK, width=3)
        elif MANIM_TYPE == 'CE':
            index_labels_A = index_labels(A, label_height=index_label_height, color=A_index_labels_color, background_stroke_width=3).set_z_index(10)
            index_labels_B = index_labels(B, label_height=index_label_height, color=B_index_labels_color, background_stroke_width=3).set_z_index(10)

        print("Showing indices...")
        super().__init__(
            dc_Create(index_labels_A),
            FadeIn(B, shift=DOWN),
            dc_Create(index_labels_B),
            Wait(5),
            lag_ratio=0.5
        )

    def process_auto_fade(self, A, B, auto_resolve_delay):
        for i in self.remaining_from_indices:
            self.process_entry(A, B, ([i], [], {"delay":auto_resolve_delay}))
        for j in self.remaining_to_indices:
            self.process_entry(A, B, ([], [j], {"delay":auto_resolve_delay}))

    def process_auto_transform(self, A, B, auto_resolve_delay):
        for i,j in zip(self.remaining_from_indices, self.remaining_to_indices):
            self.process_entry(A, B, ([i], [j], {"delay":auto_resolve_delay}))

    def begin(self):
        # Save and later restore mobA so that it is unharmed by the transform
        self.mobA.save_state()
        super().begin()

    def clean_up_from_scene(self, scene):
        # Restore mobA so that it emerges unharmed by the transform
        self.mobA.restore()
        super().clean_up_from_scene(scene)

        # Currently in scene.mobjects are a bunch of orphaned submobjects of mobB.
        # These lines make it so that scene.mobjects actually contains mobB as their parent.
        scene.remove(self.mobB)
        scene.add(self.mobB)


# Convenient way to combine multiple MathTex so that the combined object
# has the same submobject structure as a typical single string MathTex
if MANIM_TYPE == 'CE':
    def CombineTex(*mathtexes):
        subobjs = []
        for m in mathtexes:
            subobjs.extend(m.submobjects[0].submobjects)
        return VGroup(VGroup(*subobjs))
elif MANIM_TYPE == 'GL':
    def CombineTex(*texes):
        subobjs = []
        for m in texes:
            subobjs.extend(m.submobjects)
        return VGroup(*subobjs)
