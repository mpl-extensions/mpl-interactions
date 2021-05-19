import numpy as np
from numbers import Number

from traitlets import (
    HasTraits,
    Int,
    Float,
    Union,
    observe,
    dlink,
    link,
    Tuple,
    Unicode,
    validate,
    TraitError,
    Any,
)
from traittypes import Array

try:
    import ipywidgets as widgets
    from ipywidgets.widgets.widget_link import jslink
    from IPython.display import display
except ImportError:
    widgets = None
from matplotlib import widgets as mwidgets
from matplotlib.cbook import CallbackRegistry
from matplotlib.widgets import AxesWidget
from matplotlib.ticker import ScalarFormatter

try:
    from matplotlib.widgets import RangeSlider, SliderBase
except ImportError:
    from ._widget_backfill import RangeSlider, SliderBase
import matplotlib.widgets as mwidgets

__all__ = [
    "scatter_selector",
    "scatter_selector_index",
    "scatter_selector_value",
    "RangeSlider",
    "SliderWrapper",
    "IntSlider",
    "IndexSlider",
    "CategoricalWrapper",
]


class scatter_selector(AxesWidget):
    """
    A widget for selecting a point in a scatter plot. callback will receive (index, (x, y))
    """

    def __init__(self, ax, x, y, pickradius=5, which_button=1, **kwargs):
        """
        Create the scatter plot and selection machinery.

        Parameters
        ----------
        ax : Axes
            The Axes on which to make the scatter plot
        x, y : float or array-like, shape (n, )
            The data positions.
        pickradius : float
            Pick radius, in points.
        which_button : int, default: 1
            Where 1=left, 2=middle, 3=right

        Other Parameters
        ----------------
        **kwargs : arguments to scatter
            Other keyword arguments are passed directly to the ``ax.scatter`` command

        """
        super().__init__(ax)
        self.scatter = ax.scatter(x, y, **kwargs, picker=True)
        self.scatter.set_pickradius(pickradius)
        self._observers = CallbackRegistry()
        self._x = x
        self._y = y
        self._button = which_button
        self.connect_event("pick_event", self._on_pick)
        self._init_val()

    def _init_val(self):
        self.val = (0, (self._x[0], self._y[0]))
        self.value = (0, (self._x[0], self._y[0]))

    def _on_pick(self, event):
        if event.mouseevent.button == self._button:
            idx = event.ind[0]
            x = self._x[idx]
            y = self._y[idx]
            self._process(idx, (x, y))

    def _process(self, idx, val):
        self._observers.process("picked", idx, val)

    def on_changed(self, func):
        """
        When a point is clicked calll *func* with the newly selected point

        Parameters
        ----------
        func : callable
            Function to call when slider is changed.
            The function must accept a (int, tuple(float, float)) as its arguments.

        Returns
        -------
        int
            Connection id (which can be used to disconnect *func*)
        """
        return self._observers.connect("picked", lambda idx, val: func(idx, val))


class scatter_selector_index(scatter_selector):
    """
    A widget for selecting a point in a scatter plot. callback will receive the index of
    the selected point as an argument.
    """

    def _init_val(self):
        self.val = 0
        self.value = 0

    def _process(self, idx, val):
        self._observers.process("picked", idx)

    def on_changed(self, func):
        """
        When a point is clicked calll *func* with the newly selected point's index
        and position as arguments.

        Parameters
        ----------
        func : callable
            Function to call when slider is changed.
            The function must accept a single int as its arguments.

        Returns
        -------
        int
            Connection id (which can be used to disconnect *func*)
        """
        return self._observers.connect("picked", lambda idx: func(idx))


class scatter_selector_value(scatter_selector):
    """
    A widget for selecting a point in a scatter plot. callbacks will receive the x,y position of
    the selected point as arguments.
    """

    def _init_val(self):
        self.val = (self._x[0], self._y[0])
        self.value = (self._x[0], self._y[0])

    def _process(self, idx, val):
        self._observers.process("picked", val)

    def on_changed(self, func):
        """
        When a point is clicked calll *func* with the newly selected point's index
        as arguments.

        Parameters
        ----------
        func : callable
            Function to call when slider is changed.
            The function must accept a single int as its arguments.

        Returns
        -------
        int
            Connection id (which can be used to disconnect *func*)
        """
        return self._observers.connect("picked", lambda val: func(val))


_gross_traits = [
    "add_traits",
    "class_own_trait_events",
    "class_own_traits",
    "class_trait_names",
    "class_traits",
    "cross_validation_lock",
    "has_trait",
    "hold_trait_notifications",
    "notify_change",
    "on_trait_change",
    "set_trait",
    "setup_instance",
    "trait_defaults",
    "trait_events",
    "trait_has_value",
    "trait_metadata",
    "trait_names",
    "trait_values",
    "traits",
]


class HasTraitsSmallShiftTab(HasTraits):
    def __dir__(self):
        # hide all the cruft from traitlets for shift+Tab
        return [i for i in super().__dir__() if i not in _gross_traits]


class WidgetWrapper(HasTraitsSmallShiftTab):
    value = Any()

    def __init__(self, mpl_widget, **kwargs) -> None:
        super().__init__(self)
        self._mpl = mpl_widget
        self._callbacks = []

    def on_changed(self, callback):
        # callback registry?
        self._callbacks.append(callback)

    def _get_widget_for_display(self):
        if self._mpl:
            return None
        else:
            return self._raw_widget

    def _ipython_display_(self):
        if self._mpl:
            pass
        else:
            display(self._get_widget_for_display())

    @observe("value")
    def _on_changed(self, change):
        for c in self._callbacks:
            c(change["new"])


class SliderWrapper(WidgetWrapper):
    """
    A warpper class that provides a consistent interface for both
    ipywidgets and matplotlib sliders.
    """

    min = Union([Int(), Float(), Tuple([Int(), Int()]), Tuple(Float(), Float())])
    max = Union([Int(), Float(), Tuple([Int(), Int()]), Tuple(Float(), Float())])
    value = Union([Float(), Int(), Tuple([Int(), Int()]), Tuple(Float(), Float())])
    step = Union([Int(), Float(allow_none=True)])
    label = Unicode()

    def __init__(self, slider, readout_format=None, setup_value_callbacks=True, **kwargs):
        self._mpl = isinstance(slider, (mwidgets.Slider, SliderBase))
        super().__init__(self, **kwargs)
        self._raw_widget = slider

        # eventually we can just rely on SliderBase here
        # for now keep both for compatibility with mpl < 3.4
        if self._mpl:
            self.observe(lambda change: setattr(self._raw_widget, "valmin", change["new"]), "min")
            self.observe(lambda change: setattr(self._raw_widget, "valmax", change["new"]), "max")
            self.observe(lambda change: self._raw_widget.label.set_text(change["new"]), "label")
            if setup_value_callbacks:
                self.observe(lambda change: self._raw_widget.set_val(change["new"]), "value")
                self._raw_widget.on_changed(lambda val: setattr(self, "value", val))
                self.value = self._raw_widget.val
            self.min = self._raw_widget.valmin
            self.max = self._raw_widget.valmax
            self.step = self._raw_widget.valstep
            self.label = self._raw_widget.label.get_text()
        else:
            if setup_value_callbacks:
                link((slider, "value"), (self, "value"))
            link((slider, "min"), (self, "min"))
            link((slider, "max"), (self, "max"))
            link((slider, "step"), (self, "step"))
            link((slider, "description"), (self, "label"))


class IntSlider(SliderWrapper):
    min = Int()
    max = Int()
    value = Int()


class SelectionWrapper(WidgetWrapper):
    index = Int()
    values = Array()
    max_index = Int()

    def __init__(self, values, mpl_ax=None, **kwargs) -> None:
        super().__init__(mpl_ax is not None, **kwargs)
        self.values = values
        self.value = self.values[self.index]

    @validate("value")
    def _validate_value(self, proposal):
        if not proposal["value"] in self.values:
            raise TraitError(
                f"{proposal['value']} is not in the set of values for this index slider."
                " To see or change the set of valid values use the `.values` attribute"
            )
        # call `int` because traitlets can't handle np int64
        self.index = int(np.where(self.values == proposal["value"])[0][0])

        return proposal["value"]

    @observe("index")
    def _obs_index(self, change):
        # call .item because traitlets is unhappy with numpy types
        self.value = self.values[change["new"]].item()

    @validate("values")
    def _validate_values(self, proposal):
        values = proposal["value"]
        if values.ndim > 1:
            raise TraitError("Expected 1d array but got an array with shape %s" % (values.shape))
        self.max_index = values.shape[0]
        return values


class IndexSlider(SelectionWrapper):
    """
    A slider class to index through an array of values.
    """

    def __init__(
        self, values, label="", mpl_slider_ax=None, readout_format=None, play_button=False
    ):
        """
        Parameters
        ----------
        values : 1D arraylike
            The values to index over
        label : str
            The slider label
        mpl_slider_ax : matplotlib.axes or None
            If *None* an ipywidgets slider will be created
        """
        super().__init__(values, mpl_ax=mpl_slider_ax)
        self.values = np.atleast_1d(values)
        self.readout_format = readout_format
        self._scalar_formatter = ScalarFormatter(useOffset=False)
        self._scalar_formatter.create_dummy_axis()
        if mpl_slider_ax is not None:
            # make mpl_slider
            if play_button:
                raise ValueError(
                    "Play Buttons not yet available for matplotlib sliders "
                    "see https://github.com/ianhi/mpl-interactions/issues/144"
                )
            slider = mwidgets.Slider(
                mpl_slider_ax,
                label=label,
                valinit=0,
                valmin=0,
                valmax=self.values.shape[0] - 1,
                valstep=1,
            )

            def onchange(val):
                self.index = int(val)
                slider.valtext.set_text(self._format_value(self.values[int(val)]))

            slider.on_changed(onchange)
        elif widgets:
            # i've basically recreated the ipywidgets.SelectionSlider here.
            slider = widgets.IntSlider(
                0, 0, self.values.shape[0] - 1, step=1, readout=False, description=label
            )
            self._readout = widgets.Label(value=str(self.values[0]))
            widgets.dlink(
                (slider, "value"),
                (self._readout, "value"),
                transform=lambda x: self._format_value(self.values[x]),
            )
            self._play_button = None
            if play_button:
                self._play_button = widgets.Play(step=1)
                self._play_button_on_left = not (
                    isinstance(play_button, str) and play_button == "right"
                )
                jslink((slider, "value"), (self._play_button, "value"))
                jslink((slider, "min"), (self._play_button, "min"))
                jslink((slider, "max"), (self._play_button, "max"))
            link((slider, "value"), (self, "index"))
            link((slider, "max"), (self, "max_index"))
        else:
            raise ValueError("mpl_slider_ax cannot be None if ipywidgets is not available")
        self._raw_widget = slider

    def _format_value(self, value):
        if self.readout_format is None:
            if isinstance(value, Number):
                return self._scalar_formatter.format_data_short(value)
            else:
                return str(value)
        return self.readout_format.format(value)

    def _get_widget_for_display(self):
        if self._mpl:
            return None
        if self._play_button:
            if self._play_button_on_left:
                return widgets.HBox([self._play_button, self._raw_widget, self._readout])
            else:
                return widgets.HBox([self._raw_widget, self._readout, self._play_button])
        return widgets.HBox([self._raw_widget, self._readout])


# A vendored version of ipywidgets.fixed - included so don't need to depend on ipywidgets
# https://github.com/jupyter-widgets/ipywidgets/blob/e0d41f6f02324596a282bc9e4650fd7ba63c0004/ipywidgets/widgets/interaction.py#L546
class fixed(HasTraitsSmallShiftTab):
    """A pseudo-widget whose value is fixed and never synced to the client."""

    value = Any(help="Any Python object")
    description = Unicode("", help="Any Python object")

    def __init__(self, value, **kwargs):
        super().__init__(value=value, **kwargs)

    def get_interact_value(self):
        """Return the value for this widget which should be passed to
        interactive functions. Custom widgets can change this method
        to process the raw value ``self.value``.
        """
        return self.value


class CategoricalWrapper(SelectionWrapper):
    def __init__(self, values, mpl_ax=None, **kwargs):
        super().__init__(values, mpl_ax=mpl_ax, **kwargs)

        if mpl_ax is not None:
            self._raw_widget = mwidgets.RadioButtons(mpl_ax, values)

            def on_changed(label):
                self.index = self._raw_widget.active

            self._raw_widget.on_changed(on_changed)
        else:
            self._raw_widget = widgets.Select(options=values)
            link((self._raw_widget, "index"), (self, "index"))
