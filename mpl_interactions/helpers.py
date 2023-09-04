from collections import defaultdict
from collections.abc import Callable, Iterable
from functools import partial

import matplotlib.widgets as mwidgets
import numpy as np

try:
    import ipywidgets as widgets
except ImportError:
    pass
from matplotlib import get_backend
from matplotlib.pyplot import figure, gca, gcf, ioff
from matplotlib.pyplot import sca as mpl_sca

from .widgets import RangeSlider

__all__ = [
    "sca",
    "decompose_bbox",
    "update_datalim_from_xy",
    "update_datalim_from_bbox",
    "notebook_backend",
    "callable_else_value",
    "callable_else_value_no_cast",
    "kwarg_to_ipywidget",
    "kwarg_to_mpl_widget",
    "extract_num_options",
    "changeify",
    "create_slider_format_dict",
    "gogogo_figure",
    "create_mpl_controls_fig",
    "eval_xy",
    "choose_fmt_str",
]


def sca(ax):
    """Sca that won't fail if figure not managed by pyplot."""
    try:
        mpl_sca(ax)
    except ValueError as e:
        if "not managed by pyplot" not in str(e):
            raise e


def decompose_bbox(bbox):
    """Break bbox into it's 4 components."""
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
    """Update an axis datalim from a bbox."""
    _update_limits(ax, *decompose_bbox(ax.dataLim), *decompose_bbox(bbox), stretch_x, stretch_y)


def update_datalim_from_xy(ax, x, y, stretch_x=True, stretch_y=True):
    """Update an axis datalim while maybe stretching it.

    Parameters
    ----------
    ax : matplotlib axis
        The axis to update.
    x : array
        the new x datavalues to include
    y : array
        the new y datavalues to include.
    stretch_x, stretch_y : bool
        Whether to stretch
    """
    # this part bc scatter not affect by relim
    # so need this to keep stretchign working for scatter
    x0_ = np.min(x)
    x1_ = np.max(x)
    y0_ = np.min(y)
    y1_ = np.max(y)
    _update_limits(ax, *decompose_bbox(ax.dataLim), x0_, y0_, x1_, y1_, stretch_x, stretch_y)


def notebook_backend():
    """Return True if the backend is ipympl or nbagg, otherwise False."""
    backend = get_backend().lower()
    if "ipympl" in backend:
        return True
    elif backend == "nbAgg".lower():
        return True
    return False


def callable_else_value(arg, params, cache=None):
    """
    Convert callables to arrays passing existing values through as numpy arrays.

    Always returns a numpy array - use callable_else_value_no_cast
    if it's important that the value not be a numpy array.
    """
    if isinstance(arg, Callable):
        if cache:
            if arg not in cache:
                cache[arg] = np.asanyarray(arg(**params))
            return cache[arg]
        else:
            return np.asanyarray(arg(**params))
    return np.asanyarray(arg)


def callable_else_value_no_cast(arg, params, cache=None):
    """Convert callables to arrays passing existing values through."""
    if isinstance(arg, Callable):
        if cache:
            if arg not in cache:
                cache[arg] = arg(**params)
            return cache[arg]
        else:
            return arg(**params)
    return arg


def eval_xy(x_, y_, params, cache=None):
    """Evaluate x and y as needed, passing them the approriate arguments.

    for when y requires x as an argument and either, neither or both
    of x and y may be a function. This will automatically do the param exclusion
    for 'x' and 'y'.

    Returns
    -------
    x, y
        as numpy arrays
    """
    if "x" in params:
        # passed as a scalar with a slider
        x = params["x"]
    elif isinstance(x_, Callable):
        if cache is not None:
            if x_ in cache:
                x = cache[x_]
            else:
                x = x_(**params)
                cache[x_] = x
        else:
            x = x_(**params)
    else:
        x = x_
    if "y" in params:
        # passed a scalar with a slider
        y = params["y"]
    elif isinstance(y_, Callable):
        if cache is not None:
            if y_ in cache:
                y = cache[y_]
            else:
                y = y_(x, **params)
                cache[y_] = y
        else:
            y = y_(x, **params)
    else:
        y = y_
    return np.asanyarray(x), np.asanyarray(y)


def kwarg_to_ipywidget(key, val, update, slider_format_string, play_button=None):
    """Convert a kwarg to an ipywidget.

    Parameters
    ----------
    key : str
        The name of the kwarg.
    val : str or number or tuple, or set or array-like
        The value to be interpreted and possibly transformed into an ipywidget
    update : callable
        The function to be called when the value of the generated widget changes.
        Must accept a dictionary *change* and an array-like *values*
    slider_format_string : str
        The format string to use for slider labels
    play_button : bool or None or str, default: None
        If true and the output widget is a slider then added a play button widget
        on the left. Also accepts 'left' or 'right' to specify the play button position.

    Returns
    -------
    init_val
        The initial value of the widget.
    control
        The generated widget. This may be the raw widget or a higher level container
        widget (e.g. HBox) depending on what widget was generated. If a fixed value is
        returned then control will be *None*
    param_hash :
        A hash of the possible values, to be used to check duplicates in the future.
    """
    control = None
    if isinstance(val, set):
        if len(val) == 1:
            val = val.pop()
            if isinstance(val, tuple):
                # want the categories to be ordered
                pass
            else:
                # fixed parameter
                return val, None, hash(repr(val))
        else:
            val = list(val)

        # categorical
        if len(val) <= 3:
            selector = widgets.RadioButtons(options=val)
        else:
            selector = widgets.Select(options=val)
        selector.observe(partial(update, values=val), names="index")
        return val[0], selector, hash(repr(val))
    elif isinstance(val, widgets.Widget) or isinstance(val, widgets.fixed):
        if not hasattr(val, "value"):
            raise TypeError(
                "widgets passed as parameters must have the `value` trait."
                "But the widget passed for {key} does not have a `.value` attribute"
            )
        if isinstance(val, widgets.fixed):
            return val, None, hash(repr(val))
        elif (
            isinstance(val, widgets.Select)
            or isinstance(val, widgets.SelectionSlider)
            or isinstance(val, widgets.RadioButtons)
        ):
            # all the selection widget inherit a private _Selection :(
            # it looks unlikely to change but still would be nice to just check
            # if its a subclass
            val.observe(partial(update, values=val.options), names="index")
            return val.value, val, hash(repr(val.options))
        else:
            # set values to None and hope for the best
            val.observe(partial(update, values=None), names="value")
            return val.value, val, hash(repr(val))
            # val.observe(partial(update, key=key, label=None), names=["value"])
    else:
        if isinstance(val, tuple) and val[0] in ["r", "range", "rang", "rage"]:
            # also check for some reasonably easy mispellings
            if isinstance(val[1], (np.ndarray, list)):
                vals = val[1]
            else:
                vals = np.linspace(*val[1:])
            label = widgets.Label(value=str(vals[0]))
            slider = widgets.IntRangeSlider(
                value=(0, vals.size - 1), min=0, max=vals.size - 1, readout=False, description=key
            )
            widgets.dlink(
                (slider, "value"),
                (label, "value"),
                transform=lambda x: slider_format_string.format(vals[x[0]])
                + " - "
                + slider_format_string.format(vals[x[1]]),
            )
            slider.observe(partial(update, values=vals), names="value")
            controls = widgets.HBox([slider, label])
            return vals[[0, -1]], controls, hash("r" + repr(vals))

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
            return val[0], None, hash(repr(val))
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
            if play_button is not None and play_button is not False:
                play = widgets.Play(min=0, max=val.size - 1, step=1)
                widgets.jslink((play, "value"), (slider, "value"))
                if isinstance(play_button, str) and play_button.lower() == "right":
                    control = widgets.HBox([slider, label, play])
                else:
                    control = widgets.HBox([play, slider, label])
            else:
                control = widgets.HBox([slider, label])
            return val[0], control, hash(repr(val))


def extract_num_options(val):
    """Convert a categorical to a number of options."""
    if len(val) == 1:
        for v in val:
            if isinstance(v, tuple):
                # this looks nightmarish...
                # but i think it should always work
                # should also check if the tuple has length one here.
                # that will only be an issue if a trailing comma was used to make the tuple
                # i.e ('beep',) but not ('beep') - the latter is not actually a tuple
                return len(v)
            else:
                return 0
    else:
        return len(val)


def changeify(val, update):
    """Make matplotlib update functions return a dict with key 'new'.

    This makes it compatible with the ipywidget callback style.
    """
    update({"new": val})


def create_mpl_controls_fig(kwargs):
    """
    Create a figure to hold matplotlib widgets.

    Returns
    -------
    fig : matplotlib figure
    slider_height : float
        Height of sliders in figure coordinates
    radio_height : float
        Height of radio buttons in figure coordinates

    Notes
    -----
    figure out how many inches we should devote to figure of the controls
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
    for _key, val in kwargs.items():
        if isinstance(val, set):
            new_opts = extract_num_options(val)
            if new_opts > 0:
                n_radio += 1
                n_opts += new_opts
        elif (
            not isinstance(val, mwidgets.AxesWidget)
            and "ipywidgets" not in str(val.__class__)  # do this to avoid depending on ipywidgets
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
    slider_height = 0
    radio_height = 0
    gap_height = 0
    if not all(isinstance(x, mwidgets.AxesWidget) for x in kwargs.values()):
        # if the only kwargs are existing matplotlib widgets don't make a new figure
        with ioff():
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
    """Create a slider that behaves similarly to the ipywidgets selection slider."""
    slider = mwidgets.Slider(ax, label, 0, len(values) - 1, valinit=0, valstep=1)

    def update_text(val):
        slider.valtext.set_text(slider_format_string.format(values[int(val)]))

    # make sure the initial value also gets formatted
    update_text(0)
    slider.on_changed(update_text)
    return slider


def create_mpl_range_selection_slider(ax, label, values, slider_format_string):
    """Create a slider that behaves similarly to the ipywidgets selection slider."""
    slider = RangeSlider(ax, label, 0, len(values) - 1, valinit=(0, len(values) - 1), valstep=1)

    def update_text(val):
        slider.valtext.set_text(
            slider_format_string.format(values[val[0]])
            + " - "
            + slider_format_string.format(values[val[-1]])
        )

    # make sure the initial value also gets formatted
    update_text((0, len(values) - 1))
    slider.on_changed(update_text)
    return slider


def process_mpl_widget(val, update):
    """Handle the case of a kwarg being an existing matplotlib widget.

    This needs to be separate so that the controller can call it when mixing ipywidets and
    a widget like scatter_selector without having to create a control figure.
    """
    if isinstance(val, mwidgets.RadioButtons):
        cb = val.on_clicked(partial(changeify, update=partial(update, values=None)))
        return val.value_selected, val, cb, hash(repr(val.labels))
    elif isinstance(val, (mwidgets.Slider, mwidgets.RangeSlider, RangeSlider)):
        # TODO: proper inherit matplotlib rand
        # potential future improvement:
        # check if valstep has been set and then try to infer the values
        # but not now, I'm trying to avoid premature optimization lest this
        # drag on forever
        cb = val.on_changed(partial(changeify, update=partial(update, values=None)))
        hash_ = hash(str(val.valmin) + str(val.valmax) + str(val.valstep))
        return val.val, val, cb, hash_
    else:
        cb = val.on_changed(partial(changeify, update=partial(update, values=None)))
        return val.val, val, cb, hash(repr(val))


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
    """Convert a kwarg to a matplotlib widget.

    Parameters
    ----------
    fig : matplotlib figure
        The figure in which to place the widgets.
    heights : tuple
        with slider_height, radio_height, gap_height
    widget_y : float
        How much vertical space the widget should take up
    key : str
        The name of the kwarg.
    val : str or number or tuple, or set or array-like
        The value to be interpreted and possibly transformed into an ipywidget
    update : callable
        The function to be called when the value of the generated widget changes.
        Must accept a dictionary *change* and an array-like *values*
    slider_format_string : str
        The format string to use for slider labels
    play_button : bool or None or str, default: None
        If true and the output widget is a slider then added a play button widget
        on the left. Also accepts 'left' or 'right' to specify the play button position.
    play_button_pos : str
        Where to place the play button.

    Returns
    -------
    init_val
    widget
    cb
        the callback id
    new_y
        The widget_y to use for the next pass.
    hash
    """
    slider_height, radio_height, gap_height = heights

    # widget_y = 0.05
    slider_ax = []
    radio_ax = []
    radio_buttons = []
    if isinstance(val, set):
        if len(val) == 1:
            val = val.pop()
            if isinstance(val, tuple):
                pass
            else:
                return val, None, None, widget_y, hash(repr(val))
        else:
            val = list(val)

        n = len(val)
        longest_len = max([len(list(x)) for x in map(str, val)])
        # should probably use something based on fontsize rather that .015
        width = max(0.15, 0.015 * longest_len)
        radio_ax = fig.add_axes([0.2, 0.9 - widget_y - radio_height * n, width, radio_height * n])
        widget_y += radio_height * n + gap_height
        radio_buttons = mwidgets.RadioButtons(radio_ax, val, active=0)
        cb = radio_buttons.on_clicked(partial(changeify, update=partial(update, values=None)))
        return val[0], radio_buttons, cb, widget_y, hash(repr(val))
    elif isinstance(val, mwidgets.AxesWidget):
        val, widget, cb, hash_ = process_mpl_widget(val, update)
        return val, widget, cb, widget_y, hash_
    else:
        slider = None
        if isinstance(val, tuple) and val[0] in ["r", "range", "rang", "rage"]:
            if isinstance(val[1], (np.ndarray, list)):
                vals = val[1]
            else:
                vals = np.linspace(*val[1:])
            slider_ax = fig.add_axes([0.2, 0.9 - widget_y - gap_height, 0.65, slider_height])
            slider = create_mpl_range_selection_slider(slider_ax, key, vals, slider_format_string)
            cb = slider.on_changed(partial(changeify, update=partial(update, values=vals)))
            widget_y += slider_height + gap_height
            return vals[[0, -1]], slider, cb, widget_y, hash(repr(vals))

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
                return min_, slider, cb, widget_y, hash(repr(val))
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
            return val[0], None, None, widget_y, hash(repr(val))
        else:
            slider_ax = fig.add_axes([0.2, 0.9 - widget_y - gap_height, 0.65, slider_height])
            slider = create_mpl_selection_slider(slider_ax, key, val, slider_format_string)
            slider.on_changed(partial(changeify, update=partial(update, values=val)))
            widget_y += slider_height + gap_height
            return val[0], slider, None, widget_y, hash(repr(val))


def create_slider_format_dict(slider_format_string):
    """Create a dictionray of format strings based on the slider contents."""
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
            "slider_format_string must be a dict or a string"
            f" but it is a {type(slider_format_string)}"
        )
    return slider_format_strings


def gogogo_figure(ipympl, ax=None):
    """Gogogo the greatest function name of all."""
    if ax is None:
        if ipympl:
            with ioff():
                ax = gca()
                fig = ax.get_figure()
        else:
            ax = gca()
            fig = ax.get_figure()
        return fig, ax
    else:
        return ax.get_figure(), ax


def choose_fmt_str(dtype=None):
    """
    Choose the appropriate string formatting for different dtypes.

    Parameters
    ----------
    dtype : np.dtype
        dtype of array containing values to be formatted.

    Returns
    -------
    fmt : str
        Bracket style format string.
    """
    if np.issubdtype(dtype, "float"):
        fmt = r"{:0.2f}"

    elif np.issubdtype(dtype, "int"):
        fmt = r"{:d}"

    else:
        fmt = r"{:}"

    return fmt
