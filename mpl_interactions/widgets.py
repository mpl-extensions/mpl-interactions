from matplotlib.cbook import CallbackRegistry
from matplotlib.widgets import AxesWidget

__all__ = [
    "scatter_selector",
    "scatter_selector_index",
    "scatter_selector_value",
]


class scatter_selector(AxesWidget):
    """"""

    def __init__(self, ax, x, y, pickradius=5, which_button=1, **kwargs):
        """
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
        blah blah blah
        """
        return self._observers.connect("picked", lambda idx, val: func(idx, val))


class scatter_selector_index(scatter_selector):
    """
    this docstring???
    ``on_changed`` will send the index of the selected point.
    """

    def _init_val(self):
        self.val = 0

    def _process(self, idx, val):
        self._observers.process("picked", idx)

    def on_changed(self, func):
        """
        blah blah blah
        """
        return self._observers.connect("picked", lambda idx: func(idx))


class scatter_selector_value(scatter_selector):
    def _init_val(self):
        self.val = (self._x[0], self._y[0])

    def _process(self, idx, val):
        self._observers.process("picked", val)

    def on_changed(self, func):
        """
        blah blah blah
        """
        return self._observers.connect("picked", lambda val: func(val))
