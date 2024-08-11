from manim import *

class TransformByGlyphMap(AnimationGroup):
    def __init__(
        self,
        mobA,
        mobB,
        *glyph_map,
        from_copy=False,
        show_indices=False,
        mobA_submobject_index=[0],
        mobB_submobject_index=[0],
        default_introducer=FadeIn,
        default_remover=FadeOut,
        shift_fades=True,
        printing=False,
        A_index_labels_color=PINK,
        B_index_labels_color=GREEN,
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

        for entry in glyph_map:
            if printing:
                print("Glyph map entry: ", entry)
            assert len(entry) in [2, 3], "Invalid glyph_map entry: " + str(entry)
            if len(entry) == 2:
                entry_kwargs = {}
            else:
                entry_kwargs = entry[2]
            if len(entry[0]) == 0 or issubclass(entry[0], Animation):
                Introducer = entry[0] if entry[0] else default_introducer
                animations.append(Introducer(
                    VG(B,entry[1]),
                    shift = B.get_center() - A.get_center() if shift_fades else ORIGIN,
                    **entry_kwargs
                    ))
                mentioned_to_indices += entry[1]
            elif len(entry[1] == 0) or issubclass(entry[1], Animation):
                Remover = entry[1] if entry[1] else default_remover
                animations.append(Remover(
                    VG(A,entry[0]),
                    shift = B.get_center() - A.get_center() if shift_fades else ORIGIN,
                    **entry_kwargs
                    ))
                mentioned_from_indices += entry[0]
            elif len(entry[0]) > 0 and len(entry[1]) > 0:
                animations.append(ReplacementTransform(
                    VG(A,entry[0]),
                    VG(B,entry[1]),
                    **entry_kwargs
                    ))
                mentioned_from_indices += entry[0]
                mentioned_to_indices += entry[1]
            elif len(entry[0]) == 0 and len(entry[1]) == 0:
                print("Empty glyph_map entry: " + str(entry))
                show_indices = True
            else:
                raise ValueError("Invalid glyph_map entry: " + str(entry))
        
        remaining_from_indices = [i for i in range(len(A)) if i not in mentioned_from_indices]
        remaining_to_indices = [i for i in range(len(B)) if i not in mentioned_to_indices]
        
        if printing:
            print("All mentioned from indices: ", mentioned_from_indices)
            print("All mentioned to indices: ", mentioned_to_indices)
            print("Remaining from indices: ", remaining_from_indices)
            print("Remaining to indices: ", remaining_to_indices)
        
        if not len(remaining_from_indices) == len(remaining_to_indices):
            print("Error: lengths of unmentioned indices do not match.")
            print(f"Remaining from indices (length {len(remaining_from_indices)}): ", remaining_from_indices)
            print(f"Remaining to indices (length {len(remaining_to_indices)}): ", remaining_to_indices)
            show_indices = True
        
        if show_indices:
            print("Showing indices...")
            super().__init__(
                Create(index_labels(A), color=A_index_labels_color),
                FadeIn(B.next_to(A, DOWN)),
                Create(index_labels(B), color=B_index_labels_color),
                Wait(5),
                lag_ratio=0.5
            )
        
        for i,j in zip(remaining_from_indices, remaining_to_indices):
            animations.append(ReplacementTransform(A[i], B[j]))
        super().__init__(*animations, **kwargs)

        