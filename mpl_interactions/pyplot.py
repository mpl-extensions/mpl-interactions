"""Control the output of standard plotting functions such as :func:`~matplotlib.pyplot.plot` and
:func:`~matplotlib.pyplot.hist` using sliders and other widgets.

 When using the ``ipympl`` backend these functions will leverage ipywidgets for the controls,
otherwise they will use the built-in
Matplotlib widgets.
"""  # noqa: D205


from collections.abc import Callable
from numbers import Number

import matplotlib.markers as mmarkers
import numpy as np
from matplotlib.collections import PatchCollection
from matplotlib.colors import to_rgba_array
from matplotlib.patches import Rectangle

from .controller import gogogo_controls, prep_scalars
from .helpers import (
    callable_else_value,
    callable_else_value_no_cast,
    create_slider_format_dict,
    eval_xy,
    gogogo_figure,
    notebook_backend,
    sca,
    update_datalim_from_bbox,
)
from .mpl_kwargs import (
    Line2D_kwargs_list,
    Text_kwargs_list,
    collection_kwargs_list,
    imshow_kwargs_list,
    kwarg_popper,
)

__all__ = [
    "interactive_plot",
    "interactive_hist",
    "interactive_scatter",
    "interactive_imshow",
    "interactive_axhline",
    "interactive_axvline",
    "interactive_title",
    "interactive_xlabel",
    "interactive_ylabel",
    "interactive_text",
]


def interactive_plot(  # noqa: D417 - not my fault
    *args,
    parametric=False,
    ax=None,
    slider_formats=None,
    xlim="stretch",
    ylim="stretch",
    force_ipywidgets=False,
    play_buttons=None,
    controls=None,
    display_controls=True,
    **kwargs,
):
    """
    Control a plot using widgets.

    interactive_plot([x], y, [fmt])

    where x/y is are either arraylike or a function that returns arrays. Any kwargs accepted by
    `matplotlib.pyplot.plot` will be passed through, other kwargs will be intrepreted as controls

    Parameters
    ----------
    x, y : array-like or scalar or function
        The horizontal / vertical coordinates of the data points.
        *x* values are optional and default to ``range(len(y))``. If both *x* and *y* are
        provided and *y* is a function then it will be called as ``y(x, **params)``. If
        *x* is a function it will be called as ``x(**params)``
    fmt : str, optional
        A format string, e.g. 'ro' for red circles. See matplotlib.pyplot.plot
        for full documentation.
        as xlim
    parametric : boolean
        If True then the function expects to have only received a value for y and that that
        function will return an array for both x and y, or will return an array with shape (N, 2)
    ax : matplotlib axis, optional
        The axis on which to plot. If none the current axis will be used.
    slider_formats : None, string, or dict
        If None a default value of decimal points will be used. Uses the new {} style formatting
    xlim : string or tuple of floats, optional
        If a tuple it will be passed to ax.set_xlim. Other options are:
        'auto': rescale the x axis for every redraw
        'stretch': only ever expand the xlims.
    ylim : string or tuple of floats, optional
        If a tuple it will be passed to ax.set_ylim. Other options are same as xlim
    force_ipywidgets : boolean
        If True ipywidgets will always be used, even if not using the ipympl backend.
        If False the function will try to detect if it is ok to use ipywidgets
        If ipywidgets are not used the function will fall back on matplotlib widgets
    play_buttons : bool or str or dict, optional
        Whether to attach an ipywidgets.Play widget to any sliders that get created.
        If a boolean it will apply to all kwargs, if a dictionary you choose which sliders you
        want to attach play buttons too.

        - None: no sliders
        - True: sliders on the lft
        - False: no sliders
        - 'left': sliders on the left
        - 'right': sliders on the right

    controls : mpl_interactions.controller.Controls
        An existing controls object if you want to tie multiple plot elements to the same set of
        controls
    display_controls : boolean
        Whether the controls should display on creation. Ignored if controls is specified.
    **kwargs:
        Interpreted as widgets and remainder are passed through to `ax.plot`.

    Returns
    -------
    controls

    Examples
    --------
    With numpy arrays::

        x = np.linspace(0,2*np.pi)
        tau = np.linspace(0, np.pi)
        def f(tau):
            return np.sin(x*tau)
        interactive_plot(f, tau=tau)

    with tuples::

        x = np.linspace(0,2*np.pi)
        def f(x, tau):
            return np.sin(x+tau)
        interactive_plot(x, f, tau=(0, np.pi, 1000))

    """
    kwargs, plot_kwargs = kwarg_popper(kwargs, Line2D_kwargs_list)
    x_and_y = False
    x = None
    fmt = None
    if len(args) == 0:
        # wot...
        return
    elif len(args) == 1:
        y = args[0]
    elif len(args) == 2:
        # either (y, fmt) or (x, y)
        # hard to know for sure though bc fmt can be a function
        # or maybe just requirement that fmt is a function
        if isinstance(args[1], str):
            y, fmt = args
        else:
            x_and_y = True
            x, y = args
    elif len(args) == 3:
        x_and_y = True
        x, y, fmt = args
    else:
        raise ValueError(f"You passed in {len(args)} args, but no more than 3 is supported.")

    ipympl = notebook_backend() or force_ipywidgets
    fig, ax = gogogo_figure(ipympl, ax=ax)
    slider_formats = create_slider_format_dict(slider_formats)
    controls, params = gogogo_controls(
        kwargs, controls, display_controls, slider_formats, play_buttons
    )

    def update(params, indices, cache):
        if x_and_y:
            x_, y_ = eval_xy(x, y, params, cache)
            # broadcast so that we can always index
            if x_.ndim == 1:
                x_ = np.broadcast_to(x_[:, None], (x_.shape[0], len(lines)))
            if y_.ndim == 1:
                y_ = np.broadcast_to(y_[:, None], (y_.shape[0], len(lines)))
            for i, line in enumerate(lines):
                line.set_data(x_[:, i], y_[:, i])
        elif parametric:
            # transpose to splat bc matplotlib considers columns of arrays to be
            # the datasets
            # I don't think it's possible to have multiple lines here
            # assert len(lines) == 1
            out = callable_else_value_no_cast(y, params, cache)
            if isinstance(out, tuple):
                pass
            elif isinstance(out, np.ndarray):
                # transpose bc set_data expects a different shape than plot
                out = np.asanyarray(out).T
            # else hope for the best lol
            lines[0].set_data(*out)
        else:
            y_ = callable_else_value(y, params, cache)
            if y_.ndim == 1:
                y_ = np.broadcast_to(y_[:, None], (y_.shape[0], len(lines)))
            for i, line in enumerate(lines):
                line.set_ydata(y_[:, i])

        cur_xlims = ax.get_xlim()
        cur_ylims = ax.get_ylim()
        ax.relim()  # this may be expensive? don't do if not necessary?
        if ylim == "auto":
            ax.autoscale_view(scalex=False)
        elif ylim == "stretch":
            new_lims = [ax.dataLim.y0, ax.dataLim.y0 + ax.dataLim.height]
            new_lims = [
                new_lims[0] if new_lims[0] < cur_ylims[0] else cur_ylims[0],
                new_lims[1] if new_lims[1] > cur_ylims[1] else cur_ylims[1],
            ]
            ax.set_ylim(new_lims)
        if xlim == "auto":
            ax.autoscale_view(scaley=False)
        elif xlim == "stretch":
            new_lims = [ax.dataLim.x0, ax.dataLim.x0 + ax.dataLim.width]
            new_lims = [
                new_lims[0] if new_lims[0] < cur_xlims[0] else cur_xlims[0],
                new_lims[1] if new_lims[1] > cur_xlims[1] else cur_xlims[1],
            ]
            ax.set_xlim(new_lims)

    controls._register_function(update, fig, params.keys())

    if x_and_y:
        x_, y_ = eval_xy(x, y, params)
        if fmt:
            lines = ax.plot(x_, y_, fmt, **plot_kwargs)
        else:
            lines = ax.plot(x_, y_, **plot_kwargs)
    else:
        y_ = callable_else_value_no_cast(y, params)
        # set up to ensure that splatting works well
        if parametric and not isinstance(y_, tuple):
            y_ = np.asanyarray(y_).T
        else:
            # make a tuple so we can splat it
            # reduces the number of if statements necessary to plot
            # parametric functions
            y_ = (y_,)

        if fmt:
            lines = ax.plot(*y_, fmt, **plot_kwargs)
        else:
            lines = ax.plot(*y_, **plot_kwargs)

    try:
        # hack in the way it feels like matplotlib should behave
        # this is a necessary change to support ODEs which is a reasonable use case for
        # this library - lesser of two evils situation. (the evil here is deviating from matplotlib)
        labels = plot_kwargs["label"]
        if (
            len(lines) > 1
            and (isinstance(labels, list) or isinstance(labels, tuple))
            and len(labels) == len(lines)
        ):
            for label, line in zip(labels, lines):
                line.set_label(label)
    except KeyError:
        pass

    if not isinstance(xlim, str):
        ax.set_xlim(xlim)
    if not isinstance(ylim, str):
        ax.set_ylim(ylim)

    # make sure the home button will work
    if hasattr(fig.canvas, "toolbar") and fig.canvas.toolbar is not None:
        fig.canvas.toolbar.push_current()
    # set current axis to be pyplot-like
    sca(ax)

    return controls


def _simple_hist(arr, bins="auto", density=None, weights=None):
    heights, bins = np.histogram(arr, bins=bins, density=density, weights=weights)
    width = bins[1] - bins[0]
    new_patches = []
    for i in range(len(heights)):
        new_patches.append(Rectangle((bins[i], 0), width=width, height=heights[i]))
    xlims = (bins.min(), bins.max())
    ylims = (0, heights.max() * 1.05)

    return xlims, ylims, new_patches


def _stretch(ax, xlims, ylims):
    cur_xlims = ax.get_xlim()
    cur_ylims = ax.get_ylim()
    new_lims = ylims
    new_lims = [
        new_lims[0] if new_lims[0] < cur_ylims[0] else cur_ylims[0],
        new_lims[1] if new_lims[1] > cur_ylims[1] else cur_ylims[1],
    ]
    ax.set_ylim(new_lims)
    new_lims = xlims
    new_lims = [
        new_lims[0] if new_lims[0] < cur_xlims[0] else cur_xlims[0],
        new_lims[1] if new_lims[1] > cur_xlims[1] else cur_xlims[1],
    ]
    ax.set_xlim(new_lims)


def interactive_hist(
    arr,
    density=False,
    bins="auto",
    weights=None,
    ax=None,
    slider_formats=None,
    force_ipywidgets=False,
    play_buttons=False,
    controls=None,
    display_controls=True,
    **kwargs,
):
    """
    Control the contents of a histogram using widgets.

    See https://github.com/mpl-extensions/mpl-interactions/pull/73#issue-470638134
    for a discussion of the limitations of this function. These limitations will
    can improved once https://github.com/matplotlib/matplotlib/pull/18275 has
    been merged.

    Parameters
    ----------
    arr : arraylike or function
        The array or the function that returns an array that is to be histogrammed
    density : bool, optional
        whether to plot as a probability density. Passed to `numpy.histogram`
    bins : int or sequence of scalars or str, optional
        bins argument to `numpy.histogram`
    weights : array_like, optional
        passed to `numpy.histogram`
    ax : matplotlib axis, optional
        The axis on which to plot. If none the current axis will be used.
    slider_formats : None, string, or dict
        If None a default value of decimal points will be used. Uses the new {} style formatting
    force_ipywidgets : boolean
        If True ipywidgets will always be used, even if not using the ipympl backend.
        If False the function will try to detect if it is ok to use ipywidgets
        If ipywidgets are not used the function will fall back on matplotlib widgets
    play_buttons : bool or str or dict, optional
        Whether to attach an ipywidgets.Play widget to any sliders that get created.
        If a boolean it will apply to all kwargs, if a dictionary you choose which sliders you
        want to attach play buttons too.

        - None: no sliders
        - True: sliders on the lft
        - False: no sliders
        - 'left': sliders on the left
        - 'right': sliders on the right

    controls : mpl_interactions.controller.Controls
        An existing controls object if you want to tie multiple plot elements to the same set of
        controls
    display_controls : boolean
        Whether the controls should display on creation. Ignored if controls is specified.
    **kwargs :
        Converted to widgets to control the parameters. Note, unlike other functions the remaining
        will NOT be passed through to *hist*.

    Returns
    -------
    controls

    Examples
    --------
    With numpy arrays::

        loc = np.linspace(-5, 5, 500)
        scale = np.linspace(1, 10, 100)
        def f(loc, scale):
            return np.random.randn(1000)*scale + loc
        interactive_hist(f, loc=loc, scale=scale)

    with tuples::

        def f(loc, scale):
            return np.random.randn(1000)*scale + loc
        interactive_hist(f, loc=(-5, 5, 500), scale=(1, 10, 100))
    """
    ipympl = notebook_backend() or force_ipywidgets
    fig, ax = gogogo_figure(ipympl, ax=ax)
    slider_formats = create_slider_format_dict(slider_formats)
    controls, params = gogogo_controls(
        kwargs, controls, display_controls, slider_formats, play_buttons
    )
    pc = PatchCollection([])
    ax.add_collection(pc, autolim=True)

    def update(params, indices, cache):
        arr_ = callable_else_value(arr, params, cache)
        new_x, new_y, new_patches = _simple_hist(arr_, density=density, bins=bins, weights=weights)
        _stretch(ax, new_x, new_y)
        pc.set_paths(new_patches)
        ax.autoscale_view()

    controls._register_function(update, fig, params.keys())

    new_x, new_y, new_patches = _simple_hist(
        callable_else_value(arr, params), density=density, bins=bins, weights=weights
    )
    sca(ax)
    pc.set_paths(new_patches)
    ax.set_xlim(new_x)
    ax.set_ylim(new_y)

    return controls


def interactive_scatter(
    x,
    y=None,
    s=None,
    c=None,
    vmin=None,
    vmax=None,
    vmin_vmax=None,
    alpha=None,
    marker=None,
    edgecolors=None,
    facecolors=None,
    label=None,
    parametric=False,
    ax=None,
    slider_formats=None,
    xlim="stretch",
    ylim="stretch",
    force_ipywidgets=False,
    play_buttons=False,
    controls=None,
    display_controls=True,
    **kwargs,
):
    """
    Control a scatter plot using widgets.

    Parameters
    ----------
    x, y : function or float or array-like
        shape (n, ) for array-like. Functions must return the correct shape as well. If y is None
        then parametric must be True and the function for x must return x, y
    c : array-like or list of colors or color or Callable
        Valid input to plt.scatter or a function
    s : float, array-like, function, or index controls object
        valid input to plt.scatter, or a function
    vmin, vmax : float, callable, shorthand for slider or indexed controls
        The vmin, vmax values for the colormap. Can accept a float for a fixed value,
        or any slider shorthand to control with a slider, or an indexed controls
        object to use an existing slider, or an arbitrary function of the other
        parameters.
    vmin_vmax : tuple of float
        Used to generate a range slider for vmin and vmax. Should be given in range slider
        notation: `("r", 0, 1)`.
    alpha : float or Callable, optional
        Affects all scatter points. This will compound with any alpha introduced by
        the ``c`` argument
    marker : MarkerStyle, or Callable, optional
        The marker style or a function returning marker styles.
    edgecolors : callable or valid argument to scatter
        passed through to scatter.
    facecolors : callable or valid argument to scatter
        Valid input to plt.scatter, or a function
    label : string
        Passed through to Matplotlib
    parametric : boolean
        If True then the function expects to have only received a value for y and that that function
        will return an array for both x and y, or will return an array with shape (N, 2)
    ax : matplotlib axis, optional
        The axis on which to plot. If none the current axis will be used.
    slider_formats : None, string, or dict
        If None a default value of decimal points will be used. Uses the new {} style formatting
    xlim : string or tuple of floats, optional
        If a tuple it will be passed to ax.set_xlim. Other options are:
        'auto': rescale the x axis for every redraw
        'stretch': only ever expand the xlims.
    ylim : string or tuple of floats, optional
        If a tuple it will be passed to ax.set_ylim. Other options are same as xlim
    force_ipywidgets : boolean
        If True ipywidgets will always be used, even if not using the ipympl backend.
        If False the function will try to detect if it is ok to use ipywidgets
        If ipywidgets are not used the function will fall back on matplotlib widgets
    play_buttons : bool or str or dict, optional
        Whether to attach an ipywidgets.Play widget to any sliders that get created.
        If a boolean it will apply to all kwargs, if a dictionary you choose which sliders you
        want to attach play buttons too.

        - None: no sliders
        - True: sliders on the lft
        - False: no sliders
        - 'left': sliders on the left
        - 'right': sliders on the right
    controls : mpl_interactions.controller.Controls
        An existing controls object if you want to tie multiple plot elements to the same set of
        controls
    display_controls : boolean
        Whether the controls should display on creation. Ignored if controls is specified.
    **kwargs:
        Interpreted as widgets and remainder are passed through to `ax.scatter`.

    Returns
    -------
    controls
    """
    if isinstance(xlim, str):
        stretch_x = xlim == "stretch"
    else:
        stretch_x = False

    if isinstance(ylim, str) and ylim.lower() == "stretch":
        stretch_y = True
    else:
        stretch_y = False

    # yanked from https://github.com/matplotlib/matplotlib/blob/bcc1ce8461f5b6e874baaaa02ef776d0243a4abe/lib/matplotlib/axes/_axes.py#L4271-L4273
    facecolors = kwargs.pop("facecolor", facecolors)
    edgecolors = kwargs.pop("edgecolor", edgecolors)

    ipympl = notebook_backend() or force_ipywidgets
    fig, ax = gogogo_figure(ipympl, ax)
    slider_formats = create_slider_format_dict(slider_formats)

    kwargs, collection_kwargs = kwarg_popper(kwargs, collection_kwargs_list)
    funcs, extra_ctrls, param_excluder = prep_scalars(
        kwargs, s=s, alpha=alpha, marker=marker, vmin=vmin, vmax=vmax
    )
    s = funcs["s"]
    vmin = funcs["vmin"]
    vmax = funcs["vmax"]
    alpha = funcs["alpha"]
    marker = funcs["marker"]

    if vmin_vmax is not None:
        if isinstance(vmin_vmax, tuple) and not isinstance(vmin_vmax[0], str):
            vmin_vmax = ("r", *vmin_vmax)
        kwargs["vmin_vmax"] = vmin_vmax

    controls, params = gogogo_controls(
        kwargs, controls, display_controls, slider_formats, play_buttons, extra_ctrls
    )
    if vmin_vmax is not None:
        params.pop("vmin_vmax")
        params["vmin"] = controls.params["vmin"]
        params["vmax"] = controls.params["vmax"]

        def vmin(**kwargs):
            return kwargs["vmin"]

        def vmax(**kwargs):
            return kwargs["vmax"]

    def update(params, indices, cache):
        if parametric:
            out = callable_else_value_no_cast(x, param_excluder(params))
            if not isinstance(out, tuple):
                out = np.asanyarray(out).T
            x_, y_ = out
        else:
            x_, y_ = eval_xy(x, y, param_excluder(params), cache)
        scatter.set_offsets(np.column_stack([x_, y_]))
        c_ = check_callable_xy(c, x_, y_, param_excluder(params), cache)
        s_ = check_callable_xy(s, x_, y_, param_excluder(params, "s"), cache)
        ec_ = check_callable_xy(edgecolors, x_, y_, param_excluder(params), cache)
        fc_ = check_callable_xy(facecolors, x_, y_, param_excluder(params), cache)
        a_ = callable_else_value_no_cast(alpha, param_excluder(params, "alpha"), cache)
        marker_ = callable_else_value_no_cast(marker, param_excluder(params), cache)

        if marker_ is not None:
            if not isinstance(marker_, mmarkers.MarkerStyle):
                marker_ = mmarkers.MarkerStyle(marker_)
            path = marker_.get_path().transformed(marker_.get_transform())
            scatter.set_paths((path,))

        if c_ is not None:
            try:
                c_ = to_rgba_array(c_)
            except ValueError:
                try:
                    c_ = scatter.cmap(c_)
                except TypeError as te:
                    raise ValueError from te(
                        "If c is a function it must return either an RGB(A) array"
                        "or a 1D array of valid color names or values to be colormapped"
                    )
            scatter.set_facecolor(c_)
        if ec_ is not None:
            scatter.set_edgecolor(ec_)
        if fc_ is not None:
            scatter.set_facecolor(c_)
        if s_ is not None:
            if isinstance(s_, Number):
                s_ = np.broadcast_to(s_, (len(x_),))
            scatter.set_sizes(s_)
        if a_ is not None:
            scatter.set_alpha(a_)
        if isinstance(vmin, Callable):
            scatter.norm.vmin = callable_else_value(vmin, param_excluder(params, "vmin"), cache)
        if isinstance(vmax, Callable):
            scatter.norm.vmax = callable_else_value(vmax, param_excluder(params, "vmax"), cache)

        update_datalim_from_bbox(
            ax, scatter.get_datalim(ax.transData), stretch_x=stretch_x, stretch_y=stretch_y
        )
        ax.autoscale_view()

    controls._register_function(update, fig, params.keys())

    def check_callable_xy(arg, x, y, params, cache):
        if isinstance(arg, Callable):
            if arg not in cache:
                cache[arg] = arg(x, y, **params)
            return cache[arg]
        else:
            return arg

    p = param_excluder(params)
    if parametric:
        out = callable_else_value_no_cast(x, p)
        if not isinstance(out, tuple):
            out = np.asanyarray(out).T
        x_, y_ = out
    else:
        x_, y_ = eval_xy(x, y, p)
    c_ = check_callable_xy(c, x_, y_, p, {})
    s_ = check_callable_xy(s, x_, y_, param_excluder(params, "s"), {})
    ec_ = check_callable_xy(edgecolors, x_, y_, p, {})
    fc_ = check_callable_xy(facecolors, x_, y_, p, {})
    marker_ = callable_else_value_no_cast(marker, p, {})
    scatter = ax.scatter(
        x_,
        y_,
        c=c_,
        s=s_,
        alpha=callable_else_value_no_cast(alpha, param_excluder(params, "alpha")),
        vmin=callable_else_value_no_cast(vmin, param_excluder(params, "vmin")),
        vmax=callable_else_value_no_cast(vmax, param_excluder(params, "vmax")),
        marker=marker_,
        edgecolors=ec_,
        facecolors=fc_,
        label=label,
        **collection_kwargs,
    )
    # this is necessary to make calls to plt.colorbar behave as expected
    sca(ax)
    ax._sci(scatter)

    return controls


# portions of this docstring were copied directly from the docsting
# of `matplotlib.pyplot.imshow`
def interactive_imshow(
    X,
    alpha=None,
    vmin=None,
    vmax=None,
    vmin_vmax=None,
    autoscale_cmap=True,
    ax=None,
    slider_formats=None,
    force_ipywidgets=False,
    play_buttons=False,
    controls=None,
    display_controls=True,
    **kwargs,
):
    """
    Control an image using widgets.

    Parameters
    ----------
    X : function or image like
        If a function it must return an image-like object. See matplotlib.pyplot.imshow for the
        full set of valid options.
    alpha : float, callable, shorthand for slider or indexed controls
        The alpha value of the image. Can accept a float for a fixed value,
        or any slider shorthand to control with a slider, or an indexed controls
        object to use an existing slider, or an arbitrary function of the other
        parameters.
    vmin, vmax : float, callable, shorthand for slider or indexed controls
        The vmin, vmax values for the colormap. Can accept a float for a fixed value,
        or any slider shorthand to control with a slider, or an indexed controls
        object to use an existing slider, or an arbitrary function of the other
        parameters.
    vmin_vmax : tuple of float
        Used to generate a range slider for vmin and vmax. Should be given in range slider
        notation: `("r", 0, 1)`.
    autoscale_cmap : bool
        If True rescale the colormap for every function update. Will not update
        if vmin and vmax are provided or if the returned image is RGB(A) like.
        forwarded to matplotlib
    ax : matplotlib axis, optional
        The axis on which to plot. If none the current axis will be used.
    slider_formats : None, string, or dict
        If None a default value of decimal points will be used. Uses the new {} style formatting
    force_ipywidgets : boolean
        If True ipywidgets will always be used, even if not using the ipympl backend.
        If False the function will try to detect if it is ok to use ipywidgets
        If ipywidgets are not used the function will fall back on matplotlib widgets
    play_buttons : bool or str or dict, optional
        Whether to attach an ipywidgets.Play widget to any sliders that get created.
        If a boolean it will apply to all kwargs, if a dictionary you choose which sliders you
        want to attach play buttons too.

        - None: no sliders
        - True: sliders on the lft
        - False: no sliders
        - 'left': sliders on the left
        - 'right': sliders on the right
    controls : mpl_interactions.controller.Controls
        An existing controls object if you want to tie multiple plot elements to the same set of
        controls
    display_controls : boolean
        Whether the controls should display on creation. Ignored if controls is specified.
    **kwargs:
        Interpreted as widgets and remainder are passed through to `ax.imshow`.

    Returns
    -------
    controls
    """
    ipympl = notebook_backend() or force_ipywidgets
    fig, ax = gogogo_figure(ipympl, ax)
    slider_formats = create_slider_format_dict(slider_formats)
    kwargs, imshow_kwargs = kwarg_popper(kwargs, imshow_kwargs_list)

    funcs, extra_ctrls, param_excluder = prep_scalars(kwargs, vmin=vmin, vmax=vmax, alpha=alpha)
    vmin = funcs["vmin"]
    vmax = funcs["vmax"]
    alpha = funcs["alpha"]

    if vmin_vmax is not None:
        if isinstance(vmin_vmax, tuple) and not isinstance(vmin_vmax[0], str):
            vmin_vmax = ("r", *vmin_vmax)
        kwargs["vmin_vmax"] = vmin_vmax

    controls, params = gogogo_controls(
        kwargs, controls, display_controls, slider_formats, play_buttons, extra_ctrls
    )
    if vmin_vmax is not None:
        params.pop("vmin_vmax")
        params["vmin"] = controls.params["vmin"]
        params["vmax"] = controls.params["vmax"]

        def vmin(**kwargs):
            return kwargs["vmin"]

        def vmax(**kwargs):
            return kwargs["vmax"]

    def update(params, indices, cache):
        if isinstance(X, Callable):
            # ignore anything that we added directly to kwargs in prep_scalar
            # if we don't do this then we might pass the user a kwarg their function
            # didn't expect and things may break
            # check this here to avoid setting the data if we don't need to
            # use the callable_else_value fxn to make use of easy caching
            new_data = callable_else_value(X, param_excluder(params), cache)
            im.set_data(new_data)
            if autoscale_cmap and (new_data.ndim != 3) and vmin is None and vmax is None:
                im.norm.autoscale(new_data)
        # caching for these?
        if isinstance(vmin, Callable):
            im.norm.vmin = callable_else_value(vmin, param_excluder(params, "vmin"), cache)
        if isinstance(vmax, Callable):
            im.norm.vmax = callable_else_value(vmax, param_excluder(params, "vmax"), cache)
        # Don't use callable_else_value to avoid unnecessary updates
        # Seems as though set_alpha doesn't short circuit if the value
        # hasn't been changed
        if isinstance(alpha, Callable):
            im.set_alpha(callable_else_value_no_cast(alpha, param_excluder(params, "alpha"), cache))

    controls._register_function(update, fig, params.keys())

    # make it once here so we can use the dims in update
    # see explanation for excluded_params in the update function
    new_data = callable_else_value(X, param_excluder(params))
    sca(ax)
    im = ax.imshow(
        new_data,
        alpha=callable_else_value_no_cast(alpha, param_excluder(params, "alpha")),
        vmin=callable_else_value_no_cast(vmin, param_excluder(params, "vmin")),
        vmax=callable_else_value_no_cast(vmax, param_excluder(params, "vmax")),
        **imshow_kwargs,
    )

    # i know it's bad news to use private methods :(
    # but idk how else to accomplish being a psuedo-pyplot
    ax._sci(im)
    return controls


def interactive_axhline(
    y=0,
    xmin=0,
    xmax=1,
    ax=None,
    slider_formats=None,
    force_ipywidgets=False,
    play_buttons=False,
    controls=None,
    display_controls=True,
    **kwargs,
):
    """
    Control an horizontal line using widgets.

    Parameters
    ----------
    y : float or function
        y position in data coordinates of the horizontal line.
    xmin : float or function
        Should be between 0 and 1, 0 being the far left of the plot, 1 the
        far right of the plot.
    xmax : float or function
        Should be between 0 and 1, 0 being the far left of the plot, 1 the
        far right of the plot.
    ax : matplotlib axis, optional
        If None a new figure and axis will be created
    slider_formats : None, string, or dict
        If None a default value of decimal points will be used. Uses the new {} style formatting
    force_ipywidgets : boolean
        If True ipywidgets will always be used, even if not using the ipympl backend.
        If False the function will try to detect if it is ok to use ipywidgets
        If ipywidgets are not used the function will fall back on matplotlib widgets
    play_buttons : bool or str or dict, optional
        Whether to attach an ipywidgets.Play widget to any sliders that get created.
        If a boolean it will apply to all kwargs, if a dictionary you choose which sliders you
        want to attach play buttons too.

        - None: no sliders
        - True: sliders on the lft
        - False: no sliders
        - 'left': sliders on the left
        - 'right': sliders on the right

    controls : mpl_interactions.controller.Controls
        An existing controls object if you want to tie multiple plot elements to the same set of
        controls
    display_controls : boolean
        Whether the controls should display on creation. Ignored if controls is specified.
    **kwargs
        Kwargs will be used to create control widgets. Except kwargs that are valid for Line2D are
        extracted and passed through to the creation of the line.

    Returns
    -------
    controls
    """
    ipympl = notebook_backend() or force_ipywidgets
    fig, ax = gogogo_figure(ipympl, ax)
    slider_formats = create_slider_format_dict(slider_formats)

    kwargs, line_kwargs = kwarg_popper(kwargs, Line2D_kwargs_list)
    line_kwargs.pop("transform", None)  # transform is not a valid kwarg for ax{v,h}line

    extra_ctrls = []
    funcs, extra_ctrls, param_excluder = prep_scalars(kwargs, y=y, xmin=xmin, xmax=xmax)
    y = funcs["y"]
    xmin = funcs["xmin"]
    xmax = funcs["xmax"]
    controls, params = gogogo_controls(
        kwargs, controls, display_controls, slider_formats, play_buttons, extra_ctrls
    )

    def update(params, indices, cache):
        y_ = callable_else_value(y, param_excluder(params, "y"), cache).item()
        line.set_ydata([y_, y_])
        xmin_ = callable_else_value(xmin, param_excluder(params, "xmin"), cache).item()
        xmax_ = callable_else_value(xmax, param_excluder(params, "xmax"), cache).item()
        line.set_xdata([xmin_, xmax_])
        # TODO consider updating just the ydatalim here

    controls._register_function(update, fig, params)
    sca(ax)
    line = ax.axhline(
        callable_else_value(y, param_excluder(params, "y")).item(),
        callable_else_value(xmin, param_excluder(params, "xmin")).item(),
        callable_else_value(xmax, param_excluder(params, "xmax")).item(),
        **line_kwargs,
    )
    return controls


def interactive_axvline(
    x=0,
    ymin=0,
    ymax=1,
    ax=None,
    slider_formats=None,
    force_ipywidgets=False,
    play_buttons=False,
    controls=None,
    display_controls=True,
    **kwargs,
):
    """
    Control a vertical line using widgets.

    Parameters
    ----------
    x : float or function
        x position in data coordinates of the horizontal line.
    ymin : float or function
        Should be between 0 and 1, 0 being the bottom of the plot, 1 the
        far top of the plot
    ymax : float or function
        Should be between 0 and 1, 0 being the top of the plot, 1 the
        top of the plot.
    ax : matplotlib axis, optional
        If None a new figure and axis will be created
    slider_formats : None, string, or dict
        If None a default value of decimal points will be used. Uses the new {} style formatting
    force_ipywidgets : boolean
        If True ipywidgets will always be used, even if not using the ipympl backend.
        If False the function will try to detect if it is ok to use ipywidgets
        If ipywidgets are not used the function will fall back on matplotlib widgets
    play_buttons : bool or str or dict, optional
        Whether to attach an ipywidgets.Play widget to any sliders that get created.
        If a boolean it will apply to all kwargs, if a dictionary you choose which sliders you
        want to attach play buttons too.

        - None: no sliders
        - True: sliders on the lft
        - False: no sliders
        - 'left': sliders on the left
        - 'right': sliders on the right

    controls : mpl_interactions.controller.Controls
        An existing controls object if you want to tie multiple plot elements to the same set of
        controls
    display_controls : boolean
        Whether the controls should display on creation. Ignored if controls is specified.
    **kwargs
        Kwargs will be used to create control widgets. Except kwargs that are valid for Line2D are
        extracted and passed through to the creation of the line.

    Returns
    -------
    controls
    """
    ipympl = notebook_backend() or force_ipywidgets
    fig, ax = gogogo_figure(ipympl, ax)
    slider_formats = create_slider_format_dict(slider_formats)

    kwargs, line_kwargs = kwarg_popper(kwargs, Line2D_kwargs_list)
    line_kwargs.pop("transform", None)  # transform is not a valid kwarg for ax{v,h}line

    extra_ctrls = []
    funcs, extra_ctrls, param_excluder = prep_scalars(kwargs, x=x, ymin=ymin, ymax=ymax)
    x = funcs["x"]
    ymin = funcs["ymin"]
    ymax = funcs["ymax"]

    controls, params = gogogo_controls(
        kwargs, controls, display_controls, slider_formats, play_buttons, extra_ctrls
    )

    def update(params, indices, cache):
        x_ = callable_else_value(x, param_excluder(params, "x"), cache).item()
        line.set_xdata([x_, x_])
        ymin_ = callable_else_value(ymin, param_excluder(params, "ymin"), cache).item()
        ymax_ = callable_else_value(ymax, param_excluder(params, "ymax"), cache).item()
        line.set_ydata([ymin_, ymax_])
        # TODO consider updating just the ydatalim here

    controls._register_function(update, fig, params)
    sca(ax)
    line = ax.axvline(
        callable_else_value(x, param_excluder(params, "x")).item(),
        callable_else_value(ymin, param_excluder(params, "ymin")).item(),
        callable_else_value(ymax, param_excluder(params, "ymax")).item(),
        **line_kwargs,
    )
    return controls


def interactive_title(
    title,
    controls=None,
    ax=None,
    *,
    fontdict=None,
    loc=None,
    y=None,
    pad=None,
    slider_formats=None,
    display_controls=True,
    play_buttons=False,
    force_ipywidgets=False,
    **kwargs,
):
    """Set the title to update interactively.

    kwargs for `matplotlib.text.Text` will be passed through, other kwargs will be used to create
    interactive controls.

    Parameters
    ----------
    title : str or function
        The title text. Can include {} style formatting. e.g. 'The voltage is {volts:.2f} mV'
    controls : mpl_interactions.controller.Controls
        An existing controls object if you want to tie multiple plot elements to the same set of
        controls
    ax : `matplotlib.axes.Axes`, optional
        The axis on which to plot. If none the current axis will be used.
    fontdict : dict[str]
        Passed through to the Text object. Currently not dynamically updateable. See
        https://github.com/mpl-extensions/mpl-interactions/issues/247
    loc : {'center', 'left', 'right'}, default: `axes.titlelocation <matplotlib.rcParams>`
        Which title to set.
    y : float, default: `axes.titley <matplotlib.rcParams>`
        Vertical axes loation for the title (1.0 is the top).  If
        None (the default), y is determined automatically to avoid
        decorators on the axes.
    pad : float, default: `axes.titlepad <matplotlib.rcParams>`
        The offset of the title from the top of the axes, in points.
    slider_formats : None, string, or dict
        If None a default value of decimal points will be used. Uses {} style formatting
    display_controls : boolean
        Whether the controls should display on creation. Ignored if controls is specified.
    play_buttons : bool or str or dict, optional
        Whether to attach an ipywidgets.Play widget to any sliders that get created.
        If a boolean it will apply to all kwargs, if a dictionary you choose which sliders you
        want to attach play buttons too.

        - None: no sliders
        - True: sliders on the lft
        - False: no sliders
        - 'left': sliders on the left
        - 'right': sliders on the right
    force_ipywidgets : boolean
        If True ipywidgets will always be used, even if not using the ipympl backend.
        If False the function will try to detect if it is ok to use ipywidgets
        If ipywidgets are not used the function will fall back on matplotlib widgets
    **kwargs:
        Passed through to `ax.set_title`

    Returns
    -------
    controls
    """
    ipympl = notebook_backend() or force_ipywidgets
    fig, ax = gogogo_figure(ipympl, ax)
    slider_formats = create_slider_format_dict(slider_formats)

    kwargs, text_kwargs = kwarg_popper(kwargs, Text_kwargs_list)

    controls, params = gogogo_controls(
        kwargs, controls, display_controls, slider_formats, play_buttons
    )

    def update(params, indices, cache):
        ax.set_title(
            callable_else_value_no_cast(title, params, cache).format(**params),
            fontdict=fontdict,
            loc=loc,
            pad=pad,
            y=y,
            **text_kwargs,
        )

    controls._register_function(update, fig, params)
    ax.set_title(
        callable_else_value_no_cast(title, params, None).format(**params),
        fontdict=fontdict,
        loc=loc,
        pad=pad,
        y=y,
        **text_kwargs,
    )
    return controls


def interactive_xlabel(
    xlabel,
    controls=None,
    ax=None,
    *,
    fontdict=None,
    labelpad=None,
    loc=None,
    slider_formats=None,
    display_controls=True,
    play_buttons=False,
    force_ipywidgets=False,
    **kwargs,
):
    """Set an xlabel that will update interactively.

    kwargs for `matplotlib.text.Text` will be passed through, other kwargs
    will be used to create interactive controls.

    Parameters
    ----------
    xlabel : str or function
        The label text. Can include {} style formatting. e.g. 'The voltage is {volts:.2f} mV'
    controls : mpl_interactions.controller.Controls
        An existing controls object if you want to tie multiple plot elements to the same set of
        controls
    ax : matplotlib axis, optional
        The axis on which to plot. If none the current axis will be used.
    fontdict : dict[str]
        Passed through to the Text object. Currently not dynamically updateable. See
        https://github.com/mpl-extensions/mpl-interactions/issues/247
    labelpad : float, default: None
        Spacing in points from the axes bounding box including ticks
        and tick labels.
    loc : {'bottom', 'center', 'top'}, default: `yaxis.labellocation <matplotlib.rcParams>`
        The label position. This is a high-level alternative for passing
        parameters *y* and *horizontalalignment*.
    slider_formats : None, string, or dict
        If None a default value of decimal points will be used. Uses {} style formatting
    display_controls : boolean
        Whether the controls should display on creation. Ignored if controls is specified.
    play_buttons : bool or str or dict, optional
        Whether to attach an ipywidgets.Play widget to any sliders that get created.
        If a boolean it will apply to all kwargs, if a dictionary you choose which sliders you
        want to attach play buttons too.

        - None: no sliders
        - True: sliders on the lft
        - False: no sliders
        - 'left': sliders on the left
        - 'right': sliders on the right
    force_ipywidgets : boolean
        If True ipywidgets will always be used, even if not using the ipympl backend.
        If False the function will try to detect if it is ok to use ipywidgets
        If ipywidgets are not used the function will fall back on matplotlib widgets
    **kwargs :
        Used to create widgets to control parameters. Kwargs for Text objects will passed
        through.


    Returns
    -------
    controls
    """
    ipympl = notebook_backend() or force_ipywidgets
    fig, ax = gogogo_figure(ipympl, ax)
    slider_formats = create_slider_format_dict(slider_formats)

    kwargs, text_kwargs = kwarg_popper(kwargs, Text_kwargs_list)
    controls, params = gogogo_controls(
        kwargs, controls, display_controls, slider_formats, play_buttons
    )

    def update(params, indices, cache):
        ax.set_xlabel(
            callable_else_value_no_cast(xlabel, params, cache).format(**params),
            fontdict=fontdict,
            labelpad=labelpad,
            loc=loc,
            **text_kwargs,
        )

    controls._register_function(update, fig, params)
    ax.set_xlabel(
        callable_else_value_no_cast(xlabel, params, None).format(**params),
        fontdict=fontdict,
        labelpad=labelpad,
        loc=loc,
        **text_kwargs,
    )
    return controls


def interactive_ylabel(
    ylabel,
    controls=None,
    ax=None,
    *,
    fontdict=None,
    labelpad=None,
    loc=None,
    slider_formats=None,
    display_controls=True,
    play_buttons=False,
    force_ipywidgets=False,
    **kwargs,
):
    """Set a ylabel that will update interactively.

    kwargs for `matplotlib.text.Text` will be passed through, other kwargs will
    be used to create interactive controls.

    Parameters
    ----------
    ylabel : str or function
        The label text. Can include {} style formatting. e.g. 'The voltage is {volts:.2f}'
    controls : mpl_interactions.controller.Controls
        An existing controls object if you want to tie multiple plot elements to the same set of
        controls
    ax : matplotlib axis, optional
        The axis on which to plot. If none the current axis will be used.
    fontdict : dict[str]
        Passed through to the Text object. Currently not dynamically updateable. See
        https://github.com/mpl-extensions/mpl-interactions/issues/247
    labelpad : float, default: None
        Spacing in points from the axes bounding box including ticks
        and tick labels.
    loc : {'bottom', 'center', 'top'}, default: `yaxis.labellocation <matplotlib.rcParams>`
        The label position. This is a high-level alternative for passing
        parameters *y* and *horizontalalignment*.
    slider_formats : None, string, or dict
        If None a default value of decimal points will be used. Uses {} style formatting
    display_controls : boolean
        Whether the controls should display on creation. Ignored if controls is specified.
    play_buttons : bool or str or dict, optional
        Whether to attach an ipywidgets.Play widget to any sliders that get created.
        If a boolean it will apply to all kwargs, if a dictionary you choose which sliders you
        want to attach play buttons too.

        - None: no sliders
        - True: sliders on the lft
        - False: no sliders
        - 'left': sliders on the left
        - 'right': sliders on the right
    force_ipywidgets : boolean
        If True ipywidgets will always be used, even if not using the ipympl backend.
        If False the function will try to detect if it is ok to use ipywidgets
        If ipywidgets are not used the function will fall back on matplotlib widgets
    **kwargs :
        Used to create widgets to control parameters. Kwargs for Text objects will passed
        through.

    Returns
    -------
    controls
    """
    ipympl = notebook_backend() or force_ipywidgets
    fig, ax = gogogo_figure(ipympl, ax)
    slider_formats = create_slider_format_dict(slider_formats)

    kwargs, text_kwargs = kwarg_popper(kwargs, Text_kwargs_list)
    controls, params = gogogo_controls(
        kwargs, controls, display_controls, slider_formats, play_buttons
    )

    def update(params, indices, cache):
        ax.set_ylabel(
            callable_else_value_no_cast(ylabel, params, cache).format(**params),
            fontdict=fontdict,
            labelpad=labelpad,
            loc=loc,
            **text_kwargs,
        )

    controls._register_function(update, fig, params)
    ax.set_ylabel(
        callable_else_value_no_cast(ylabel, params, None).format(**params),
        fontdict=fontdict,
        labelpad=labelpad,
        loc=loc,
        **text_kwargs,
    )
    return controls


def interactive_text(
    x,
    y,
    s,
    fontdict=None,
    controls=None,
    ax=None,
    *,
    slider_formats=None,
    display_controls=True,
    play_buttons=False,
    force_ipywidgets=False,
    **kwargs,
):
    """Create a text object that will update interactively.

    kwargs for `matplotlib.text.Text` will be passed through, other kwargs will be used to create
    interactive controls.

    .. note::

        fontdict properties are currently static
        see https://github.com/mpl-extensions/mpl-interactions/issues/247


    Parameters
    ----------
    x, y : float or function
        The text position.
    s : str or function
        The text. Can either be static text, a function returning a string or
        can include {} style formatting. e.g. 'The voltage is {volts:.2f}'
    fontdict : dict[str]
        Passed through to the Text object. Currently not dynamically updateable. See
        https://github.com/mpl-extensions/mpl-interactions/issues/247
    controls : mpl_interactions.controller.Controls
        An existing controls object if you want to tie multiple plot elements to the same set of
        controls
    ax : matplotlib axis, optional
        The axis on which to plot. If none the current axis will be used.
    slider_formats : None, string, or dict
        If None a default value of decimal points will be used. Uses {} style formatting
    display_controls : boolean
        Whether the controls should display on creation. Ignored if controls is specified.
    play_buttons : bool or str or dict, optional
        Whether to attach an ipywidgets.Play widget to any sliders that get created.
        If a boolean it will apply to all kwargs, if a dictionary you choose which sliders you
        want to attach play buttons too.

        - None: no sliders
        - True: sliders on the lft
        - False: no sliders
        - 'left': sliders on the left
        - 'right': sliders on the right
    force_ipywidgets : boolean
        If True ipywidgets will always be used, even if not using the ipympl backend.
        If False the function will try to detect if it is ok to use ipywidgets
        If ipywidgets are not used the function will fall back on matplotlib widgets
    **kwargs :
        Used to create widgets to control parameters. Kwargs for Text objects will passed
        through.

    Returns
    -------
    controls
    """
    ipympl = notebook_backend() or force_ipywidgets
    fig, ax = gogogo_figure(ipympl, ax)
    slider_formats = create_slider_format_dict(slider_formats)

    kwargs, text_kwargs = kwarg_popper(kwargs, Text_kwargs_list)
    funcs, extra_ctrls, param_excluder = prep_scalars(kwargs, x=x, y=y)
    x = funcs["x"]
    y = funcs["y"]
    controls, params = gogogo_controls(
        kwargs, controls, display_controls, slider_formats, play_buttons, extra_ctrls
    )

    def update(params, indices, cache):
        x_, y_ = eval_xy(x, y, param_excluder(params, ["x", "y"]), cache)
        text.set_x(x_)
        text.set_y(y_)
        text.set_text(callable_else_value_no_cast(s, params, cache).format(**params))

    controls._register_function(update, fig, params)
    x_, y_ = eval_xy(x, y, param_excluder(params, ["x", "y"]))
    text = ax.text(
        x_,
        y_,
        callable_else_value_no_cast(s, params).format(**params),
        fontdict=fontdict,
        **text_kwargs,
    )
    return controls
