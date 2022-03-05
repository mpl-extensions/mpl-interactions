__all__ = [
    "set_param_values",
]


def set_param_values(controls, params):
    """
    A bit sketch because it set the index for ipywidgets
    and direct value for mpl sliders. big TODO there.
    """
    for p, v in params.items():
        slider = controls.controls[p]
        if "Box" in str(slider.__class__):
            for obj in slider.children:
                if "Slider" in str(obj.__class__):
                    obj.value = v
        else:
            slider.set_val(v)
