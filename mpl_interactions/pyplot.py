import ipywidgets as widgets
from IPython.display import display as ipy_display
from numpy import asarray, atleast_1d, arange, linspace
from matplotlib import get_backend
from functools import partial
from warnings import warn
from collections import defaultdict
from .utils import ioff, figure
import matplotlib.widgets as mwidgets
from collections.abc import Iterable
from matplotlib.pyplot import axes, sca
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
from matplotlib import __version__ as mpl_version
from packaging import version


# functions that are methods
__all__ = [
    'interactive_plot_factory',
    'interactive_plot',
    'interactive_hist',
]

def _notebook_backend():
    backend = get_backend().lower()
    if 'ipympl' in backend:
        return True
    elif backend == 'nbAgg'.lower():
        warn('You are using an outdated backend. You should use `%matplotlib ipympl` instead of `%matplotlib notebook`')
        return True
    return False
def _kwargs_to_widget(kwargs, params, update, slider_format_strings):
    """
    this will break if you pass a matplotlib slider. I suppose it could support mixed types of sliders
    but that doesn't really seem worthwhile?
    """
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


def _extract_num_options(val):
    """
    convert a categorical to a number of options
    """
    if len(val) == 1:
        for v in val:
            if isinstance(v, tuple):
                # this looks nightmarish...
                # but i think it should always work
                # should also check if the tuple has length one here.
                # that will only be an issue if a trailing comma was used to make the tuple ('beep',)
                # but not ('beep') - the latter is not actually a tuple
                return len(v)
            else:
                return 0
    else:
        return len(val)

def _changeify(val, key, update):
    """
    make matplotlib update functions return a dict with key 'new'.
    Do this for compatibility with ipywidgets
    """
    update({'new': val}, key, None)

# this is a bunch of hacky nonsense
# making it involved me holding a ruler up to my monitor
# if you have a better solution I would love to hear about it :)
# - Ian 2020-08-22
def _kwargs_to_mpl_widgets(kwargs, params, update, slider_format_strings):
    n_opts = 0
    n_radio = 0
    n_sliders = 0
    for key, val in kwargs.items():
        if isinstance(val, set):
            new_opts = extract_num_options(val)
            if new_opts>0:
                n_radio += 1
                n_opts += new_opts
        elif not isinstance(val, mwidgets.AxesWidget) and not isinstance(val, widgets.fixed) and isinstance(val, Iterable) and len(val)>1:
            n_sliders += 1

    # These are roughly the sizes used in the matplotlib widget tutorial
    # https://matplotlib.org/3.2.2/gallery/widgets/slider_demo.html#sphx-glr-gallery-widgets-slider-demo-py
    slider_in = .15
    radio_in = .6/3
    widget_gap_in = .1

    widget_inches = n_sliders*slider_in + n_opts*radio_in + widget_gap_in * (n_sliders + n_radio + 1) + .5 # half an inch for margin
    fig = None
    if not all(map(lambda x: isinstance(x, mwidgets.AxesWidget), kwargs.values())):
        # if the only kwargs are existing matplotlib widgets don't make a new figure
        with ioff:
            fig = figure()
        size = fig.get_size_inches()
        fig_h = widget_inches
        fig.set_size_inches(size[0], widget_inches)
        slider_height = slider_in / fig_h
        radio_height  = radio_in / fig_h
        # radio
        gap_height = widget_gap_in/fig_h
    widget_y = .05
    slider_ax = []
    sliders = []
    radio_ax = []
    radio_buttons = []
    cbs = []
    for key, val in kwargs.items():
        if isinstance(val, set):
            if len(val) == 1:
                val = val.pop()
                if isinstance(val, tuple):
                    pass
                else:
                    params[key] = val
                    continue
            else:
                val = list(val)

            n = len(val)
            longest_len = max(list(map(lambda x: len(list(x)),map(str,val))))
            # should probably use something based on fontsize rather that .015
            width = max(.15, .015*longest_len)
            radio_ax.append(axes([.2 ,.9 - widget_y - radio_height*n, width, radio_height*n]))
            widget_y += radio_height * n + gap_height
            radio_buttons.append(mwidgets.RadioButtons(radio_ax[-1], val, active=0))
            cbs.append(radio_buttons[-1].on_clicked(partial(_changeify,key=key, update=update)))
            params[key] = val[0]
        elif isinstance(val, mwidgets.RadioButtons):
            val.on_clicked(partial(_changeify, key=key, update=update))
            params[key] = val.val
        elif isinstance(val, mwidgets.Slider):
            val.on_changed(partial(_changeify, key=key, update=update))
            params[key] = val.val
        else:
            if isinstance(val, tuple):
                if len(val) == 2:
                    min_ = val[0]
                    max_ = val[1]
                elif len(val) == 3:
                    # should warn that that doesn't make sense with matplotlib sliders
                    min_ = val[0]
                    max_ = val[1]
            else:
                val = np.atleast_1d(val)
                if val.ndim > 1:
                    raise ValueError(f'{key} is {val.ndim}D but can only be 1D or a scalar')
                if len(val)==1:
                    # don't need to create a slider
                    params[key] = val[0]
                    continue
                else:
                    # list or numpy array
                    # should warn here as well
                    min_ = np.min(val)
                    max_ = np.max(val)

            slider_ax.append(axes([.2, .9- widget_y-gap_height, .65, slider_height]))
            sliders.append(mwidgets.Slider(slider_ax[-1], key, min_, max_, valinit=min_, valfmt=slider_format_strings[key]))
            cbs.append(sliders[-1].on_changed(partial(_changeify, key=key, update=update)))
            widget_y += slider_height + gap_height
            params[key] = min_
    controls = [fig, radio_ax, radio_buttons, slider_ax, sliders]
    return controls


def _create_slider_format_dict(slider_format_string, use_ipywidgets):
    # mpl sliders for verison 3.3 and onwards support None as an argument for valfmt
    mpl_gr_33 = version.parse(mpl_version) >= version.parse("3.3")
    if isinstance(slider_format_string, str):
        slider_format_strings = defaultdict(lambda: slider_format_string)
    elif isinstance(slider_format_string, dict) or slider_format_string is None:
        if use_ipywidgets:
            slider_format_strings = defaultdict(lambda: '{:.2f}')
        elif mpl_gr_33:
            slider_format_strings = defaultdict(lambda: None)
        else:
            slider_format_strings = defaultdict(lambda: '%1.2f')

        if slider_format_string is not None:
            for key, val in slider_format_string.items():
                slider_format_strings[key] = val
    else:
        raise ValueError(f'slider_format_string must be a dict or a string but it is a {type(slider_format_string)}')
    return slider_format_strings
def interactive_plot_factory(ax, f, x=None,
                                 xlim='stretch',
                                 ylim='stretch',
                                 slider_format_string=None,
                                 plot_kwargs=None,
                                 title=None, use_ipywidgets=None, **kwargs):
    """
    Use this function for maximum control over layout of the widgets.
    
    parameters
    ----------
    ax : matplotlib axes
    f : function or iterable of functions
    use_ipywidgets : None or boolean, optional
        If None will attempt to infer whether to use ipywidgets based on the backend. Use
        True or False to ensure ipywidgets is or is not used.
    """
    if use_ipywidgets is None:
        use_ipywidgets = _notebook_backend() 
    params = {}
    funcs = atleast_1d(f)

    slider_format_strings = _create_slider_format_dict(slider_format_string, use_ipywidgets)
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
        if ylim=='auto':
            ax.autoscale_view(scalex=False)
        elif ylim=='stretch':
            new_lims = [ax.dataLim.y0, ax.dataLim.y0+ax.dataLim.height]
            new_lims = [
                new_lims[0] if new_lims[0]<cur_ylims[0] else cur_ylims[0],
                new_lims[1] if new_lims[1]>cur_ylims[1] else cur_ylims[1]
                ]
            ax.set_ylim(new_lims)
        if xlim=='auto':
            ax.autoscale_view(scaley=False)
        elif xlim=='stretch':
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
    if use_ipywidgets:
        sliders, labels, controls = _kwargs_to_widget(kwargs, params, update, slider_format_strings)
    else:
        controls = _kwargs_to_mpl_widgets(kwargs, params, update, slider_format_strings)
        sca(ax)

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
        for i in range(len(funcs)):
            plot_kwargs.append({})
    else:
        plot_kwargs = atleast_1d(plot_kwargs)
        if not len(plot_kwargs) == len(funcs):
            raise ValueError('If using multiple functions'
                            ' then plot_kwargs must be a list'
                            ' of the same length or None.')
    
    # make sure plot labels make sense
    for i in range(len(funcs)):
        if 'label' not in plot_kwargs[i]:
            plot_kwargs[i]['label'] = funcs[i].__name__

    lines = []
    for i,f in enumerate(funcs):

        if x is not None and not indexed_x:
            lines.append(ax.plot(x, f(x, **params), **plot_kwargs[i])[0])
        elif indexed_x:
            lines.append(ax.plot(x, f(**params), **plot_kwargs[i])[0])
        else:
            lines.append(ax.plot(*f(**params), **plot_kwargs[i])[0])
    if not isinstance(xlim,str):
        ax.set_xlim(xlim)
    if not isinstance(ylim,str):
        ax.set_ylim(ylim)
    if title is not None:
        ax.set_title(title.format(**params))

    # make sure the home button will work
    fig.canvas.toolbar.push_current()
    return controls

def interactive_plot(f, x=None, xlim='stretch', ylim='stretch',
                        slider_format_string=None,
                        plot_kwargs=None,
                        title=None,figsize=None, display=True, force_ipywidgets=False, **kwargs):
    """
    Make a plot interactive using sliders.
    
    parameters
    ----------
    f : function or list(functions)
        The function(s) to plot. Each function should return either the y values, or
        a list of both the x and y arrays to plot [x, y]
    x : arraylike or None
        x values a which to evaluate the function. If None the function(s) f should
        return a list of [x, y]
    ax : matplolibt.Axes or None
        axes on which to 
    xlim : string or tuple of floats, optional
        If a tuple it will be passed to ax.set_xlim. Other options are:
        'auto': rescale the x axis for every redraw
        'stretch': only ever expand the xlims.
    ylim : string or tuple of floats, optional
        If a tuple it will be passed to ax.set_ylim. Other options are same
        as xlim
    slider_format_string : None, string, or dict
        If None a default value of decimal points will be used. For ipywidgets this uses the new f-string formatting
        For matplotlib widgets you need to use `%` style formatting. A string will be used as the default
        format for all values. A dictionary will allow assigning different formats to different sliders.
        note: For matplotlib >= 3.3 a value of None for slider_format_string will use the matplotlib ScalarFormatter
        object for matplotlib slider values.
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
    force_ipywidgets : boolean
        If True ipywidgets will always be used, even if not using the ipympl backend.
        If False the function will try to detect if it is ok to use ipywidgets
        If ipywidgets are not used the function will fall back on matplotlib widgets

    returns
    -------
    fig : matplotlib figure
    ax : matplotlib axis
    controls : list of slider widgets

    Examples 
    --------

    With numpy arrays::

        x = np.linspace(0,2*np.pi)
        tau = np.linspace(0, np.pi)
        def f(x, tau):
            return np.sin(x+tau)
        interactive_plot(f, x=x, tau=tau)

    with tuples::

        x = np.linspace(0,2*np.pi)
        def f(x, tau):
            return np.sin(x+tau)
        interactive_plot(f, x=x, tau=(0, np.pi, 1000))

    """
                                 
    ipympl = _notebook_backend()
    if ipympl:
        with ioff:
            fig = figure()
            ax = fig.gca()
    else:
        fig = figure()
        ax = fig.gca()

    use_ipywidgets = ipympl or force_ipywidgets
    controls = interactive_plot_factory(ax, f, x, xlim,
                            ylim, slider_format_string,
                            plot_kwargs, title,
                            use_ipywidgets=use_ipywidgets, **kwargs)
    if use_ipywidgets:
        controls = widgets.VBox(controls) 
        if display:
            if ipympl:
                ipy_display(widgets.VBox([controls, fig.canvas]))
            else:
                # for the case of using %matplotlib qt
                # but also want ipywidgets sliders
                # ie with force_ipywidgets = True
                ipy_display(controls)
                fig.show()
    else:
        if display:
            fig.show()
            controls[0].show()
    return fig, ax, controls



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

def interactive_hist(f, density=False, bins='auto', weights=None, slider_format_string=None, force_ipywidgets=False, **kwargs):
    """
    Control the contents of a histogram using sliders.
    
    See https://github.com/ianhi/mpl-interactions/pull/73#issue-470638134 for a discussion
    of the limitations of this function. These limitations will be improved once
    https://github.com/matplotlib/matplotlib/pull/18275 has been merged.

    parameters
    ----------
    f : function
        A function that will return a 1d array of which to take the histogram
    density : bool, optional
        whether to plot as a probability density. Passed to np.histogram
    bins : int or sequence of scalars or str, optional
        bins argument to np.histogram
    weights : array_like, optional
        passed to np.histogram
    slider_format_string : None, string, or dict
        If None a default value of decimal points will be used. For ipywidgets this uses the new f-string formatting
        For matplotlib widgets you need to use `%` style formatting. A string will be used as the default
        format for all values. A dictionary will allow assigning different formats to different sliders.
        note: For matplotlib >= 3.3 a value of None for slider_format_string will use the matplotlib ScalarFormatter
        object for matplotlib slider values.
    force_ipywidgets : boolean
        If True ipywidgets will always be used, even if not using the ipympl backend.
        If False the function will try to detect if it is ok to use ipywidgets
        If ipywidgets are not used the function will fall back on matplotlib widgets

    returns
    -------
    fig : matplotlib figure
    ax : matplotlib axis
    controls : list of slider widgets

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

    params = {}
    funcs = atleast_1d(f)
    # supporting more would require more thought
    if len(funcs) != 1:
        raise ValueError(f"Currently only a single function is supported. You passed in {len(funcs)} functions")

    ipympl = _notebook_backend()
    if ipympl:
        with ioff:
            fig = figure()
            ax = fig.gca()
    else:
        fig = figure()
        ax = fig.gca()
    use_ipywidgets = ipympl or force_ipywidgets
    pc = PatchCollection([])
    ax.add_collection(pc, autolim=True)

    slider_format_strings = _create_slider_format_dict(slider_format_string, use_ipywidgets)

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
    if use_ipywidgets:
        sliders, labels, controls = _kwargs_to_widget(kwargs, params, update, slider_format_strings)
    else:
        controls = _kwargs_to_mpl_widgets(kwargs, params, update, slider_format_strings)

    new_x, new_y, new_patches = simple_hist(funcs[0](**params), density=density, bins=bins, weights=weights)
    pc.set_paths(new_patches)
    ax.set_xlim(new_x)
    ax.set_ylim(new_y)


    if use_ipywidgets:
        controls = widgets.VBox(controls) 
        if display:
            if ipympl:
                ipy_display(widgets.VBox([controls, fig.canvas]))
            else:
                # for the case of using %matplotlib qt
                # but also want ipywidgets sliders
                # ie with force_ipywidgets = True
                ipy_display(controls)
                fig.show()
    else:
        if display:
            fig.show()
            controls[0].show()
    return fig, ax, controls
