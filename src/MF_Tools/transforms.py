from manim import *

class TransformByGlyphMap(AnimationGroup):
    def __init__(
        self,
        mobA,
        mobB,
        *glyph_map,
        from_copy=False,
        mobA_submobject_index=[0],
        mobB_submobject_index=[0],
        default_introducer=FadeIn,
        default_remover=FadeOut,
        introduce_individually=False,
        remove_individually=False,
        shift_fades=True,
        show_indices=False,
        A_index_labels_color=RED_D,
        B_index_labels_color=BLUE_D,
        index_label_height=0.18,
        printing=False,
        **kwargs
        ):

        A = mobA.copy() if from_copy else mobA
        for i in mobA_submobject_index:
            A = A[i]
        B = mobB
        for i in mobB_submobject_index:
            B = B[i]
        animations = []
        mentioned_from_indices = []
        mentioned_to_indices = []

        def VG(mob, index_list):
            return VGroup(*[mob[i] for i in index_list])
        
        if len(glyph_map)==0: show_indices=True

        for entry in glyph_map:
            if printing:
                print("Glyph map entry: ", entry)
            assert len(entry) in [2, 3], "Invalid glyph_map entry: " + str(entry)
            entry_kwargs = {} if len(entry) == 2 else entry[2]

            if not entry[0] and not entry[1]:
                print("Empty glyph_map entry: " + str(entry))
                show_indices = True
            elif (not entry[0]) or (isinstance(entry[0], type) and issubclass(entry[0], Animation)):
                Introducer = entry[0] if entry[0] else default_introducer
                introduced_mobs = [B[i] for i in entry[1]] if introduce_individually else [VG(B,entry[1])]
                for mob in introduced_mobs:
                    animations.append(Introducer(
                        mob,
                        shift = B.get_center() - A.get_center() if shift_fades else ORIGIN,
                        **{**kwargs, **entry_kwargs}
                        ))
                    if "delay" in entry_kwargs:
                        animations[-1] = Succession(Wait(entry_kwargs["delay"]), animations[-1])
                mentioned_to_indices += entry[1]
            elif not entry[1] or (isinstance(entry[1], type) and issubclass(entry[1], Animation)):
                Remover = entry[1] if entry[1] else default_remover
                removed_mobs = [A[i] for i in entry[0]] if remove_individually else [VG(A,entry[0])]
                for mob in removed_mobs:
                    animations.append(Remover(
                        mob,
                        shift = B.get_center() - A.get_center() if shift_fades else ORIGIN,
                        **{**kwargs, **entry_kwargs}
                        ))
                    if "delay" in entry_kwargs:
                        animations[-1] = Succession(Wait(entry_kwargs["delay"]), animations[-1])
                mentioned_from_indices += entry[0]
            elif len(entry[0]) > 0 and len(entry[1]) > 0:
                animations.append(ReplacementTransform(
                    VGroup(*[A[i].copy() if i in mentioned_from_indices else A[i] for i in entry[0]]),
                    VG(B,entry[1]),
                    **{**kwargs, **entry_kwargs}
                    ))
                if "delay" in entry_kwargs:
                    animations[-1] = Succession(Wait(entry_kwargs["delay"]), animations[-1])
                mentioned_from_indices += entry[0]
                mentioned_to_indices += entry[1]
            else:
                raise ValueError("Invalid glyph_map entry: " + str(entry))
        
        if printing:
            print("All mentioned from indices: ", mentioned_from_indices)
            print("All mentioned to indices: ", mentioned_to_indices)
        
        remaining_from_indices = [i for i in range(len(A)) if i not in mentioned_from_indices]
        remaining_to_indices = [i for i in range(len(B)) if i not in mentioned_to_indices]
        
        if not len(remaining_from_indices) == len(remaining_to_indices):
            print("Error: lengths of unmentioned indices do not match.")
            print(f"Remaining from indices (length {len(remaining_from_indices)}): ", remaining_from_indices)
            print(f"Remaining to indices (length {len(remaining_to_indices)}): ", remaining_to_indices)
            show_indices = True
        elif printing:
            print("Remaining from indices: ", remaining_from_indices)
            print("Remaining to indices: ", remaining_to_indices)
        
        if show_indices:
            print("Showing indices...")
            super().__init__(
                Create(index_labels(A, label_height=index_label_height, color=A_index_labels_color, background_stroke_width=3)),
                FadeIn(B.next_to(A, DOWN), shift=DOWN),
                Create(index_labels(B, label_height=index_label_height, color=B_index_labels_color, background_stroke_width=3)),
                Wait(5),
                lag_ratio=0.5
            )
        else:
            for i,j in zip(remaining_from_indices, remaining_to_indices):
                animations.append(ReplacementTransform(A[i], B[j], **kwargs))
            super().__init__(*animations, **kwargs)


def ir(a,b): #inclusive_range
    return list(range(a,b+1))