from collections import defaultdict
from collections.abc import Callable, Iterable
from functools import partial
from numbers import Number

import matplotlib.widgets as mwidgets
import numpy as np

try:
    import ipywidgets as widgets
    from IPython.display import display as ipy_display
except ImportError:
    pass
from matplotlib import __version__ as mpl_version
from matplotlib import get_backend
from matplotlib.pyplot import axes, gca, gcf, figure
from numpy.distutils.misc_util import is_sequence
from packaging import version

from .utils import ioff

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
    "callable_else_value_no_cast",
    "kwarg_to_ipywidget",
    "kwarg_to_mpl_widget",
    "extract_num_options",
    "changeify",
    "create_slider_format_dict",
    "gogogo_figure",
    "gogogo_display",
    "create_mpl_controls_fig",
    "eval_xy",
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


def callable_else_value(arg, params, cache=None):
    """
    returns as a numpy array
    """
    if isinstance(arg, Callable):
        if cache:
            if not arg in cache:
                cache[arg] = np.asanyarray(arg(**params))
            return cache[arg]
        else:
            return np.asanyarray(arg(**params))
    return np.asanyarray(arg)


def callable_else_value_no_cast(arg, params, cache=None):
    """
    doesn't cast to numpy. Useful when working with parametric functions that might
    return (x, y) where it's handy to check if the return is a tuple
    """
    if isinstance(arg, Callable):
        if cache:
            if not arg in cache:
                cache[arg] = arg(**params)
            return cache[arg]
        else:
            return arg(**params)
    return arg


def callable_else_value_wrapper(arg, params, cache=None):
    def f(params):
        if isinstance(arg, Callable):
            if cache:
                if not arg in cache:
                    cache[arg] = np.asanyarray(arg(**params))
                return cache[arg]
            else:
                return np.asanyarray(arg(**params))
        return np.asanyarray(arg)

    return f


def eval_xy(x_, y_, params, cache=None):
    """
    for when y requires x as an argument and either, neither or both
    of x and y may be a function.

    returns
    -------
    x, y
        as numpy arrays
    """
    if isinstance(x_, Callable):
        if cache is not None:
            if x_ in cache:
                x = cache[x_]
            else:
                x = x_(**params)
        else:
            x = x_(**params)
    else:
        x = x_
    if isinstance(y_, Callable):
        if cache is not None:
            if y_ in cache:
                y = cache[y_]
            else:
                y = y_(x, **params)
        else:
            y = y_(x, **params)
    else:
        y = y_
    return np.asanyarray(x), np.asanyarray(y)


def kwarg_to_ipywidget(
    key, val, update, slider_format_string, play_button=False, play_button_pos="right"
):
    """
    parameters
    ----------
    slider_returns_index : bool
        If True then the slider will return it's index rather
    returns
    -------
    init_val, control
    control is None is fixed, else it is something that is ready to have display called on it
    to check if its fixed you can do `if control:`
    """

    init_val = 0
    control = None
    if isinstance(val, set):
        if len(val) == 1:
            val = val.pop()
            if isinstance(val, tuple):
                # want the categories to be ordered
                pass
            else:
                # fixed parameter
                return val, None
        else:
            val = list(val)

        # categorical
        if len(val) <= 3:
            selector = widgets.RadioButtons(options=val)
        else:
            selector = widgets.Select(options=val)
        selector.observe(partial(update, values=val), names="index")
        return val[0], selector
    elif isinstance(val, widgets.Widget) or isinstance(val, widgets.fixed):
        if not hasattr(val, "value"):
            raise TypeError(
                "widgets passed as parameters must have the `value` trait."
                "But the widget passed for {key} does not have a `.value` attribute"
            )
        if isinstance(val, widgets.fixed):
            return val, None
        elif (
            isinstance(val, widgets.Select)
            or isinstance(val, widgets.SelectionSlider)
            or isinstance(val, widgets.RadioButtons)
        ):
            # all the selection widget inherit a private _Selection :(
            # it looks unlikely to change but still would be nice to just check
            # if its a subclass
            val.observe(partial(update, values=val.options), names="index")
        else:
            # set values to None and hope for the best
            val.observe(partial(update, values=None), names="value")
            return val.value, val
            # val.observe(partial(update, key=key, label=None), names=["value"])
    else:
        if isinstance(val, tuple) and len(val) in [2, 3]:
            # treat as an argument to linspace
            # idk if it's acceptable to overwrite kwargs like this
            # but I think at this point kwargs is just a dict like any other
            val = np.linspace(*val)
        val = np.atleast_1d(val)
        if val.ndim > 1:
            raise ValueError(f"{key} is {val.ndim}D but can only be 1D or a scalar")
        if len(val) == 1:
            # don't need to create a slider
            return val, None
        else:
            # params[key] = val[0]
            label = widgets.Label(value=slider_format_string.format(val[0]))
            slider = widgets.IntSlider(min=0, max=val.size - 1, readout=False, description=key)
            widgets.dlink(
                (slider, "value"),
                (label, "value"),
                transform=lambda x: slider_format_string.format(val[x]),
            )
            slider.observe(partial(update, values=val), names="value")
            if play_button:
                play = widgets.Play(min=0, max=val.size - 1, step=1)
                widgets.jslink((play, "value"), (slider, "value"))
                if play_button_pos == "left":
                    control = widgets.HBox([play, slider, label])
                else:
                    control = widgets.HBox([slider, label, play])
            else:
                control = widgets.HBox([slider, label])
            return val[0], control


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


def changeify(val, update):
    """
    make matplotlib update functions return a dict with key 'new'.
    Do this for compatibility with ipywidgets
    """
    update({"new": val})


def changeify_radio(val, labels, update):
    """
    matplolib radio buttons don't keep track what index is selected. So this
    figures out what the index is
    made a whole function bc its easier to use with partial then

    There doesn't seem to be a good way to determine which one was clicked if the
    radio button has multiple indentical values but that's wildly niche
    and also probably means they're doing something they shouldn't. So: ¯\_(ツ)_/¯
    """
    update({"new": labels.index(value)})


def create_mpl_controls_fig(kwargs):
    """
    returns
    -------
    fig : matplotlib figure
    slider_height : float
        Height of sliders in figure coordinates
    radio_height : float
        Height of radio buttons in figure coordinates

    note
    ----
    figure out how many inches we shoudl devote to figure of the controls
    this is a bunch of hacky nonsense
    making it involved me holding a ruler up to my monitor
    if you have a better solution I would love to hear about it :)
    - Ian 2020-08-22

    I think maybe the correct approach is to use transforms and actually specify things in inches
    - Ian 2020-09-27
    """
    init_fig = gcf()
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
            and not "ipywidgets" in str(val.__class__)  # do this to avoid depending on ipywidgets
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
    # reset the active figure - necessary to make legends behave as expected
    # maybe this should really be handled via axes? idk
    figure(init_fig.number)
    return fig, slider_height, radio_height, gap_height


def create_mpl_selection_slider(ax, label, values, slider_format_string):
    """
    creates a slider that behaves similarly to the ipywidgets selection slider
    """
    slider = mwidgets.Slider(ax, label, 0, len(values), valinit=0, valstep=1)

    def update_text(val):
        slider.valtext.set_text(slider_format_string.format(values[val]))

    # make sure the initial value also gets formatted
    update_text(0)
    slider.on_changed(update_text)
    return slider


def kwarg_to_mpl_widget(
    fig,
    heights,
    widget_y,
    key,
    val,
    update,
    slider_format_string,
    play_button=False,
    play_button_pos="right",
):
    """
    heights : tuple
        with slider_height, radio_height, gap_height
    returns
    -------
    init_val
    widget
    cb
        the callback id
    new_y
        The widget_y to use for the next pass
    """
    slider_height, radio_height, gap_height = heights

    # widget_y = 0.05
    slider_ax = []
    sliders = []
    radio_ax = []
    radio_buttons = []
    cbs = []
    if isinstance(val, set):
        if len(val) == 1:
            val = val.pop()
            if isinstance(val, tuple):
                pass
            else:
                return val, None, None, widget_y
        else:
            val = list(val)

        n = len(val)
        longest_len = max(list(map(lambda x: len(list(x)), map(str, val))))
        # should probably use something based on fontsize rather that .015
        width = max(0.15, 0.015 * longest_len)
        radio_ax = fig.add_axes([0.2, 0.9 - widget_y - radio_height * n, width, radio_height * n])
        widget_y += radio_height * n + gap_height
        radio_buttons = mwidgets.RadioButtons(radio_ax, val, active=0)
        cb = radio_buttons.on_clicked(partial(changeify_radio, labels=val, update=update))
        return val[0], radio_buttons, cb, widget_y
    elif isinstance(val, mwidgets.RadioButtons):
        # gotta set it to the zeroth index bc theres no reasonable way to determine the current value
        # the only way the current value is stored is through the color of the circles.
        # so could query that an extract but oh boy do I ever not want to
        val.set_active(0)
        cb = val.on_clicked(partial(changeify_radio, labels=val.labels, update=update))
        return val.labels[0], val, cb, widget_y
    elif isinstance(val, mwidgets.Slider):
        # potential future improvement:
        # check if valstep has been set and then try to infer the values
        # but not now, I'm trying to avoid premature optimization lest this
        # drag on forever
        # cb = val.on_changed(partial(changeify, update=update))
        return val.val, val, cb, widget_y
    else:
        slider = None
        update_fxn = None
        if isinstance(val, tuple):
            if len(val) == 2:
                min_ = float(val[0])
                max_ = float(val[1])
                slider_ax = fig.add_axes([0.2, 0.9 - widget_y - gap_height, 0.65, slider_height])
                slider = mwidgets.Slider(slider_ax, key, min_, max_)

                def update_text(val):
                    slider.valtext.set_text(slider_format_string.format(val))

                # make sure the initial value also gets formatted
                update_text(slider.valinit)
                slider.on_changed(update_text)
                cb = slider.on_changed(partial(changeify, update=partial(update, values=None)))
                widget_y += slider_height + gap_height
                return min_, slider, cb, widget_y
            elif len(val) == 3:
                # should warn that that doesn't make sense with matplotlib sliders
                min_ = val[0]
                max_ = val[1]
                val = np.linspace(*val)
        val = np.atleast_1d(val)
        if val.ndim > 1:
            raise ValueError(f"{key} is {val.ndim}D but can only be 1D or a scalar")
        if len(val) == 1:
            # don't need to create a slider
            return val[0], None, None, widget_y
        else:
            slider_ax = fig.add_axes([0.2, 0.9 - widget_y - gap_height, 0.65, slider_height])
            slider = create_mpl_selection_slider(slider_ax, key, val, slider_format_string)
            slider.on_changed(partial(changeify, update=partial(update, values=val)))
            widget_y += slider_height + gap_height
            return val[0], slider, None, widget_y


def create_slider_format_dict(slider_format_string):
    if isinstance(slider_format_string, defaultdict):
        return slider_format_string
    elif isinstance(slider_format_string, dict) or slider_format_string is None:
        slider_format_strings = defaultdict(lambda: "{:.2f}")
        if slider_format_string is not None:
            for key, val in slider_format_string.items():
                slider_format_strings[key] = val
    elif isinstance(slider_format_string, str):

        def f():
            return slider_format_string

        slider_format_strings = defaultdict(f)
    else:
        raise ValueError(
            f"slider_format_string must be a dict or a string but it is a {type(slider_format_string)}"
        )
    return slider_format_strings


def gogogo_figure(ipympl, ax=None):
    """
    gogogo the greatest function name of all
    """
    if ax is None:
        if ipympl:
            with ioff:
                ax = gca()
                fig = ax.get_figure()
        else:
            ax = gca()
            fig = ax.get_figure()
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
