from collections import defaultdict
from collections.abc import Callable, Iterable
from functools import partial
from numbers import Number

import ipywidgets as widgets
import matplotlib.widgets as mwidgets
import numpy as np
from IPython.display import display as ipy_display
from matplotlib import __version__ as mpl_version
from matplotlib import get_backend
from matplotlib.pyplot import axes
from numpy.distutils.misc_util import is_sequence
from packaging import version

from .utils import figure, ioff

__all__ = [
    "decompose_bbox",
    "update_datalim_from_xy",
    "update_datalim_from_bbox",
    "is_jagged",
    "broadcast_to",
    "prep_broadcast",
    "broadcast_arrays",
    "broadcast_many",
    "notebook_backend",
    "callable_else_value",
    "kwargs_to_ipywidgets",
    "extract_num_options",
    "changeify",
    "kwargs_to_mpl_widgets",
    "create_slider_format_dict",
    "gogogo_figure",
    "gogogo_display",
]


def decompose_bbox(bbox):
    return bbox.x0, bbox.y0, bbox.x1, bbox.y1


def _update_limits(ax, x0, y0, x1, y1, x0_, y0_, x1_, y1_, stretch_x, stretch_y):
    if stretch_x:
        x0 = np.min([x0, x0_])
        x1 = np.max([x1, x1_])
    else:
        x0 = x0_
        x1 = x1_

    if stretch_y:
        y0 = np.min([y0, y0_])
        y1 = np.max([y1, y1_])
    else:
        y0 = y0_
        y1 = y1_
    # now relim and always take the maximum extent
    ax.relim()
    ax.dataLim.update_from_data_xy(np.asarray([[x0, y0], [x1, y1]]), ignore=False)


def update_datalim_from_bbox(ax, bbox, stretch_x=True, stretch_y=True):
    _update_limits(ax, *decompose_bbox(ax.dataLim), *decompose_bbox(bbox), stretch_x, stretch_y)


def update_datalim_from_xy(ax, x, y, stretch_x=True, stretch_y=True):
    """
    current : ax.dataLim
    x : array
        the new x datavalues to include
    y : array
        the new y datavalues to include
    """
    # this part bc scatter not affect by relim
    # so need this to keep stretchign working for scatter
    x0_ = np.min(x)
    x1_ = np.max(x)
    y0_ = np.min(y)
    y1_ = np.max(y)
    _update_limits(ax, *decompose_bbox(ax.dataLim), x0_, y0_, x1_, y1_, stretch_x, stretch_y)


def is_jagged(seq):
    """
    checks for jaggedness up to two dimensions
    don't need more because more doesn't make any sense for this library
    need this bc numpy is unhappy about being passed jagged arrays now :(
    """
    lens = []
    if is_sequence(seq):
        for y in seq:
            if isinstance(y, Number) or isinstance(y, Callable):
                lens.append(0)
                continue
            try:
                lens.append(len(y))
            except TypeError:
                return True
        if not all(lens[0] == l for l in lens):
            return True
    return False


def prep_broadcast(arr):
    if arr is None:
        return np.atleast_1d(None)
    if is_jagged(arr):
        arr = np.asarray(arr, dtype=np.object)
    elif isinstance(arr, Number) or isinstance(arr, Callable):
        arr = np.atleast_1d(arr)
    else:
        arr = np.atleast_1d(arr)
        if np.issubdtype(arr.dtype, np.number) and arr.ndim == 1:
            arr = arr[None, :]
    return arr


def broadcast_to(arr, to_shape, names):
    """
    happily this doesn't increase memory footprint e.g:
    import sys
    xs = np.arange(5)
    print(sys.getsizeof(xs.nbytes))
    print(sys.getsizeof(np.broadcast_to(xs, (19000, xs.shape[0]))))

    gives 28 and 112. Note 112/28 != 19000
    """
    if arr.shape[0] == to_shape[0]:
        return arr

    if arr.ndim > 1:
        if arr.shape[0] == 1:
            return np.broadcast_to(arr, (to_shape[0], *arr.shape[1:]))
        else:
            raise ValueError(f"can't broadcast {names[0]} {arr.shape} onto {names[1]} {to_shape}")
    elif arr.shape[0] == 1:
        return np.broadcast_to(arr, (to_shape[0],))
    else:
        raise ValueError(f"can't broadcast {names[0]} {arr.shape} onto {names[1]} {to_shape}")


def broadcast_arrays(*args):
    """
    This is a modifed version the numpy `broadcast_arrays` function
    that uses a verion of _broadcast_to that only considers the first axis
    """

    shapes = [array.shape[0] for (array, name) in args]
    idx = np.argmax(shapes)
    if all([shapes[0] == s for s in shapes]):
        # case where nothing needs to be broadcasted.
        return [array for (array, name) in args]
    return [broadcast_to(array, args[idx][0].shape, [name, args[idx][1]]) for (array, name) in args]


def broadcast_many(*args):
    """
    helper to call prep_broadcast followed by broadcast arrays
    keep as a separate function to keep the idea of broadcast_arrays the same
    """
    return broadcast_arrays(*[(prep_broadcast(arg[0]), arg[1]) for arg in args])


def notebook_backend():
    """
    returns True if the backend is ipympl or nbagg, otherwise False
    """
    backend = get_backend().lower()
    if "ipympl" in backend:
        return True
    elif backend == "nbAgg".lower():
        return True
    return False


def callable_else_value(arg, params):
    if isinstance(arg, Callable):
        return arg(**params)
    return arg


def kwargs_to_ipywidgets(
    kwargs, params, update, slider_format_strings, play_buttons=False, play_button_pos="right"
):
    """
    this will break if you pass a matplotlib slider. I suppose it could support mixed types of sliders
    but that doesn't really seem worthwhile?

    parameters
    ----------
    play_button: boolean or dict
        if boolean it will be applied to all sliders. If a dict it should have the same keys
        as kwargs and the values should be True or False. Or an iterable of strings of parameter names
    """
    labels = []
    sliders = []
    controls = []
    players = []
    if isinstance(play_buttons, bool):
        has_play_button = defaultdict(lambda: play_buttons)
    elif isinstance(play_buttons, defaultdict):
        has_play_button = play_buttons
    elif isinstance(play_buttons, dict):
        has_play_button = defaultdict(lambda: False, play_buttons)
    elif isinstance(play_buttons, Iterable) and all([isinstance(p, str) for p in play_buttons]):
        has_play_button = defaultdict(
            lambda: False, dict(zip(play_buttons, [True] * len(play_buttons)))
        )
    else:
        has_play_button = play_buttons

    for key, val in kwargs.items():
        if isinstance(val, set):
            if len(val) == 1:
                val = val.pop()
                if isinstance(val, tuple):
                    # want the categories to be ordered
                    pass
                else:
                    # fixed parameter
                    params[key] = val
            else:
                val = list(val)

            # categorical
            if len(val) <= 3:
                selector = widgets.RadioButtons(options=val)
            else:
                selector = widgets.Select(options=val)
            params[key] = val[0]
            controls.append(selector)
            selector.observe(partial(update, key=key, label=None), names=["value"])
        elif isinstance(val, widgets.Widget) or isinstance(val, widgets.fixed):
            if not hasattr(val, "value"):
                raise TypeError(
                    "widgets passed as parameters must have the `value` trait."
                    "But the widget passed for {key} does not have a `.value` attribute"
                )
            if isinstance(val, widgets.fixed):
                params[key] = val.value
            else:
                params[key] = val.value
                controls.append(val)
                val.observe(partial(update, key=key, label=None), names=["value"])
        else:
            if isinstance(val, tuple) and len(val) in [2, 3]:
                # treat as an argument to linspace
                # idk if it's acceptable to overwrite kwargs like this
                # but I think at this point kwargs is just a dict like any other
                val = np.linspace(*val)
                kwargs[key] = val
            val = np.atleast_1d(val)
            if val.ndim > 1:
                raise ValueError(f"{key} is {val.ndim}D but can only be 1D or a scalar")
            if len(val) == 1:
                # don't need to create a slider
                params[key] = val
            else:
                params[key] = val[0]
                labels.append(widgets.Label(value=slider_format_strings[key].format(val[0])))
                sliders.append(
                    widgets.IntSlider(min=0, max=val.size - 1, readout=False, description=key)
                )
                if has_play_button[key]:
                    players.append(widgets.Play(min=0, max=val.size - 1, step=1))
                    widgets.jslink((players[-1], "value"), (sliders[-1], "value"))
                    if play_button_pos == "left":
                        controls.append(widgets.HBox([players[-1], sliders[-1], labels[-1]]))
                    else:
                        controls.append(widgets.HBox([sliders[-1], labels[-1], players[-1]]))
                else:
                    controls.append(widgets.HBox([sliders[-1], labels[-1]]))
                sliders[-1].observe(partial(update, key=key, label=labels[-1]), names=["value"])
    return sliders, labels, controls, players


def extract_num_options(val):
    """
    convert a categorical to a number of options
    """
    if len(val) == 1:
        for v in val:
            if isinstance(v, tuple):
                # this looks nightmarish...
                # but i think it should always work
                # should also check if the tuple has length one here.
                # that will only be an issue if a trailing comma was used to make the tuple ('beep',)
                # but not ('beep') - the latter is not actually a tuple
                return len(v)
            else:
                return 0
    else:
        return len(val)


def changeify(val, key, update):
    """
    make matplotlib update functions return a dict with key 'new'.
    Do this for compatibility with ipywidgets
    """
    update({"new": val}, key, None)


# this is a bunch of hacky nonsense
# making it involved me holding a ruler up to my monitor
# if you have a better solution I would love to hear about it :)
# - Ian 2020-08-22
def kwargs_to_mpl_widgets(kwargs, params, update, slider_format_strings, valstep=None):
    n_opts = 0
    n_radio = 0
    n_sliders = 0
    for key, val in kwargs.items():
        if isinstance(val, set):
            new_opts = extract_num_options(val)
            if new_opts > 0:
                n_radio += 1
                n_opts += new_opts
        elif (
            not isinstance(val, mwidgets.AxesWidget)
            and not isinstance(val, widgets.fixed)
            and isinstance(val, Iterable)
            and len(val) > 1
        ):
            n_sliders += 1

    # These are roughly the sizes used in the matplotlib widget tutorial
    # https://matplotlib.org/3.2.2/gallery/widgets/slider_demo.html#sphx-glr-gallery-widgets-slider-demo-py
    slider_in = 0.15
    radio_in = 0.6 / 3
    widget_gap_in = 0.1

    widget_inches = (
        n_sliders * slider_in + n_opts * radio_in + widget_gap_in * (n_sliders + n_radio + 1) + 0.5
    )  # half an inch for margin
    fig = None
    if not all(map(lambda x: isinstance(x, mwidgets.AxesWidget), kwargs.values())):
        # if the only kwargs are existing matplotlib widgets don't make a new figure
        with ioff:
            fig = figure()
        size = fig.get_size_inches()
        fig_h = widget_inches
        fig.set_size_inches(size[0], widget_inches)
        slider_height = slider_in / fig_h
        radio_height = radio_in / fig_h
        # radio
        gap_height = widget_gap_in / fig_h
    widget_y = 0.05
    slider_ax = []
    sliders = []
    radio_ax = []
    radio_buttons = []
    cbs = []
    for key, val in kwargs.items():
        if isinstance(val, set):
            if len(val) == 1:
                val = val.pop()
                if isinstance(val, tuple):
                    pass
                else:
                    params[key] = val
                    continue
            else:
                val = list(val)

            n = len(val)
            longest_len = max(list(map(lambda x: len(list(x)), map(str, val))))
            # should probably use something based on fontsize rather that .015
            width = max(0.15, 0.015 * longest_len)
            radio_ax.append(axes([0.2, 0.9 - widget_y - radio_height * n, width, radio_height * n]))
            widget_y += radio_height * n + gap_height
            radio_buttons.append(mwidgets.RadioButtons(radio_ax[-1], val, active=0))
            cbs.append(radio_buttons[-1].on_clicked(partial(changeify, key=key, update=update)))
            params[key] = val[0]
        elif isinstance(val, mwidgets.RadioButtons):
            val.on_clicked(partial(changeify, key=key, update=update))
            params[key] = val.val
        elif isinstance(val, mwidgets.Slider):
            val.on_changed(partial(changeify, key=key, update=update))
            params[key] = val.val
        else:
            if isinstance(val, tuple):
                if len(val) == 2:
                    min_ = val[0]
                    max_ = val[1]
                elif len(val) == 3:
                    # should warn that that doesn't make sense with matplotlib sliders
                    min_ = val[0]
                    max_ = val[1]
            else:
                val = np.atleast_1d(val)
                if val.ndim > 1:
                    raise ValueError(f"{key} is {val.ndim}D but can only be 1D or a scalar")
                if len(val) == 1:
                    # don't need to create a slider
                    params[key] = val[0]
                    continue
                else:
                    # list or numpy array
                    # should warn here as well
                    min_ = np.min(val)
                    max_ = np.max(val)

            slider_ax.append(axes([0.2, 0.9 - widget_y - gap_height, 0.65, slider_height]))
            sliders.append(
                mwidgets.Slider(
                    slider_ax[-1],
                    key,
                    min_,
                    max_,
                    valinit=min_,
                    valfmt=slider_format_strings[key],
                    valstep=valstep,
                )
            )
            cbs.append(sliders[-1].on_changed(partial(changeify, key=key, update=update)))
            widget_y += slider_height + gap_height
            params[key] = min_
    controls = [fig, radio_ax, radio_buttons, slider_ax, sliders]
    return controls


def create_slider_format_dict(slider_format_string, use_ipywidgets):
    # mpl sliders for verison 3.3 and onwards support None as an argument for valfmt
    mpl_gr_33 = version.parse(mpl_version) >= version.parse("3.3")
    if isinstance(slider_format_string, str):
        slider_format_strings = defaultdict(lambda: slider_format_string)
    elif isinstance(slider_format_string, dict) or slider_format_string is None:
        if use_ipywidgets:
            slider_format_strings = defaultdict(lambda: "{:.2f}")
        elif mpl_gr_33:
            slider_format_strings = defaultdict(lambda: None)
        else:
            slider_format_strings = defaultdict(lambda: "%1.2f")

        if slider_format_string is not None:
            for key, val in slider_format_string.items():
                slider_format_strings[key] = val
    else:
        raise ValueError(
            f"slider_format_string must be a dict or a string but it is a {type(slider_format_string)}"
        )
    return slider_format_strings


def gogogo_figure(ipympl, figsize, ax=None):
    """
    gogogo the greatest function name of all
    """
    if ax is None:
        if ipympl:
            with ioff:
                fig = figure(figsize=figsize)
                ax = fig.gca()
        else:
            fig = figure(figsize=figsize)
            ax = fig.gca()
        return fig, ax
    else:
        return ax.get_figure(), ax


def gogogo_display(ipympl, use_ipywidgets, display, controls, fig):
    if use_ipywidgets:
        controls = widgets.VBox(controls)
        if display:
            if ipympl:
                ipy_display(widgets.VBox([controls, fig.canvas]))
            else:
                # for the case of using %matplotlib qt
                # but also want ipywidgets sliders
                # ie with force_ipywidgets = True
                ipy_display(controls)
                fig.show()
    else:
        if display:
            fig.show()
            controls[0].show()
    return controls
