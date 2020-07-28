import ipywidgets as widgets
from IPython.display import display as ipy_display
from numpy import asarray, abs, argmin, min, max, swapaxes, atleast_1d
from matplotlib.pyplot import figure as mpl_figure
from matplotlib.pyplot import ioff, ion, rcParams
from matplotlib import is_interactive
from collections.abc import Iterable
from functools import partial


# functions that are methods
__all__ = [
    'interactive_plot_factory',
    'interactive_plot',
    'figure',
    'nearest_idx',
    'heatmap_slicer'
]


def interactive_plot_factory(ax, f, x=None,
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
            if x is not None:
                lines[i].set_data(x, f(x, **params))
            else:
                lines[i].set_data(*f(**params))
        cur_lims = ax.get_ylim()
        if y_scale=='auto':
            ax.relim()
            ax.autoscale_view()
        elif y_scale=='stretch':
            ax.relim()
            new_lims = [ax.dataLim.y0, ax.dataLim.y0+ax.dataLim.height]
            new_lims = [
                new_lims[0] if new_lims[0]<cur_lims[0] else cur_lims[0],
                new_lims[1] if new_lims[1]>cur_lims[1] else cur_lims[1]
                ]
            ax.set_ylim(new_lims)
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
    if x is not None:
        x = asarray(x)
        if x.ndim != 1:
            raise ValueError(f'x must be None or be 1D but is {x.ndim}D')

    if plot_kwargs is None:
        plot_kwargs = []
        for f in funcs:
            plot_kwargs.append({'label':f.__name__})
    else:
        plot_kwargs = atleast_1d(plot_kwargs)
        assert len(plot_kwargs) == len(funcs)

    lines = []
    for i,f in enumerate(funcs):

        if x is not None:
            lines.append(ax.plot(x,f(x, **params), **plot_kwargs[i])[0])
        else:
            lines.append(ax.plot(*f(**params), **plot_kwargs[i])[0])
    if not isinstance(y_scale,str):
        ax.set_ylim(y_scale)
    # make sure the home button will work
    fig.canvas.toolbar.push_current()
    



    return controls

def interactive_plot(f, x=None, y_scale='stretch',
                        slider_format_string='{:.1f}',
                        plot_kwargs=None,
                        title=None,figsize=None, display=True, **kwargs):
    """
    Make a plot interactive using sliders. just pass the keyword arguments of the function
    you want to plot to this function like so:
    
    ```
    tau = np.linspace()
    def f(x, tau):
        return np.sin(x*tau)
    interactive_plot(f, tau=tau)
    ```

    parameters
    ----------
    x : arraylike or None
        x values a which to evaluate the function. If None the function(s) f should
        return a list of [x, y]
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
        None or be iterable.
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
    """
                                 
    was_interactive = False
    if is_interactive():
        was_interactive = True
        ioff()
    fig = figure()
    ax = fig.gca()
    if was_interactive:
        ion()
    controls = widgets.VBox(interactive_plot_factory(ax, f, x,
                                        y_scale, slider_format_string,
                                        plot_kwargs, title, **kwargs))
    if display:
        ipy_display(widgets.VBox([controls, fig.canvas]))
    return fig, ax, controls


def figure(figsize=1,*args,**kwargs):
    if not isinstance(figsize,Iterable):
        figsize = [figsize*x for x in rcParams['figure.figsize']]
    return mpl_figure(figsize=figsize,*args,**kwargs)

def nearest_idx(array,value,axis=None):
    """
    Return the index of the array that is closest to value. Equivalent to
    `np.argmin(np.abs(array-value))`
    
    Parameters
    ----------
    array : arraylike
    value : Scalar
    axis  : int, optional
        From np.argmin: "By default, the index is into the flattened array, otherwise
        along the specified axis."

    Returns
    -------
    idx : IndexArray
        index of array that most closely matches value. If axis=None this will be an integer
    """
    array = asarray(array)
    return argmin(abs(array-value),axis=axis)

def heatmap_slicer(X,Y,heatmaps, slices='horizontal',heatmap_names = None,max_cols=None,figsize=(18,9),linecolor='k',labels=('X','Y'),interaction_type='move'):
    
    """
    Parameters
    ----------
    X,Y : 1D array
    heatmaps : array_like
       must be 2-D or 3-D. If 3-D the last two axes should be (X,Y) 
    heatmap_names : (String, String, ...)
        An iterable with the names of the heatmaps. If provided it must have as many names as there are heatmaps
    slice : {'horizontal', 'vertical', 'both'}
        Direction to draw slice on heatmap. both will draw horizontal and vertical traces on the same
        plot, while both_separate will make a line plot for each.
    max_cols : int, optional - not working yet :(
        Maximum number of columns to allo    x : arraylike or None
        x values a which to evaluate the function. If None the function(s) f should
        return a list of [x, y]
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

    Returns
    -------
    fig : matplotlib figure
    ax  : tuple of axes
    """
    horiz = vert = False
    if slices == 'both':
        num_line_axes = 2
        horiz_axis = -2
        vert_axis = -1
        horiz = vert = True
    else:
        horiz_axis = -1
        vert_axis = -1
        num_line_axes = 1
        if slices =='horizontal':
            horiz = True
        elif slices =='vertical':
            vert = True
        else:
            raise ValueError('Valid options for slices are {horizontal, vertical, both}')


    heatmaps = asarray(heatmaps)
    if heatmap_names is None:
        heatmap_names = [f'heatmap_{i}' for i in range(heatmaps.shape[0])]

    if heatmaps.ndim == 3:
        num_axes = num_line_axes + heatmaps.shape[0]
        if type(heatmap_names) is str or (len(heatmap_names) != heatmaps.shape[0]):
            raise ValueError('need to provide at least as many heatmap_names as heatmaps')
    elif heatmaps.ndim == 2:
        heatmaps = heatmaps.reshape(1,*heatmaps.shape)
        if type(heatmap_names) is str:
            heatmap_names = [heatmap_names]
        num_axes = num_line_axes + 1
    else:
        raise ValueError(f"heatmaps must be 2D or 3D but is {heatmaps.ndim}D")


    fig, axes = plt.subplots(1,num_axes,figsize=figsize)
    hlines = []
    vlines = []
    init_idx = 0
    axes[0].set_ylabel(labels[1])
    for i,ax in enumerate(axes[:-num_line_axes]):
        ax.pcolormesh(X,Y,heatmaps[i])
        ax.set_xlabel(labels[0])
        ax.set_title(heatmap_names[i])
        if i>0:
            ax.set_yticklabels([])

        if horiz:
            data_line = axes[horiz_axis].plot(X,heatmaps[i,init_idx,:],label=f"{heatmap_names[i]}")[0]
            hlines.append((ax.axhline(Y[init_idx],color=linecolor),data_line))
        if vert:
            data_line = axes[vert_axis].plot(Y,heatmaps[i,:,init_idx],label=f"{heatmap_names[i]}")[0]
            vlines.append((ax.axvline(X[init_idx],color=linecolor),data_line))

    minimum = min(heatmaps)
    maximum = max(heatmaps)
    if vert:
        axes[vert_axis].set_title('Vertical')
        axes[vert_axis].set_ylim([minimum,maximum])
        axes[vert_axis].legend()
    if horiz:
        axes[horiz_axis].set_title('Horizontal')
        axes[horiz_axis].set_ylim([minimum,maximum])
        axes[horiz_axis].legend()

    def update_lines(event):
        if event.inaxes is not None:
            for i,lines in enumerate(hlines):
                y_idx = nearest_idx(Y,event.ydata)
                lines[0].set_ydata(Y[y_idx])
                lines[1].set_ydata(heatmaps[i,y_idx,:])
            for i,lines in enumerate(vlines):
                x_idx = nearest_idx(X,event.xdata)
                lines[0].set_xdata(X[x_idx])
                lines[1].set_ydata(heatmaps[i,:,x_idx])
    if interaction_type == 'move':
        fig.canvas.mpl_connect('motion_notify_event',update_lines) 
    elif interaction_type == 'click':
        fig.canvas.mpl_connect('button_press_event',update_lines) 
    else:
        plt.close(fig)
        raise ValueError(f'{interaction_type} is not a valid option for interaction_type, valid options are \'click\' or \'move\'')
    return fig,axes
