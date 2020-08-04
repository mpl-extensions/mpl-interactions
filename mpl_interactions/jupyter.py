import ipywidgets as widgets
from IPython.display import display as ipy_display
from numpy import asarray, atleast_1d, arange
from matplotlib import get_backend
from functools import partial
from warnings import warn
from .utils import ioff, figure


# functions that are methods
__all__ = [
    'interactive_plot_factory',
    'interactive_plot',
]


def interactive_plot_factory(ax, f, x=None,
                                 x_scale='stretch',
                                 y_scale='stretch',
                                 slider_format_string='{:.1f}',
                                 plot_kwargs=None,
                                 title=None, **kwargs):
    """
    Use this function for maximum control over layout of the widgets
    
    ax : matplotlib axes
    f : function or iterable of functions
    """
    params = {}
    funcs = atleast_1d(f)

    def update(change, key, label):
        params[key] = kwargs[key][change['new']]
        label.value = slider_format_string.format(kwargs[key][change['new']])
        
        # update plot
        for i,f in enumerate(funcs):
            if x is not None and not indexed_x:
                lines[i].set_data(x, f(x, **params))
            elif indexed_x:
                lines[i].set_data(x, f(**params))
            else:
                lines[i].set_data(*f(**params))

        cur_xlims = ax.get_xlim()
        cur_ylims = ax.get_ylim()
        ax.relim() # this may be expensive? don't do if not necessary?
        if y_scale=='auto':
            ax.autoscale_view(scalex=False)
        elif y_scale=='stretch':
            new_lims = [ax.dataLim.y0, ax.dataLim.y0+ax.dataLim.height]
            new_lims = [
                new_lims[0] if new_lims[0]<cur_ylims[0] else cur_ylims[0],
                new_lims[1] if new_lims[1]>cur_ylims[1] else cur_ylims[1]
                ]
            ax.set_ylim(new_lims)
        if x_scale=='auto':
            ax.autoscale_view(scaley=False)
        elif x_scale=='stretch':
            new_lims = [ax.dataLim.x0, ax.dataLim.x0+ax.dataLim.width]
            new_lims = [
                new_lims[0] if new_lims[0]<cur_xlims[0] else cur_xlims[0],
                new_lims[1] if new_lims[1]>cur_xlims[1] else cur_xlims[1]
                ]
            ax.set_xlim(new_lims)
        if title is not None:
            ax.set_title(title.format(**params))
        fig.canvas.draw_idle()
    fig = ax.get_figure()
    labels = []
    sliders = []
    controls = []
    for key, val in kwargs.items():
        val = atleast_1d(val)
        if val.ndim > 1:
            raise ValueError(f'{key} is {val.ndim}D but can only be 1D or a scalar')
        if len(val)==1:
            # don't need to create a slider
            fixed_params[key] = val
            params[key] = val
        else:
            params[key] = val[0]
            labels.append( widgets.Label(value=f'{val[0]}'))
            sliders.append(widgets.IntSlider(min=0, max=val.size-1, readout=False, description = key))
            controls.append(widgets.HBox([sliders[-1], labels[-1]]))
            sliders[-1].observe(partial(update, key=key, label=labels[-1]), names=['value'])
    indexed_x = False
    if x is not None:
        x = asarray(x)
        if x.ndim != 1:
            raise ValueError(f'x must be None or be 1D but is {x.ndim}D')
    else:
        # call f once to determine it returns x
        out = asarray(f(**params))
        if len(out.shape) != 2 or (len(out.shape)==2 and out.shape[0]==1):
            # probably should use arange to set the x values
            indexed_x = True
            x = arange(out.size)


    if plot_kwargs is None:
        plot_kwargs = []
        for f in funcs:
            plot_kwargs.append({'label':f.__name__})
    else:
        plot_kwargs = atleast_1d(plot_kwargs)
        assert len(plot_kwargs) == len(funcs)

    lines = []
    for i,f in enumerate(funcs):

        if x is not None and not indexed_x:
            lines.append(ax.plot(x, f(x, **params), **plot_kwargs[i])[0])
        elif indexed_x:
            lines.append(ax.plot(x, f(**params), **plot_kwargs[i])[0])
        else:
            lines.append(ax.plot(*f(**params), **plot_kwargs[i])[0])
    if not isinstance(x_scale,str):
        ax.set_ylim(x_scale)
    if not isinstance(y_scale,str):
        ax.set_ylim(y_scale)
    # make sure the home button will work
    fig.canvas.toolbar.push_current()
    return controls

def interactive_plot(f, x=None, x_scale='stretch', y_scale='stretch',
                        slider_format_string='{:.1f}',
                        plot_kwargs=None,
                        title=None,figsize=None, display=True, **kwargs):
    """
    Make a plot interactive using sliders. just pass the keyword arguments of the function
    you want to plot to this function like so:
    
    parameters
    ----------
    x : arraylike or None
        x values a which to evaluate the function. If None the function(s) f should
        return a list of [x, y]
    ax : matplolibt.Axes or None
        axes on which to 
    x_scale : string or tuple of floats, optional
        If a tuple it will be passed to ax.set_xlim. Other options are:
        'auto': rescale the x axis for every redraw
        'stretch': only ever expand the xlims.
    y_scale : string or tuple of floats, optional
        If a tuple it will be passed to ax.set_ylim. Other options are same
        as x_scale
    slider_format_string : string
        A valid format string, this will be used to render
        the current value of the parameter
    plot_kwargs : None, dict, or iterable of dicts
        Keyword arguments to pass to plot. If using multiple f's then plot_kwargs must be either
        None or be iterable.
    title : None or string
        If a string then you can have it update automatically using string formatting of the names
        of the parameters. i.e. to include the current value of tau: title='the value of tau is: {tau}'
    figsize : tuple or scalar
        If tuple it will be used as the matplotlib figsize. If a number
        then it will be used to scale the current rcParams figsize
    display : boolean
        If True then the output and controls will be automatically displayed

    returns
    -------
    fig : matplotlib figure
    ax : matplotlib axis
    controls : list of slider widgets

    Examples 
    --------
    tau = np.linspace()
    def f(x, tau):
        return np.sin(x*tau)
    interactive_plot(f, tau=tau)
    """
                                 
    backend = get_backend().lower()
    if 'ipympl' in backend:
        ipympl = True
        with ioff:
            fig = figure()
            ax = fig.gca()
    else:
        ipympl = False
        if backend == 'nbAgg'.lower():
            warn('You are using an outdated backend. You should use %matplotlib ipympl instead of %matplotlib notebook')
        fig = figure()
        ax = fig.gca()
    controls = widgets.VBox(interactive_plot_factory(ax, f, x, x_scale,
                                        y_scale, slider_format_string,
                                        plot_kwargs, title, **kwargs))
    if display:
        if ipympl:
            ipy_display(widgets.VBox([controls, fig.canvas]))
        else:
            ipy_display(controls)
    return fig, ax, controls
