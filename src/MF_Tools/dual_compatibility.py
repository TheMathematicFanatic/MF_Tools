try:
    from manimlib import *
    from manimlib import (
        ShowCreation as dc_Create,
        Tex as dc_Tex,
        TexText as dc_TexText,
    )
    MANIM_TYPE = 'GL'

except ImportError:
    from manim import *
    from manim import (
        Create as dc_Create,
        MathTex as dc_Tex,
        Tex as dc_TexText,
    )
    MANIM_TYPE = 'CE'


if MANIM_TYPE == 'GL':
    class Wait(FadeOut):
        def __init__(self, wait_time, **kwargs):
            self.mobject = VMobject()
            super().__init__(self.mobject, run_time=wait_time, **kwargs)

    class VDict(VMobject):
        def __init__(
            self,
            mapping_or_iterable = {},
            show_keys: bool = False,
            **kwargs,
        ) -> None:
            super().__init__(**kwargs)
            self.show_keys = show_keys
            self.submob_dict = {}
            self.add(mapping_or_iterable)

        def add(self, mapping_or_iterable):
            for key, value in dict(mapping_or_iterable).items():
                self.add_key_value_pair(key, value)
            return self

        def remove(self, key):
            if key not in self.submob_dict:
                raise KeyError(f"The given key '{key!s}' is not present in the VDict")
            super().remove(self.submob_dict[key])
            del self.submob_dict[key]
            return self

        def __getitem__(self, key):
            submob = self.submob_dict[key]
            return submob

        def __setitem__(self, key, value):
            if key in self.submob_dict:
                self.remove(key)
            self.add([(key, value)])

        def __delitem__(self, key):
            del self.submob_dict[key]

        def __contains__(self, key):
            return key in self.submob_dict

        def get_all_submobjects(self):
            submobjects = self.submob_dict.values()
            return submobjects

        def add_key_value_pair(self, key, value):
            mob = value
            if self.show_keys:
                key_text = TexText(str(key)).next_to(value, LEFT)
                mob.add(key_text)
            self.submob_dict[key] = mob
            super().add(value)


if MANIM_TYPE == 'CE':
    pass

