import ipywidgets as widgets
from IPython.display import display as ipy_display
from numpy import asarray, abs, argmin, min, max, swapaxes, atleast_1d, arange
from matplotlib.pyplot import figure as mpl_figure
from matplotlib.pyplot import ioff, ion, rcParams, subplots, interactive, install_repl_displayhook, uninstall_repl_displayhook
from matplotlib import is_interactive, interactive
from collections.abc import Iterable
from functools import partial


# functions that are methods
__all__ = [
    'interactive_plot_factory',
    'interactive_plot',
    'ioff',
    'figure',
    'nearest_idx',
    'heatmap_slicer',
    'zoom_factory',
    'panhandler',
]

# use until https://github.com/matplotlib/matplotlib/pull/17371 has a conclusion
class _ioff_class():
    def __call__(self):
        """Turn the interactive mode off."""
        interactive(False)
        uninstall_repl_displayhook()

    def __enter__(self):
        self.wasinteractive = is_interactive()
        self.__call__()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.wasinteractive:
            interactive(True)
            install_repl_displayhook()
        del self.wasinteractive
ioff = _ioff_class()

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
                                 
    with ioff:
        fig = figure()
        ax = fig.gca()
    controls = widgets.VBox(interactive_plot_factory(ax, f, x, x_scale,
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
    slice : {'horizontal', 'vertical', 'both'}
        Direction to draw slice on heatmap. both will draw horizontal and vertical traces on the same
        plot, while both_separate will make a line plot for each.
    heatmap_names : (String, String, ...)
        An iterable with the names of the heatmaps. If provided it must have as many names as there are heatmaps
    max_cols : int, optional - not working yet :(
        Maximum number of columns to allo   
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


    fig, axes = subplots(1,num_axes,figsize=figsize)
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


# based on https://gist.github.com/tacaswell/3144287
def zoom_factory(ax, base_scale = 1.1):
    """
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
    
    fig = ax.get_figure() # get the figure of interest
    fig.canvas.capture_scroll = True
    toolbar = fig.canvas.toolbar
    toolbar.push_current()
    orig_xlim = ax.get_xlim()
    orig_ylim = ax.get_ylim()
    orig_yrange = limits_to_range(orig_ylim)
    orig_xrange = limits_to_range(orig_xlim)
    orig_center = ((orig_xlim[0]+orig_xlim[1])/2, (orig_ylim[0]+orig_ylim[1])/2)
    out = widgets.Output()
    def zoom_fun(event):
        # get the current x and y limits
        cur_xlim = ax.get_xlim()
        cur_ylim = ax.get_ylim()
        # set the range
        cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
        cur_yrange = (cur_ylim[1] - cur_ylim[0])*.5
        xdata = event.xdata # get event x location
        ydata = event.ydata # get event y location
        if event.button == 'up':
            # deal with zoom in
            scale_factor = base_scale
        elif event.button == 'down':
            # deal with zoom out
            scale_factor = 1/base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
        # set new limits
        new_xlim = [xdata - (xdata-cur_xlim[0]) / scale_factor,
                    xdata + (cur_xlim[1]-xdata) / scale_factor]
        new_ylim = [ydata - (ydata-cur_ylim[0]) / scale_factor,
                        ydata + (cur_ylim[1]-ydata) / scale_factor]
        new_yrange = limits_to_range(new_ylim)
        new_xrange = limits_to_range(new_xlim)

        if abs(new_yrange)>abs(orig_yrange):
            new_ylim = orig_center[1] -new_yrange/2 , orig_center[1] +new_yrange/2
        if abs(new_xrange)>abs(orig_xrange):
            new_xlim = orig_center[0] -new_xrange/2 , orig_center[0] +new_xrange/2
        ax.set_xlim(new_xlim)
        ax.set_ylim(new_ylim)

        toolbar.push_current()
        ax.figure.canvas.draw_idle() # force re-draw


    # attach the call back
    cid = fig.canvas.mpl_connect('scroll_event',zoom_fun)
    def disconnect_zoom():
        fig.canvas.mpl_disconnect(cid)    

    #return the disconnect function
    return disconnect_zoom

class panhandler:
    """
    enable click to pan image.
    button determines which button will be used (default right click)
    Left: 1
    Middle: 2
    Right: 3
    """
    def __init__(self, fig, button=3):
        self.fig = fig
        self._id_drag = None
        self.button = button
        self.fig.canvas.mpl_connect('button_press_event', self.press)
        self.fig.canvas.mpl_connect('button_release_event', self.release)

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
            if (x is not None and y is not None and a.in_axes(event) and
                    a.get_navigate() and a.can_pan()):
                a.start_pan(x, y, event.button)
                self._xypress.append((a, i))
                self._id_drag = self.fig.canvas.mpl_connect(
                    'motion_notify_event', self._mouse_move)
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