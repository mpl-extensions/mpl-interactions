from matplotlib.cbook import CallbackRegistry
from matplotlib.widgets import AxesWidget
from matplotlib import cbook, ticker
import numpy as np

__all__ = [
    "scatter_selector",
    "scatter_selector_index",
    "scatter_selector_value",
    "RangeSlider",
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


# slider widgets are taken almost verbatim from https://github.com/matplotlib/matplotlib/pull/18829/files
# which was written by me - but incorporates much of the existing matplotlib slider infrastructure
class SliderBase(AxesWidget):
    def __init__(
        self, ax, orientation, closedmin, closedmax, valmin, valmax, valfmt, dragging, valstep
    ):
        if ax.name == "3d":
            raise ValueError("Sliders cannot be added to 3D Axes")

        super().__init__(ax)

        self.orientation = orientation
        self.closedmin = closedmin
        self.closedmax = closedmax
        self.valmin = valmin
        self.valmax = valmax
        self.valstep = valstep
        self.drag_active = False
        self.valfmt = valfmt

        if orientation == "vertical":
            ax.set_ylim((valmin, valmax))
            axis = ax.yaxis
        else:
            ax.set_xlim((valmin, valmax))
            axis = ax.xaxis

        self._fmt = axis.get_major_formatter()
        if not isinstance(self._fmt, ticker.ScalarFormatter):
            self._fmt = ticker.ScalarFormatter()
            self._fmt.set_axis(axis)
        self._fmt.set_useOffset(False)  # No additive offset.
        self._fmt.set_useMathText(True)  # x sign before multiplicative offset.

        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_navigate(False)
        self.connect_event("button_press_event", self._update)
        self.connect_event("button_release_event", self._update)
        if dragging:
            self.connect_event("motion_notify_event", self._update)
        self._observers = cbook.CallbackRegistry()

    def _stepped_value(self, val):
        if self.valstep:
            return self.valmin + round((val - self.valmin) / self.valstep) * self.valstep
        return val

    def disconnect(self, cid):
        """
        Remove the observer with connection id *cid*

        Parameters
        ----------
        cid : int
            Connection id of the observer to be removed
        """
        self._observers.disconnect(cid)

    def reset(self):
        """Reset the slider to the initial value"""
        if self.val != self.valinit:
            self.set_val(self.valinit)


class RangeSlider(SliderBase):
    """
    A slider representing a floating point range.

    Create a slider from *valmin* to *valmax* in axes *ax*. For the slider to
    remain responsive you must maintain a reference to it. Call
    :meth:`on_changed` to connect to the slider event.

    Attributes
    ----------
    val : tuple of float
        Slider value.
    """

    def __init__(
        self,
        ax,
        label,
        valmin,
        valmax,
        valinit=None,
        valfmt=None,
        closedmin=True,
        closedmax=True,
        dragging=True,
        valstep=None,
        orientation="horizontal",
        **kwargs,
    ):
        """
        Parameters
        ----------
        ax : Axes
            The Axes to put the slider in.

        label : str
            Slider label.

        valmin : float
            The minimum value of the slider.

        valmax : float
            The maximum value of the slider.

        valinit : tuple of float or None, default: None
            The initial positions of the slider. If None the initial positions
            will be at the 25th and 75th percentiles of the range.

        valfmt : str, default: None
            %-format string used to format the slider values.  If None, a
            `.ScalarFormatter` is used instead.

        closedmin : bool, default: True
            Whether the slider interval is closed on the bottom.

        closedmax : bool, default: True
            Whether the slider interval is closed on the top.

        dragging : bool, default: True
            If True the slider can be dragged by the mouse.

        valstep : float, default: None
            If given, the slider will snap to multiples of *valstep*.

        orientation : {'horizontal', 'vertical'}, default: 'horizontal'
            The orientation of the slider.

        Notes
        -----
        Additional kwargs are passed on to ``self.poly`` which is the
        `~matplotlib.patches.Rectangle` that draws the slider knob.  See the
        `.Rectangle` documentation for valid property names (``facecolor``,
        ``edgecolor``, ``alpha``, etc.).
        """
        super().__init__(
            ax, orientation, closedmin, closedmax, valmin, valmax, valfmt, dragging, valstep
        )

        self.val = valinit
        if valinit is None:
            valinit = np.array([valmin + 0.25 * valmax, valmin + 0.75 * valmax])
        else:
            valinit = self._value_in_bounds(valinit)
        self.val = valinit
        self.valinit = valinit
        if orientation == "vertical":
            self.poly = ax.axhspan(valinit[0], valinit[1], 0, 1, **kwargs)
        else:
            self.poly = ax.axvspan(valinit[0], valinit[1], 0, 1, **kwargs)

        if orientation == "vertical":
            self.label = ax.text(
                0.5,
                1.02,
                label,
                transform=ax.transAxes,
                verticalalignment="bottom",
                horizontalalignment="center",
            )

            self.valtext = ax.text(
                0.5,
                -0.02,
                self._format(valinit),
                transform=ax.transAxes,
                verticalalignment="top",
                horizontalalignment="center",
            )
        else:
            self.label = ax.text(
                -0.02,
                0.5,
                label,
                transform=ax.transAxes,
                verticalalignment="center",
                horizontalalignment="right",
            )

            self.valtext = ax.text(
                1.02,
                0.5,
                self._format(valinit),
                transform=ax.transAxes,
                verticalalignment="center",
                horizontalalignment="left",
            )

        self.set_val(valinit)

    def _min_in_bounds(self, min):
        """
        Ensure the new min value is between valmin and self.val[1]
        """
        if min <= self.valmin:
            if not self.closedmin:
                return self.val[0]
            min = self.valmin

        if min > self.val[1]:
            min = self.val[1]
        return self._stepped_value(min)

    def _max_in_bounds(self, max):
        """
        Ensure the new max value is between valmax and self.val[0]
        """
        if max >= self.valmax:
            if not self.closedmax:
                return self.val[1]
            max = self.valmax

        if max <= self.val[0]:
            max = self.val[0]
        return self._stepped_value(max)

    def _value_in_bounds(self, val):
        return (self._min_in_bounds(val[0]), self._max_in_bounds(val[1]))

    def _update_val_from_pos(self, pos):
        """
        Given a position update the *val*
        """
        idx = np.argmin(np.abs(self.val - pos))
        if idx == 0:
            val = self._min_in_bounds(pos)
            self.set_min(val)
        else:
            val = self._max_in_bounds(pos)
            self.set_max(val)

    def _update(self, event):
        """Update the slider position."""
        if self.ignore(event) or event.button != 1:
            return

        if event.name == "button_press_event" and event.inaxes == self.ax:
            self.drag_active = True
            event.canvas.grab_mouse(self.ax)

        if not self.drag_active:
            return

        elif (event.name == "button_release_event") or (
            event.name == "button_press_event" and event.inaxes != self.ax
        ):
            self.drag_active = False
            event.canvas.release_mouse(self.ax)
            return
        if self.orientation == "vertical":
            self._update_val_from_pos(event.ydata)
        else:
            self._update_val_from_pos(event.xdata)

    def _format(self, val):
        """Pretty-print *val*."""
        if self.valfmt is not None:
            return (self.valfmt % val[0], self.valfmt % val[1])
        else:
            # fmt.get_offset is actually the multiplicative factor, if any.
            _, s1, s2, _ = self._fmt.format_ticks([self.valmin, *val, self.valmax])
            # fmt.get_offset is actually the multiplicative factor, if any.
            s1 += self._fmt.get_offset()
            s2 += self._fmt.get_offset()
            # use raw string to avoid issues with backslashes from
            return rf"({s1}, {s2})"

    def set_min(self, min):
        """
        Set the lower value of the slider to *min*

        Parameters
        ----------
        min : float
        """
        self.set_val((min, self.val[1]))

    def set_max(self, max):
        """
        Set the lower value of the slider to *max*

        Parameters
        ----------
        max : float
        """
        self.set_val((self.val[0], max))

    def set_val(self, val):
        """
        Set slider value to *val*

        Parameters
        ----------
        val : tuple or arraylike of float
        """
        val = np.sort(np.asanyarray(val))
        if val.shape != (2,):
            raise ValueError(f"val must have shape (2,) but has shape {val.shape}")
        val[0] = self._min_in_bounds(val[0])
        val[1] = self._max_in_bounds(val[1])
        xy = self.poly.xy
        if self.orientation == "vertical":
            xy[0] = 0, val[0]
            xy[1] = 0, val[1]
            xy[2] = 1, val[1]
            xy[3] = 1, val[0]
            xy[4] = 0, val[0]
        else:
            xy[0] = val[0], 0
            xy[1] = val[0], 1
            xy[2] = val[1], 1
            xy[3] = val[1], 0
            xy[4] = val[0], 0
        self.poly.xy = xy
        self.valtext.set_text(self._format(val))
        if self.drawon:
            self.ax.figure.canvas.draw_idle()
        self.val = val
        if self.eventson:
            self._observers.process("changed", val)

    def on_changed(self, func):
        """
        When the slider value is changed call *func* with the new
        slider value

        Parameters
        ----------
        func : callable
            Function to call when slider is changed.
            The function must accept a numpy array with shape (2,) float
            as its argument.

        Returns
        -------
        int
            Connection id (which can be used to disconnect *func*)
        """
        return self._observers.connect("changed", func)
