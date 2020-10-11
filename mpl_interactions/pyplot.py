from collections.abc import Callable, Iterable
from functools import partial
from numbers import Number

import numpy as np
from matplotlib.cbook.deprecation import deprecated
from matplotlib.collections import PatchCollection
from matplotlib.colors import to_rgba_array
from matplotlib.patches import Rectangle
from matplotlib.pyplot import sca, sci

from .controller import Controls, gogogo_controls

from .helpers import (
    broadcast_many,
    callable_else_value,
    callable_else_value_no_cast,
    eval_xy,
    create_slider_format_dict,
    gogogo_display,
    gogogo_figure,
    kwarg_to_ipywidget,
    kwarg_to_mpl_widget,
    notebook_backend,
    update_datalim_from_bbox,
)

# functions that are methods
__all__ = [
    "interactive_plot",
    "interactive_hist",
    "interactive_scatter",
    "interactive_imshow",
    "interactive_axhline",
    "interactive_axvline",
]


def interactive_plot(
    *args,
    parametric=False,
    multiline=False,
    ax=None,
    slider_formats=None,
    title=None,
    xlim="stretch",
    ylim="stretch",
    force_ipywidgets=False,
    play_buttons=False,
    play_button_pos="right",
    controls=None,
    display_controls=True,
    **kwargs,
):
    """
    Control a plot using widgets

    interactive_plot([x], y, [fmt])

    where x/y is are either arraylike or a function that returns arrays. Any kwargs accepted by
    matplotlib.pyplot.plot will be passed through, other kwargs will be intrepreted as controls

    parameters
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
        If True then the function expects to have only received a value for y and that that function will
        return an array for both x and y, or will return an array with shape (N, 2)
    ax : matplotlib axis, optional
        The axis on which to plot. If none the current axis will be used.
    slider_formats : None, string, or dict
        If None a default value of decimal points will be used. Uses the new {} style formatting
    title : None or string
        If a string then you can have it update automatically using string formatting of the names
        of the parameters. i.e. to include the current value of tau: title='the value of tau is: {tau:.2f}'
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
    play_buttons : bool or dict, optional
        Whether to attach an ipywidgets.Play widget to any sliders that get created.
        If a boolean it will apply to all kwargs, if a dictionary you choose which sliders you
        want to attach play buttons too.
    play_button_pos : str, or dict, or list(str)
        'left' or 'right'. Whether to position the play widget(s) to the left or right of the slider(s)
    controls : mpl_interactions.controller.Controls
        An existing controls object if you want to tie multiple plot elements to the same set of
        controls
    display_controls : boolean
        Whether the controls should display themselve on creation. Ignored if controls is specified.

    returns
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
    # this is a list of options to Line2D partially taken from
    # https://github.com/matplotlib/matplotlib/blob/f9d29189507cfe4121a231f6ab63539d216c37bd/lib/matplotlib/lines.py#L271
    # many of these can also be made into functions
    plot_kwargs_list = [
        "alpha",
        "linewidth",
        "linestyle",
        "color",
        "marker",
        "markersize",
        "markeredgewidth",
        "markeredgecolor",
        "markerfacecolor",
        "markerfacecoloralt",
        "fillstyle",
        "antialiased",
        "dash_capstyle",
        "solid_capstyle",
        "dash_joinstyle",
        "solid_joinstyle",
        "pickradius",
        "drawstyle",
        "markevery",
        "label",
    ]
    plot_kwargs = {}
    for k in plot_kwargs_list:
        if k in kwargs:
            plot_kwargs[k] = kwargs.pop(k)
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

    ipympl = notebook_backend()
    use_ipywidgets = ipympl or force_ipywidgets
    fig, ax = gogogo_figure(ipympl, ax=ax)
    slider_formats = create_slider_format_dict(slider_formats)
    controls, params = gogogo_controls(
        kwargs, controls, display_controls, slider_formats, play_buttons, play_button_pos
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
        if title is not None:
            ax.set_title(title.format(**params))

    controls.register_function(update, fig, params.keys())

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
    if title is not None:
        ax.set_title(title.format(**params))

    # make sure the home button will work
    if hasattr(fig.canvas, "toolbar") and fig.canvas.toolbar is not None:
        fig.canvas.toolbar.push_current()
    # set current axis to be pyplot-like
    sca(ax)

    return controls


def simple_hist(arr, bins="auto", density=None, weights=None):
    heights, bins = np.histogram(arr, bins=bins, density=density, weights=weights)
    width = bins[1] - bins[0]
    new_patches = []
    for i in range(len(heights)):
        new_patches.append(Rectangle((bins[i], 0), width=width, height=heights[i]))
    xlims = (bins.min(), bins.max())
    ylims = (0, heights.max() * 1.05)

    return xlims, ylims, new_patches


def stretch(ax, xlims, ylims):
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
    title=None,
    force_ipywidgets=False,
    play_buttons=False,
    play_button_pos="right",
    controls=None,
    display_controls=True,
    **kwargs,
):
    """
    Control the contents of a histogram using widgets.

    See https://github.com/ianhi/mpl-interactions/pull/73#issue-470638134 for a discussion
    of the limitations of this function. These limitations will be improved once
    https://github.com/matplotlib/matplotlib/pull/18275 has been merged.

    parameters
    ----------
    arr : arraylike or function
        The array or the funciton that returns an array that is to be histogrammed
    density : bool, optional
        whether to plot as a probability density. Passed to np.histogram
    bins : int or sequence of scalars or str, optional
        bins argument to np.histogram
    weights : array_like, optional
        passed to np.histogram
    ax : matplotlib axis, optional
        The axis on which to plot. If none the current axis will be used.
    slider_formats : None, string, or dict
        If None a default value of decimal points will be used. Uses the new {} style formatting
    title : None or string
        If a string then you can have it update automatically using string formatting of the names
        of the parameters. i.e. to include the current value of tau: title='the value of tau is: {tau:.2f}'
    force_ipywidgets : boolean
        If True ipywidgets will always be used, even if not using the ipympl backend.
        If False the function will try to detect if it is ok to use ipywidgets
        If ipywidgets are not used the function will fall back on matplotlib widgets
    play_buttons : bool or dict, optional
        Whether to attach an ipywidgets.Play widget to any sliders that get created.
        If a boolean it will apply to all kwargs, if a dictionary you choose which sliders you
        want to attach play buttons too.
    play_button_pos : str, or dict, or list(str)
        'left' or 'right'. Whether to position the play widget(s) to the left or right of the slider(s)
    controls : mpl_interactions.controller.Controls
        An existing controls object if you want to tie multiple plot elements to the same set of
        controls
    display_controls : boolean
        Whether the controls should display themselve on creation. Ignored if controls is specified.

    returns
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

    ipympl = notebook_backend()
    fig, ax = gogogo_figure(ipympl, ax=ax)
    use_ipywidgets = ipympl or force_ipywidgets
    slider_formats = create_slider_format_dict(slider_formats)
    controls, params = gogogo_controls(
        kwargs, controls, display_controls, slider_formats, play_buttons, play_button_pos
    )
    pc = PatchCollection([])
    ax.add_collection(pc, autolim=True)

    def update(params, indices, cache):
        if title is not None:
            ax.set_title(title.format(**params))
        arr_ = callable_else_value(arr, params, cache)
        new_x, new_y, new_patches = simple_hist(arr_, density=density, bins=bins, weights=weights)
        stretch(ax, new_x, new_y)
        pc.set_paths(new_patches)
        ax.autoscale_view()

    controls.register_function(update, fig, params.keys())

    new_x, new_y, new_patches = simple_hist(
        callable_else_value(arr, params), density=density, bins=bins, weights=weights
    )
    sca(ax)
    pc.set_paths(new_patches)
    ax.set_xlim(new_x)
    ax.set_ylim(new_y)
    if title is not None:
        ax.set_title(title.format(**params))

    return controls


def interactive_scatter(
    x,
    y=None,
    s=None,
    c=None,
    cmap=None,
    vmin=None,
    vmax=None,
    alpha=None,
    edgecolors=None,
    label=None,
    parametric=False,
    ax=None,
    slider_formats=None,
    title=None,
    xlim="stretch",
    ylim="stretch",
    force_ipywidgets=False,
    play_buttons=False,
    play_button_pos="right",
    controls=None,
    display_controls=True,
    **kwargs,
):
    """
    Control a scatter plot using widgets.

    parameters
    ----------
    x, y : function or float or array-like
        shape (n, ) for array-like. Functions must return the correct shape as well. If y is None
        then parametric must be True and the function for x must return x, y
    c : array-like or list of colors or color, broadcastable
        Must be broadcastable to x,y and any other plotting kwargs.
        valid input to plt.scatter, or an array of valid inputs, or a function
        or an array-like of functions of the same length as f
    s : float or array-like or function, broadcastable
        valid input to plt.scatter, or an array of valid inputs, or a function
        or an array-like of functions of the same length as f
    alpha : float, None, or function(s), broadcastable
        Affects all scatter points. This will compound with any alpha introduced by
        the ``c`` argument
    edgecolors : colorlike, broadcastable
        passed through to scatter.
    label : string(s) broadcastable
        labels for the functions being plotted.
    parametric : boolean
        If True then the function expects to have only received a value for y and that that function will
        return an array for both x and y, or will return an array with shape (N, 2)
    ax : matplotlib axis, optional
        The axis on which to plot. If none the current axis will be used.
    slider_formats : None, string, or dict
        If None a default value of decimal points will be used. Uses the new {} style formatting
    title : None or string
        If a string then you can have it update automatically using string formatting of the names
        of the parameters. i.e. to include the current value of tau: title='the value of tau is: {tau:.2f}'
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
    play_buttons : bool or dict or list(str), optional
        Whether to attach an ipywidgets.Play widget to any sliders that get created.
        If a boolean it will apply to all kwargs, if a dictionary you choose which sliders you
        want to attach play buttons too. If a list of strings use the names of the parameters that
        you want to have sliders
    play_button_pos : str, or dict, or list(str)
        'left' or 'right'. Whether to position the play widget(s) to the left or right of the slider(s)
    controls : mpl_interactions.controller.Controls
        An existing controls object if you want to tie multiple plot elements to the same set of
        controls
    display_controls : boolean
        Whether the controls should display themselve on creation. Ignored if controls is specified.

    returns
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

    ipympl = notebook_backend()
    fig, ax = gogogo_figure(ipympl, ax)
    use_ipywidgets = ipympl or force_ipywidgets
    slider_formats = create_slider_format_dict(slider_formats)
    controls, params = gogogo_controls(
        kwargs, controls, display_controls, slider_formats, play_buttons, play_button_pos
    )

    def update(params, indices, cache):
        if title is not None:
            ax.set_title(title.format(**params))

        if parametric:
            out = callable_else_value_no_cast(x, params)
            if not isinstance(out, tuple):
                out = np.asanyarray(out).T
            x_, y_ = out
        else:
            x_, y_ = eval_xy(x, y, params, cache)
        scatter.set_offsets(np.column_stack([x_, y_]))
        c_ = check_callable_xy(c, x_, y_, params, cache)
        s_ = check_callable_xy(s, x_, y_, params, cache)
        ec_ = check_callable_xy(edgecolors, x_, y_, params, cache)
        a_ = check_callable_alpha(alpha, params, cache)
        if c_ is not None:
            try:
                c_ = to_rgba_array(c_)
            except ValueError as array_err:
                try:
                    c_ = scatter.cmap(c_)
                except TypeError as cmap_err:
                    raise ValueError(
                        "If c is a function it must return either an RGB(A) array"
                        "or a 1D array of valid color names or values to be colormapped"
                    )
            scatter.set_facecolor(c_)
        if ec_ is not None:
            scatter.set_edgecolor(ec_)
        if s_ is not None and not isinstance(s_, Number):
            scatter.set_sizes(s_)
        if a_ is not None:
            scatter.set_alpha(a_)

        update_datalim_from_bbox(
            ax, scatter.get_datalim(ax.transData), stretch_x=stretch_x, stretch_y=stretch_y
        )
        ax.autoscale_view()

    controls.register_function(update, fig, params.keys())
    if title is not None:
        ax.set_title(title.format(**params))

    def check_callable_xy(arg, x, y, params, cache):
        if isinstance(arg, Callable):
            if arg not in cache:
                cache[arg] = arg(x, y, **params)
            return cache[arg]
        else:
            return arg

    def check_callable_alpha(alpha_, params, cache):
        if isinstance(alpha_, Callable):
            if not alpha_ in cache:
                cache[alpha_] = alpha_(**params)
            return cache[alpha_]
        else:
            return alpha_

    if parametric:
        out = callable_else_value_no_cast(x, params)
        if not isinstance(out, tuple):
            out = np.asanyarray(out).T
        x_, y_ = out
    else:
        x_, y_ = eval_xy(x, y, params)
    c_ = check_callable_xy(c, x_, y_, params, {})
    s_ = check_callable_xy(s, x_, y_, params, {})
    ec_ = check_callable_xy(edgecolors, x_, y_, params, {})
    a_ = check_callable_alpha(alpha, params, {})
    scatter = ax.scatter(
        x_,
        y_,
        c=c_,
        s=s_,
        vmin=vmin,
        vmax=vmax,
        cmap=cmap,
        alpha=a_,
        edgecolors=ec_,
        label=label,
    )
    # this is necessary to make calls to plt.colorbar behave as expected
    sca(ax)
    sci(scatter)

    if title is not None:
        ax.set_title(title.format(**params))

    return controls


# portions of this docstring were copied directly from the docsting
# of `matplotlib.pyplot.imshow`
def interactive_imshow(
    X,
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
    controls=None,
    display_controls=True,
    **kwargs,
):
    """
    Control an image using widgets.

    parameters
    ----------
    X : function or image like
        If a function it must return an image-like object. See matplotlib.pyplot.imshow for the
        full set of valid options.
    cmap : str or `~matplotlib.colors.Colormap`
        The Colormap instance or registered colormap name used to map
        scalar data to colors. This parameter is ignored for RGB(A) data.
        forwarded to matplotlib
    norm : `~matplotlib.colors.Normalize`, optional
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
        The axis on which to plot. If none the current axis will be used.
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
    play_button_pos : str, or dict, or list(str)
        'left' or 'right'. Whether to position the play widget(s) to the left or right of the slider(s)

    returns
    -------
    controls
    """
    ipympl = notebook_backend()
    fig, ax = gogogo_figure(ipympl, ax)
    use_ipywidgets = ipympl or force_ipywidgets
    slider_formats = create_slider_format_dict(slider_formats)

    controls, params = gogogo_controls(
        kwargs, controls, display_controls, slider_formats, play_buttons, play_button_pos
    )

    def update(params, indices, cache):
        if title is not None:
            ax.set_title(title.format(**params))

        if isinstance(X, Callable):
            # check this here to avoid setting the data if we don't need to
            # use the callable_else_value fxn to make use of easy caching
            new_data = callable_else_value(X, params, cache)
            im.set_data(new_data)
            if autoscale_cmap and (new_data.ndim != 3) and vmin is None and vmax is None:
                im.norm.autoscale(new_data)
        # caching for these?
        if isinstance(vmin, Callable):
            im.norm.vmin = vmin(**params)
        if isinstance(vmax, Callable):
            im.norm.vmax = vmax(**params)

    controls.register_function(update, fig, params.keys())

    # make it once here so we can use the dims in update
    new_data = callable_else_value(X, params)
    sca(ax)
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


def interactive_axhline(
    y=0,
    xmin=0,
    xmax=1,
    ax=None,
    slider_formats=None,
    title=None,
    force_ipywidgets=False,
    play_buttons=False,
    play_button_pos="right",
    controls=None,
    display_controls=True,
    **kwargs,
):
    """
    Control an horizontal line using widgets.

    parameters
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
    play_buttons : bool or dict, optional
        Whether to attach an ipywidgets.Play widget to any sliders that get created.
        If a boolean it will apply to all kwargs, if a dictionary you choose which sliders you
        want to attach play buttons too.
    play_button_pos : str, or dict, or list(str)
        'left' or 'right'. Whether to position the play widget(s) to the left or right of the slider(s)
    controls : mpl_interactions.controller.Controls
        An existing controls object if you want to tie multiple plot elements to the same set of
        controls
    display_controls : boolean
        Whether the controls should display themselve on creation. Ignored if controls is specified.

    returns
    -------
    controls
    """
    ipympl = notebook_backend()
    fig, ax = gogogo_figure(ipympl, ax)
    use_ipywidgets = ipympl or force_ipywidgets
    slider_formats = create_slider_format_dict(slider_formats)

    controls, params = gogogo_controls(
        kwargs, controls, display_controls, slider_formats, play_buttons, play_button_pos
    )

    def update(params, indices, cache):
        if title is not None:
            ax.set_title(title.format(**params))
        y_ = callable_else_value(y, params, cache).item()
        line.set_ydata([y_, y_])
        xmin_ = callable_else_value(xmin, params, cache).item()
        xmax_ = callable_else_value(xmax, params, cache).item()
        line.set_xdata([xmin_, xmax_])
        # TODO consider updating just the ydatalim here

    controls.register_function(update, fig, params)
    sca(ax)
    line = ax.axhline(
        callable_else_value(y, params).item(),
        callable_else_value(xmin, params).item(),
        callable_else_value(xmax, params).item(),
    )
    return controls


def interactive_axvline(
    x=0,
    ymin=0,
    ymax=1,
    ax=None,
    slider_formats=None,
    title=None,
    force_ipywidgets=False,
    play_buttons=False,
    play_button_pos="right",
    controls=None,
    display_controls=True,
    **kwargs,
):
    """
    Control a vertical line using widgets.

    parameters
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
    play_buttons : bool or dict, optional
        Whether to attach an ipywidgets.Play widget to any sliders that get created.
        If a boolean it will apply to all kwargs, if a dictionary you choose which sliders you
        want to attach play buttons too.
    play_button_pos : str, or dict, or list(str)
        'left' or 'right'. Whether to position the play widget(s) to the left or right of the slider(s)
    controls : mpl_interactions.controller.Controls
        An existing controls object if you want to tie multiple plot elements to the same set of
        controls
    display_controls : boolean
        Whether the controls should display themselve on creation. Ignored if controls is specified.

    returns
    -------
    controls
    """
    ipympl = notebook_backend()
    fig, ax = gogogo_figure(ipympl, ax)
    use_ipywidgets = ipympl or force_ipywidgets
    slider_formats = create_slider_format_dict(slider_formats)

    controls, params = gogogo_controls(
        kwargs, controls, display_controls, slider_formats, play_buttons, play_button_pos
    )

    def update(params, indices, cache):
        if title is not None:
            ax.set_title(title.format(**params))
        x_ = callable_else_value(x, params, cache).item()
        line.set_ydata([x_, x_])
        ymin_ = callable_else_value(ymin, params, cache).item()
        ymax_ = callable_else_value(ymax, params, cache).item()
        line.set_xdata([ymin_, ymax_])
        # TODO consider updating just the ydatalim here

    controls.register_function(update, fig, params)
    sca(ax)
    line = ax.axvline(
        callable_else_value(x, params).item(),
        callable_else_value(ymin, params).item(),
        callable_else_value(ymax, params).item(),
    )
    return controls
