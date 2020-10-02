import warnings
from collections.abc import Callable, Iterable

import matplotlib.cm as cm
import numpy as np
from matplotlib import __version__ as mpl_version
from matplotlib import get_backend
from matplotlib.colors import TABLEAU_COLORS, XKCD_COLORS, to_rgba_array
from matplotlib.path import Path
from matplotlib.pyplot import close, subplots, sci
from matplotlib.widgets import LassoSelector
from numpy import asanyarray, asarray, max, min, swapaxes
from packaging import version

from .helpers import *
from .utils import figure, ioff, nearest_idx
from .controller import gogogo_controls

# functions that are methods
__all__ = [
    "heatmap_slicer",
    "zoom_factory",
    "panhandler",
    "image_segmenter",
    "hyperslicer",
]


def heatmap_slicer(
    X,
    Y,
    heatmaps,
    slices="horizontal",
    heatmap_names=None,
    max_cols=None,
    cmap=None,
    vmin=None,
    vmax=None,
    figsize=(18, 9),
    linecolor="k",
    labels=("X", "Y"),
    interaction_type="move",
    fig=None,
):

    """
    Compare horizontal and/or vertical slices accross multiple arrays.

    Parameters
    ----------
    X,Y : 1D array
    heatmaps : array_like
       must be 2-D or 3-D. If 3-D the last two axes should be (X,Y)
    slice : {'horizontal', 'vertical', 'both'}
        Direction to draw slice on heatmap. both will draw horizontal and vertical traces on the same
        plot, while both_separate will make a line plot for each.
    heatmap_names : (String, String, ...)
        An iterable with the names of the heatmaps. If provided it must have as many names as there are heatmaps
    max_cols : int, optional - not working yet :(
        Maximum number of columns to allow
    cmap : str or Colormap, optional
        A Colormap instance or registered colormap name. The colormap maps the C values to colors.
    vmin, vmax : float, optional
        The colorbar range. If None, suitable min/max values are automatically chosen by the Normalize instance.
    ax : matplolibt.Axes or None
        axes on which to
    y_scale : string or tuple of floats, optional
        If a tuple it will be passed to ax.set_ylim. Other options are:
        'auto': rescale the y axis for every redraw
        'stretch': only ever expand the ylims.
    slider_format_string : string
        A valid format string, this will be used to render
        the current value of the parameter
    plot_kwargs : None, dict, or iterable of dicts
        Keyword arguments to pass to plot. If using multiple f's then plot_kwargs must be either
        None or be iterable.l
        figure size to pass to `plt.subplots`
    labels : (string, string), optional
    interaction_type : str
        Update on mouse movement or mouse click. Options are {'move','click'}
    fig : matplotlib figure, optional
        figure to use for the heatmap_slicer. Useful when embedding into a gui.
        If you are embedding into a gui make sure you set up the gui canvas first
        and then pass the figure to this function

    Returns
    -------
    fig : matplotlib figure
    ax  : tuple of axes
    """
    horiz = vert = False
    if slices == "both":
        num_line_axes = 2
        horiz_axis = -2
        vert_axis = -1
        horiz = vert = True
    else:
        horiz_axis = -1
        vert_axis = -1
        num_line_axes = 1
        if slices == "horizontal":
            horiz = True
        elif slices == "vertical":
            vert = True
        else:
            raise ValueError("Valid options for slices are {horizontal, vertical, both}")

    heatmaps = asarray(heatmaps)
    if heatmap_names is None:
        heatmap_names = [f"heatmap_{i}" for i in range(heatmaps.shape[0])]

    if heatmaps.ndim == 3:
        num_axes = num_line_axes + heatmaps.shape[0]
        if type(heatmap_names) is str or (len(heatmap_names) != heatmaps.shape[0]):
            raise ValueError("need to provide at least as many heatmap_names as heatmaps")
    elif heatmaps.ndim == 2:
        heatmaps = heatmaps.reshape(1, *heatmaps.shape)
        if type(heatmap_names) is str:
            heatmap_names = [heatmap_names]
        num_axes = num_line_axes + 1
    else:
        raise ValueError(f"heatmaps must be 2D or 3D but is {heatmaps.ndim}D")

    if fig is None:
        fig, axes = subplots(1, num_axes, figsize=figsize)
    else:
        axes = fig.subplots(1, num_axes)

    hlines = []
    vlines = []
    init_idx = 0
    axes[0].set_ylabel(labels[1])
    X = asarray(X)
    Y = asarray(Y)
    # mpl pcolormesh from verison 3.3+ handles len(X), len(Y) equal to Z shape
    # differently than <2. (Unquestionably better, but different enough to justify a shim)
    # https://github.com/matplotlib/matplotlib/pull/16258
    mpl_gr_33 = version.parse(mpl_version) >= version.parse("3.3")
    if mpl_gr_33:
        shading = "auto"
    else:
        shading = "flat"

    x_centered = X[:-1] + (X[1:] - X[:-1]) / 2
    y_centered = Y[:-1] + (Y[1:] - Y[:-1]) / 2
    for i, ax in enumerate(axes[:-num_line_axes]):
        ax.pcolormesh(X, Y, heatmaps[i], cmap=cmap, vmin=vmin, vmax=vmax, shading=shading)
        ax.set_xlabel(labels[0])
        ax.set_title(heatmap_names[i])
        hmap_shape = asanyarray(heatmaps[i]).shape

        if i > 0:
            ax.set_yticklabels([])
        if horiz:
            same_shape = X.shape[0] == hmap_shape[1]
            if same_shape:
                x = X
            else:
                x = x_centered
            data_line = axes[horiz_axis].plot(
                x, heatmaps[i, init_idx, :], label=f"{heatmap_names[i]}"
            )[0]
            hlines.append((same_shape, ax.axhline(Y[init_idx], color=linecolor), data_line))

        if vert:
            same_shape = Y.shape[0] == hmap_shape[0]
            if same_shape:
                y = Y
            else:
                y = y_centered
            data_line = axes[vert_axis].plot(
                y, heatmaps[i, :, init_idx], label=f"{heatmap_names[i]}"
            )[0]
            vlines.append((same_shape, ax.axvline(X[init_idx], color=linecolor), data_line))

    minimum = min(heatmaps)
    maximum = max(heatmaps)
    if vert:
        axes[vert_axis].set_title("Vertical")
        axes[vert_axis].set_ylim([minimum, maximum])
        axes[vert_axis].legend()
    if horiz:
        axes[horiz_axis].set_title("Horizontal")
        axes[horiz_axis].set_ylim([minimum, maximum])
        axes[horiz_axis].legend()

    def _gen_idxs(orig, centered, same_shape, event_data):
        """
        is there a better way? probably, but this gets the job done
        so here we are...
        """
        if same_shape:
            data_idx = nearest_idx(orig, event_data)
            if mpl_gr_33:
                disp_idx = nearest_idx(orig, event_data)
                arr = orig
            else:
                disp_idx = nearest_idx(centered, event_data)
                arr = centered
        else:
            disp_idx = nearest_idx(centered, event_data)
            data_idx = nearest_idx(centered, event_data)
            arr = centered
        return arr, data_idx, disp_idx

    def update_lines(event):
        if event.inaxes in axes[:-num_line_axes]:
            y = None
            for i, (same_shape, display_line, data_line) in enumerate(hlines):
                if y is None:
                    y, data_idx, disp_idx = _gen_idxs(Y, y_centered, same_shape, event.ydata)
                display_line.set_ydata(y[disp_idx])
                data_line.set_ydata(heatmaps[i, data_idx])
            x = None
            for i, (same_shape, display_line, data_line) in enumerate(vlines):
                if x is None:
                    x, data_idx, disp_idx = _gen_idxs(X, x_centered, same_shape, event.xdata)
                display_line.set_xdata(x[disp_idx])
                data_line.set_ydata(heatmaps[i, :, data_idx])
        fig.canvas.draw_idle()

    if interaction_type == "move":
        fig.canvas.mpl_connect("motion_notify_event", update_lines)
    elif interaction_type == "click":
        fig.canvas.mpl_connect("button_press_event", update_lines)
    else:
        close(fig)
        raise ValueError(
            f"{interaction_type} is not a valid option for interaction_type, valid options are 'click' or 'move'"
        )
    return fig, axes


# based on https://gist.github.com/tacaswell/3144287
def zoom_factory(ax, base_scale=1.1):
    """
    Add ability to zoom with the scroll wheel.

    parameters
    ----------
    ax : matplotlib axes object
        axis on which to implement scroll to zoom
    base_scale : float
        how much zoom on each tick of scroll wheel

    returns
    -------
    disconnect_zoom : function
        call this to disconnect the scroll listener
    """

    def limits_to_range(lim):
        return lim[1] - lim[0]

    fig = ax.get_figure()  # get the figure of interest
    fig.canvas.capture_scroll = True
    has_toolbar = hasattr(fig.canvas, "toolbar") and fig.canvas.toolbar is not None
    if has_toolbar:
        # it might be possible to have an interactive backend without
        # a toolbar. I'm not sure so being safe here
        toolbar = fig.canvas.toolbar
        toolbar.push_current()
    orig_xlim = ax.get_xlim()
    orig_ylim = ax.get_ylim()
    orig_yrange = limits_to_range(orig_ylim)
    orig_xrange = limits_to_range(orig_xlim)
    orig_center = ((orig_xlim[0] + orig_xlim[1]) / 2, (orig_ylim[0] + orig_ylim[1]) / 2)

    def zoom_fun(event):
        if not event.inaxes is ax:
            return
        # get the current x and y limits
        cur_xlim = ax.get_xlim()
        cur_ylim = ax.get_ylim()
        # set the range
        cur_xrange = (cur_xlim[1] - cur_xlim[0]) * 0.5
        cur_yrange = (cur_ylim[1] - cur_ylim[0]) * 0.5
        xdata = event.xdata  # get event x location
        ydata = event.ydata  # get event y location
        if event.button == "up":
            # deal with zoom in
            scale_factor = base_scale
        elif event.button == "down":
            # deal with zoom out
            scale_factor = 1 / base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
        # set new limits
        new_xlim = [
            xdata - (xdata - cur_xlim[0]) / scale_factor,
            xdata + (cur_xlim[1] - xdata) / scale_factor,
        ]
        new_ylim = [
            ydata - (ydata - cur_ylim[0]) / scale_factor,
            ydata + (cur_ylim[1] - ydata) / scale_factor,
        ]
        new_yrange = limits_to_range(new_ylim)
        new_xrange = limits_to_range(new_xlim)

        if abs(new_yrange) > abs(orig_yrange):
            new_ylim = orig_center[1] - new_yrange / 2, orig_center[1] + new_yrange / 2
        if abs(new_xrange) > abs(orig_xrange):
            new_xlim = orig_center[0] - new_xrange / 2, orig_center[0] + new_xrange / 2
        ax.set_xlim(new_xlim)
        ax.set_ylim(new_ylim)

        if has_toolbar:
            toolbar.push_current()
        ax.figure.canvas.draw_idle()  # force re-draw

    # attach the call back
    cid = fig.canvas.mpl_connect("scroll_event", zoom_fun)

    def disconnect_zoom():
        fig.canvas.mpl_disconnect(cid)

    # return the disconnect function
    return disconnect_zoom


class panhandler:
    """
    Enable panning a plot with any mouse button.

    button determines which button will be used (default right click)
    Left: 1
    Middle: 2
    Right: 3
    """

    def __init__(self, fig, button=3):
        self.fig = fig
        self._id_drag = None
        self.button = button
        self.fig.canvas.mpl_connect("button_press_event", self.press)
        self.fig.canvas.mpl_connect("button_release_event", self.release)

    def _cancel_action(self):
        self._xypress = []
        if self._id_drag:
            self.fig.canvas.mpl_disconnect(self._id_drag)
            self._id_drag = None

    def press(self, event):
        if event.button != self.button:
            self._cancel_action()
            return

        x, y = event.x, event.y

        self._xypress = []
        for i, a in enumerate(self.fig.get_axes()):
            if (
                x is not None
                and y is not None
                and a.in_axes(event)
                and a.get_navigate()
                and a.can_pan()
            ):
                a.start_pan(x, y, event.button)
                self._xypress.append((a, i))
                self._id_drag = self.fig.canvas.mpl_connect("motion_notify_event", self._mouse_move)

    def release(self, event):
        self._cancel_action()
        self.fig.canvas.mpl_disconnect(self._id_drag)

        for a, _ind in self._xypress:
            a.end_pan()
        if not self._xypress:
            self._cancel_action()
            return
        self._cancel_action()

    def _mouse_move(self, event):
        for a, _ind in self._xypress:
            # safer to use the recorded button at the _press than current
            # button: # multiple button can get pressed during motion...
            a.drag_pan(1, event.key, event.x, event.y)
        self.fig.canvas.draw_idle()


class image_segmenter:
    """
    Manually segment an image with the lasso selector.
    """

    def __init__(
        self,
        img,
        nclasses=1,
        mask=None,
        mask_colors=None,
        mask_alpha=0.75,
        figsize=(10, 10),
        cmap="viridis",
    ):
        """
        parameters
        ----------
        img : array_like
            A valid argument to imshow
        nclasses : int, default 1
        mask: arraylike, optional
            If you want to pre-seed the mask
        mask_colors : None, color, or array of colors, optional
            the colors to use for each class. Unselected regions will always be totally transparent
        mask_alpha : float, default .75
            The alpha values to use for selected regions. This will always override the alpha values
            in mask_colors if any were passed
        figsize : (float, float), optional
            passed to plt.figure
        cmap : 'string'
            the colormap to use if img has shape (X,Y)
        """

        # ensure mask colors is iterable and the same length as the number of classes
        # choose colors from default color cycle?

        self.mask_alpha = mask_alpha

        if mask_colors is None:
            # this will break if there are more than 10 classes
            if nclasses <= 10:
                self.mask_colors = to_rgba_array(list(TABLEAU_COLORS)[:nclasses])
            else:
                # up to 949 classes. Hopefully that is always enough....
                self.mask_colors = to_rgba_array(list(XKCD_COLORS)[:nclasses])
        else:
            self.mask_colors = to_rgba_array(np.atleast_1d(mask_colors))
            # should probably check the shape here
        self.mask_colors[:, -1] = self.mask_alpha

        self._img = np.asarray(img)

        if mask is None:
            self.mask = np.zeros(self._img.shape[:2])
        else:
            self.mask = mask

        self._overlay = np.zeros((*self._img.shape[:2], 4))
        self.nclasses = nclasses
        for i in range(nclasses + 1):
            idx = self.mask == i
            if i == 0:
                self._overlay[idx] = [0, 0, 0, 0]
            else:
                self._overlay[idx] = self.mask_colors[i - 1]
        with ioff:
            self.fig = figure(figsize=figsize)
            self.ax = self.fig.gca()
            self.displayed = self.ax.imshow(self._img)
            self._mask = self.ax.imshow(self._overlay)

        lineprops = {"color": "black", "linewidth": 1, "alpha": 0.8}
        useblit = False if "ipympl" in get_backend().lower() else True
        self.lasso = LassoSelector(self.ax, self._onselect, lineprops=lineprops, useblit=useblit)
        self.lasso.set_visible(True)

        pix_x = np.arange(self._img.shape[0])
        pix_y = np.arange(self._img.shape[1])
        xv, yv = np.meshgrid(pix_y, pix_x)
        self.pix = np.vstack((xv.flatten(), yv.flatten())).T

        self.ph = panhandler(self.fig)
        self.disconnect_zoom = zoom_factory(self.ax)
        self.current_class = 1
        self.erasing = False

    def _onselect(self, verts):
        self.verts = verts
        p = Path(verts)
        self.indices = p.contains_points(self.pix, radius=0).reshape(self.mask.shape)
        if self.erasing:
            self.mask[self.indices] = 0
            self._overlay[self.indices] = [0, 0, 0, 0]
        else:
            self.mask[self.indices] = self.current_class
            self._overlay[self.indices] = self.mask_colors[self.current_class - 1]

        self._mask.set_data(self._overlay)
        self.fig.canvas.draw_idle()

    def _ipython_display_(self):
        display(self.fig.canvas)


def hyperslicer(
    arr,
    cmap=None,
    norm=None,
    aspect=None,
    interpolation=None,
    alpha=None,
    vmin=None,
    vmax=None,
    origin=None,
    extent=None,
    autoscale_cmap=True,
    filternorm=True,
    filterrad=4.0,
    resample=None,
    url=None,
    ax=None,
    slider_formats=None,
    title=None,
    force_ipywidgets=False,
    play_buttons=False,
    play_button_pos="right",
    is_color_image=False,
    controls=None,
    display_controls=True,
    **kwargs,
):

    """
    View slices from a hyperstack of images selected by sliders.

    parameters
    ----------
    arr : array like
        Hyperstack of images. The last 2 or 3 dimensions will be treated as individiual images.
    cmap : str or `~matplotlib.colors.Colormap`
        The Colormap instance or registered colormap name used to map
        scalar data to colors. This parameter is ignored for RGB(A) data.
        forwarded to matplotlib
    norm: `~matplotlib.colors.Normalize`, optional
        The `.Normalize` instance used to scale scalar data to the [0, 1]
        range before mapping to colors using *cmap*. By default, a linear
        scaling mapping the lowest value to 0 and the highest to 1 is used.
        This parameter is ignored for RGB(A) data.
        forwarded to matplotlib
    autoscale_cmap : bool
        If True rescale the colormap for every function update. Will not update
        if vmin and vmax are provided or if the returned image is RGB(A) like.
        forwarded to matplotlib
    aspect : {'equal', 'auto'} or float
        forwarded to matplotlib
        interpolation : str
        forwarded to matplotlib
    ax : matplotlib axis, optional
        if None a new figure and axis will be created
    slider_formats : None, string, or dict
        If None a default value of decimal points will be used. Uses the new {} style formatting
    title : None or string
        If a string then you can have it update automatically using string formatting of the names
        of the parameters. i.e. to include the current value of tau: title='the value of tau is: {tau:.2f}'
    force_ipywidgets : boolean
         If True ipywidgets will always be used, even if not using the ipympl backend.
         If False the function will try to detect if it is ok to use ipywidgets
         If ipywidgets are not used the function will fall back on matplotlib widgets
     play_buttons : bool or dict or list(str), optional
        Whether to attach an ipywidgets.Play widget to any sliders that get created.
        If a boolean it will apply to all kwargs, if a dictionary you choose which sliders you
        want to attach play buttons too. If a list of strings use the names of the parameters that
        you want to have sliders
        left' or 'right'. Whether to position the play widget(s) to the left or right of the slider(s)
    is_color_image : boolean
        If True, will treat the last 3 dimensions as comprising a color images and will only set up sliders for the first arr.ndim - 3 dimensions.
    controls : mpl_interactions.controller.Controls
        An existing controls object if you want to tie multiple plot elements to the same set of
        controls
    display_controls : boolean
        Whether the controls should display themselve on creation. Ignored if controls is specified.

    returns
    -------
    controls
    """

    arr = np.asarray(np.squeeze(arr))
    if arr.ndim < 3 + is_color_image:
        raise ValueError(
            f"arr must be at least {3+is_color_image}D but it is {arr.ndim}D. mpl_interactions.imshow for 2D images."
        )

    if is_color_image:
        im_dims = 3
    else:
        im_dims = 2

    ipympl = notebook_backend()
    fig, ax = gogogo_figure(ipympl, ax)
    use_ipywidgets = ipympl or force_ipywidgets
    slider_format_strings = create_slider_format_dict(slider_formats)

    name_to_dim = {}
    slices = [0 for i in range(arr.ndim - im_dims)]

    names = None
    axes = None
    if "names" in kwargs:
        names = kwargs.pop("names")

    elif "axes" in kwargs:
        axes = kwargs.pop("axes")

    # Just pass in an array - no kwargs
    for i in range(arr.ndim - im_dims):

        slider_arr_passed = False
        start, stop = None, None
        name = f"axis{i}"
        if name in kwargs:
            if len(kwargs[name]) == 2:
                start, stop = kwargs.pop(name)
            else:
                slider_arr_passed = True
                slider_arr = kwargs.pop(name)

        if axes is not None and axes[i] is not None:
            # no we assume the axes[i] has one of the following forms
            # ('mu', (0,1))
            # ('mu', np.array)
            # ('mu', 0, 1)
            # (0, 1)
            # 'mu'
            # np.array or a list
            a = axes[i]
            if isinstance(a, str):
                # axes = ['mu', ]
                name = a
            elif isinstance(a, tuple):
                if len(a) == 3:
                    # axes = [('mu', 0, 1)]
                    name = a[0]
                    kwargs[name] = (*a[1:], arr.shape[i])
                elif len(a) == 2:
                    if isinstance(a[0], str):
                        # axes = [('mu', (0,1))]
                        # axes = [('mu', np.linspace())]
                        # axes = [('mu', {('type1', 'type2', 'type3')}]
                        name = a[0]
                        if isinstance(a[1], tuple) or (isinstance(a[1], list) and len(a[1]) == 2):
                            kwargs[name] = (*a[1], arr.shape[i])
                        elif isinstance(a[1], np.ndarray) or isinstance(a[1], list):
                            kwargs[name] = a[1]
                        elif isinstance(a[1], set):
                            kwargs[name] = a[1]
                    elif np.isscalar(a[0]) and np.isscalar(a[1]):
                        # axes = [(0,1)]
                        kwargs[name] = (a[0], a[1], arr.shape[i])
                        slider_format_strings[name] = "{:.0f}"
            elif isinstance(a, list) or isinstance(np.ndarray):
                # no name only values
                kwargs[name] = a
        elif names is not None and names[i] is not None:
            name = names[i]
        name_to_dim[name] = i

        if not name in kwargs:
            slider_format_strings[name] = "{:.0f}"
            kwargs[name] = np.arange(arr.shape[i])

    controls, params = gogogo_controls(
        kwargs, controls, display_controls, slider_format_strings, play_buttons, play_button_pos
    )

    def update(params, indices, cache):
        if title is not None:
            ax.set_title(title.format(**params))

        for k, v in indices.items():
            slices[name_to_dim[k]] = v

        new_data = arr[tuple(slices)]
        im.set_data(new_data)

        if autoscale_cmap and (new_data.ndim != 3) and vmin is None and vmax is None:
            im.norm.autoscale(new_data)

        if isinstance(vmin, Callable):
            im.norm.vmin = vmin(**params)
        if isinstance(vmax, Callable):
            im.norm.vmax = vmax(**params)

    controls.register_function(update, fig, params.keys())
    # make it once here so we can use the dims in update
    new_data = arr[tuple(0 for i in range(arr.ndim - im_dims))]
    im = ax.imshow(
        new_data,
        cmap=cmap,
        norm=norm,
        aspect=aspect,
        interpolation=interpolation,
        alpha=alpha,
        vmin=callable_else_value(vmin, params),
        vmax=callable_else_value(vmax, params),
        origin=origin,
        extent=extent,
        filternorm=filternorm,
        filterrad=filterrad,
        resample=resample,
        url=url,
    )
    # this is necessary to make calls to plt.colorbar behave as expected
    sci(im)
    if title is not None:
        ax.set_title(title.format(**params))

    return controls
