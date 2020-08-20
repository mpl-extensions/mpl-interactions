import ipywidgets as widgets
from IPython.display import display as ipy_display
from numpy import asarray, atleast_1d, arange, linspace
from matplotlib import get_backend
from functools import partial
from warnings import warn
from collections import defaultdict
from .utils import ioff, figure


# functions that are methods
__all__ = [
    'interactive_plot_factory',
    'interactive_plot',
    'interactive_hist',
]

def _kwargs_to_widget(kwargs, params, update, slider_format_strings):
    labels = []
    sliders = []
    controls = []
    for key, val in kwargs.items():
        if isinstance(val, set):
            if len(val) == 1:
                val = val.pop()
                if isinstance(val, tuple):
                    # want the categories to be ordered
                    pass
                else:
                    # fixed parameter
                    params[key] = val
            else:
                val = list(val)

            # categorical
            if len(val) <= 3:
                selector = widgets.RadioButtons(options = val)
            else:
                    selector = widgets.Select(options=val)
            params[key] = val[0]
            controls.append(selector)
            selector.observe(partial(update, key = key, label=None), names=['value'])
        elif isinstance(val, widgets.Widget) or isinstance(val, widgets.fixed):
            if not hasattr(val, 'value'):
                raise TypeError("widgets passed as parameters must have the `value` trait."
                                "But the widget passed for {key} does not have a `.value` attribute")
            if isinstance(val, widgets.fixed):
                params[key] = val.value
            else:
                params[key] = val.value
                controls.append(val)
                val.observe(partial(update, key =key, label=None), names=['value'])
        else:
            if isinstance(val, tuple) and len(val) in [2, 3]:
                # treat as an argument to linspace
                # idk if it's acceptable to overwrite kwargs like this
                # but I think at this point kwargs is just a dict like any other
                val = linspace(*val)
                kwargs[key] = val
            val = atleast_1d(val)
            if val.ndim > 1:
                raise ValueError(f'{key} is {val.ndim}D but can only be 1D or a scalar')
            if len(val)==1:
                # don't need to create a slider
                params[key] = val
            else:
                params[key] = val[0]
                labels.append( widgets.Label(value=slider_format_strings[key].format(val[0])))
                sliders.append(widgets.IntSlider(min=0, max=val.size-1, readout=False, description = key))
                controls.append(widgets.HBox([sliders[-1], labels[-1]]))
                sliders[-1].observe(partial(update, key=key, label=labels[-1]), names=['value'])
    return sliders, labels, controls

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
    if isinstance(slider_format_string, str):
        slider_format_strings = defaultdict(lambda: slider_format_string)
    elif isinstance(slider_format_string, dict):
        slider_format_strings = defaultdict(lambda: '{:.1f}')
        for key, val in slider_format_string.items():
            slider_format_strings[key] = val
    else:
        raise ValueError(f'slider_format_string must be a dict or a string but it is a {type(slider_format_string)}')

    def update(change, key, label):
        if label:
            #continuous
            params[key] = kwargs[key][change['new']]
            label.value = slider_format_strings[key].format(kwargs[key][change['new']])
        else:
            # categorical
            params[key] = change['new']
        
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
    sliders, labels, controls = _kwargs_to_widget(kwargs, params, update, slider_format_strings)
    # for key, val in kwargs.items():
    #     _kwarg_to_widget(key, val, params, sliders, labels, controls, update, slider_format_strings)
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
        plot_kwargs = [{}] * len(funcs)
    else:
        plot_kwargs = atleast_1d(plot_kwargs)
        if not len(plot_kwargs) == len(funcs):
            raise ValueError('If using multiple functions'
                            ' then plot_kwargs must be a list'
                            ' of the same length or None.')
    
    # make sure plot labels make sense
    for i, (pk, f) in enumerate(zip(plot_kwargs, funcs)):
        if pk is None:
            pk = {}
            plot_kwargs[i] = pk
        if 'label' not in pk:
            pk['label'] = f.__name__



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
    if title is not None:
        ax.set_title(title.format(**params))

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
    slider_format_string : string | dictionary
        A valid format string, this will be used to render the current value of the parameter.
        To control on a per slider basis pass a dictionary of format strings with the parameter
        names as the keys.
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

    With numpy arrays::

        x = np.linspac(0,2*np.pi)
        tau = np.linspace(0, np.pi)
        def f(x, tau):
            return np.sin(x+tau)
        interactive_plot(f, x=x, tau=tau)

    with tuples::

        x = np.linspac(0,2*np.pi)
        def f(x, tau):
            return np.sin(x+tau)
        interactive_plot(f, x=x, tau=(0, np.pi, 1000))

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


import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection

def simple_hist(arr, bins='auto', density=None, weights=None):
    heights, bins = np.histogram(arr, bins=bins,  density=density,weights=weights)
    width = bins[1]-bins[0]
    new_patches = []
    for i in range(len(heights)):
        new_patches.append(Rectangle((bins[i],0), width=width, height=heights[i]))
    xlims = (bins.min(), bins.max())
    ylims = (0, heights.max()*1.05)
    
    return xlims, ylims, new_patches
    
def stretch(ax, xlims, ylims):
    cur_xlims = ax.get_xlim()
    cur_ylims = ax.get_ylim()
    new_lims = ylims
    new_lims = [
        new_lims[0] if new_lims[0]<cur_ylims[0] else cur_ylims[0],
        new_lims[1] if new_lims[1]>cur_ylims[1] else cur_ylims[1]
        ]
    ax.set_ylim(new_lims)
    new_lims = xlims
    new_lims = [
        new_lims[0] if new_lims[0]<cur_xlims[0] else cur_xlims[0],
        new_lims[1] if new_lims[1]>cur_xlims[1] else cur_xlims[1]
        ]
    ax.set_xlim(new_lims)

def interactive_hist(f, density=False, bins='auto', weights=None, slider_format_string='{:.2f}',  **kwargs):

    params = {}
    funcs = atleast_1d(f)
    # supporting more would require more thought
    if len(funcs) != 1:
        raise ValueError(f"Currently only a single function is supported. You passed in {len(funcs)} functions")
    if isinstance(slider_format_string, str):
        slider_format_strings = defaultdict(lambda: slider_format_string)
    elif isinstance(slider_format_string, dict):
        slider_format_strings = defaultdict(lambda: '{:.1f}')
        for key, val in slider_format_string.items():
            slider_format_strings[key] = val
    else:
        raise ValueError(f'slider_format_string must be a dict or a string but it is a {type(slider_format_string)}')

    with ioff:
        fig = figure()
        ax = fig.gca()
    pc = PatchCollection([])
    ax.add_collection(pc, autolim=True)

        # update plot
    def update(change, key, label):
        if label:
            #continuous
            params[key] = kwargs[key][change['new']]
            label.value = slider_format_strings[key].format(kwargs[key][change['new']])
        else:
            # categorical
            params[key] = change['new']
        arr = funcs[0](**params)
        new_x, new_y, new_patches = simple_hist(arr, density=density, bins=bins, weights=weights)
        stretch(ax, new_x, new_y)
        pc.set_paths(new_patches)
        ax.autoscale_view()
        fig.canvas.draw() # same effect with draw_idle

    # this line implicitly fills the params dict
    sliders, labels, controls = _kwargs_to_widget(kwargs, params, update, slider_format_strings)

    new_x, new_y, new_patches = simple_hist(funcs[0](**params), density=density, bins=bins, weights=weights)
    pc.set_paths(new_patches)
    stretch(ax, new_x, new_y)

    display(widgets.VBox(controls))
    display(fig.canvas)