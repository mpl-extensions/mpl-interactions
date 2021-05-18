import numpy as np

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

try:
    from matplotlib.widgets import RangeSlider, SliderBase
except ImportError:
    from ._widget_backfill import RangeSlider, SliderBase

__all__ = [
    "scatter_selector",
    "scatter_selector_index",
    "scatter_selector_value",
    "RangeSlider",
    "SliderWrapper",
    "IntSlider",
    "IndexSlider",
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

    def _on_pick(self, event):
        if event.mouseevent.button == self._button:
            idx = event.ind[0]
            x = self._x[idx]
            y = self._y[idx]
            self._process(idx, (x, y))

    def _process(idx, val):
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


class SliderWrapper(HasTraits):
    """
    A warpper class that provides a consistent interface for both
    ipywidgets and matplotlib sliders.
    """

    min = Union([Int(), Float(), Tuple([Int(), Int()]), Tuple(Float(), Float())])
    max = Union([Int(), Float(), Tuple([Int(), Int()]), Tuple(Float(), Float())])
    value = Union([Float(), Int(), Tuple([Int(), Int()]), Tuple(Float(), Float())])
    step = Union([Int(), Float(allow_none=True)])
    label = Unicode()
    readout_format = Unicode("{:.2f}")

    def __init__(self, slider, readout_format=None, setup_value_callbacks=True):
        super().__init__()
        self._raw_slider = slider
        # eventually we can just rely on SliderBase here
        # for now keep both for compatibility with mpl < 3.4
        self._mpl = isinstance(slider, (mwidgets.Slider, SliderBase))
        if self._mpl:
            self.observe(lambda change: setattr(self._raw_slider, "valmin", change["new"]), "min")
            self.observe(lambda change: setattr(self._raw_slider, "valmax", change["new"]), "max")
            self.observe(lambda change: self._raw_slider.label.set_text(change["new"]), "label")
            if setup_value_callbacks:
                self.observe(lambda change: self._raw_slider.set_val(change["new"]), "value")
                self._raw_slider.on_changed(lambda val: setattr(self, "value", val))
                self.value = self._raw_slider.val
            self.min = self._raw_slider.valmin
            self.max = self._raw_slider.valmax
            self.step = self._raw_slider.valstep
            self.label = self._raw_slider.label.get_text()
        else:
            if setup_value_callbacks:
                link((slider, "value"), (self, "value"))
            link((slider, "min"), (self, "min"))
            link((slider, "max"), (self, "max"))
            link((slider, "step"), (self, "step"))
            link((slider, "description"), (self, "label"))
        self._callbacks = []

    @observe("value")
    def _on_changed(self, change):
        for c in self._callbacks:
            c(change["new"])

    def on_changed(self, callback):
        # callback registry?
        self._callbacks.append(callback)

    def _get_widget_for_display(self):
        return self._raw_slider

    def _ipython_display_(self):
        if self._mpl:
            pass
        else:
            display(self._get_widget_for_display())

    def __dir__(self):
        # hide all the cruft from traitlets for shfit+Tab
        return [i for i in super().__dir__() if i not in _gross_traits]


class IntSlider(SliderWrapper):
    min = Int()
    max = Int()
    value = Int()


class IndexSlider(IntSlider):
    """
    A slider class to index through an array of values.
    """

    index = Int()
    max_index = Int()
    value = Any()
    values = Array()
    # gotta make values traitlike - traittypes?

    def __init__(self, values, label="", mpl_slider_ax=None, play_button=False):
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
        self.values = np.atleast_1d(values)
        self.readout_format = "{:.2f}"
        if mpl_slider_ax is not None:
            # make mpl_slider
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
                slider.valtext.set_text(self.readout_format.format(self.values[int(val)]))

            slider.on_changed(onchange)
            self.values
        elif widgets:
            slider = widgets.IntSlider(
                0, 0, self.values.shape[0] - 1, step=1, readout=False, description=label
            )
            self._readout = widgets.Label(value=str(self.values[0]))
            widgets.dlink(
                (slider, "value"),
                (self._readout, "value"),
                transform=lambda x: self.readout_format.format(self.values[x]),
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
        super().__init__(slider, setup_value_callbacks=False)
        self.value = self.values[self.index]

    def _get_widget_for_display(self):
        if self._play_button:
            if self._play_button_on_left:
                return widgets.HBox([self._play_button, self._raw_slider, self._readout])
            else:
                return widgets.HBox([self._raw_slider, self._readout, self._play_button])
        return widgets.HBox([self._raw_slider, self._readout])

    @validate("value")
    def _validate_value(self, proposal):
        if not proposal["value"] in self.values:
            raise TraitError(
                f"{proposal['value']} is not in the set of values for this index slider."
                " To see or change the set of valid values use the `.values` attribute"
            )
        # call `int` because traitlets can't handle np int64
        index = int(np.argmin(np.abs(self.values - proposal["value"])))
        self.index = index

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
