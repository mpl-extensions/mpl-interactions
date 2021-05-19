try:
    from ipywidgets import widgets
    from IPython.display import display as ipy_display

    _not_ipython = False
except ImportError:
    _not_ipython = True
    pass
from collections import defaultdict
from mpl_interactions.widgets import IndexSlider, SliderWrapper

from .helpers import (
    create_slider_format_dict,
    maybe_create_mpl_controls_axes,
    kwarg_to_widget,
    maybe_get_widget_for_display,
    notebook_backend,
)
from functools import partial
from collections.abc import Iterable
from matplotlib.widgets import AxesWidget
from matplotlib.widgets import Slider as mSlider
from matplotlib.animation import FuncAnimation


class Controls:
    def __init__(
        self,
        slider_formats=None,
        play_buttons=False,
        play_button_pos="right",
        use_ipywidgets=None,
        use_cache=True,
        index_kwargs=[],
        **kwargs
    ):
        # it might make sense to also accept kwargs as a straight up arg
        # to allow for passing the dictionary, but then it would need a different name
        # and we'd have to combine dicitonarys which looks like a hassle

        if use_ipywidgets is None:
            # if this ends up being true we are garunteed
            self.use_ipywidgets = notebook_backend()
        else:
            self.use_ipywidgets = use_ipywidgets
        if self.use_ipywidgets:
            if _not_ipython:
                raise ValueError(
                    "You need to be in an Environment with IPython.display available to use ipywidgets"
                )
            self.vbox = widgets.VBox([])
        else:
            self.control_figures = []  # storage for figures made of matplotlib sliders
        if widgets:
            self.vbox = widgets.VBox([])
        self.use_cache = use_cache
        self.kwargs = kwargs
        self.slider_format_strings = create_slider_format_dict(slider_formats)
        self.controls = {}
        self.params = {}
        self.figs = defaultdict(list)  # maybe should only store weakrefs?
        self.indices = defaultdict(lambda: 0)
        self._update_funcs = defaultdict(list)
        self._user_callbacks = defaultdict(list)
        self.add_kwargs(kwargs, slider_formats, play_buttons, index_kwargs=index_kwargs)

    def add_kwargs(
        self,
        kwargs,
        slider_formats=None,
        play_buttons=None,
        allow_duplicates=False,
        index_kwargs=None,
    ):
        """
        If you pass a redundant kwarg it will just be overwritten
        maybe should only raise a warning rather than an error?

        need to implement matplotlib widgets
        also a big question is how to dynamically update the display of matplotlib widgets.

        Parameters
        ----------
        index_kwargs : list of str or None
            A list of which sliders should use an index for their callbacks.
        """
        if not index_kwargs:
            index_kwargs = []
        if isinstance(play_buttons, bool) or isinstance(play_buttons, str) or play_buttons is None:
            _play_buttons = defaultdict(lambda: play_buttons)
        elif isinstance(play_buttons, defaultdict):
            _play_buttons = play_buttons
        elif isinstance(play_buttons, dict):
            _play_buttons = defaultdict(lambda: False, play_buttons)
        elif isinstance(play_buttons, Iterable) and all([isinstance(p, str) for p in play_buttons]):
            _play_buttons = defaultdict(
                lambda: False, dict(zip(play_buttons, [True] * len(play_buttons)))
            )
        else:
            _play_buttons = play_buttons
        if slider_formats is not None:
            slider_formats = create_slider_format_dict(slider_formats)
            for k, v in slider_formats.items():
                self.slider_format_strings[k] = v

        if not self.use_ipywidgets:
            axes, fig = maybe_create_mpl_controls_axes(kwargs)
            if fig is not None:
                self.control_figures.append((fig))
        else:
            axes = [None] * len(kwargs)

        for k, v in kwargs.items():
            if k in self.params:
                if allow_duplicates:
                    continue
                else:
                    raise ValueError("can't overwrite an existing param in the controller")
            # TODO: accept existing mpl widget
            # if isinstance(v, AxesWidget):
            #     self.params[k], self.controls[k], _ = process_mpl_widget(
            #         v, partial(self.slider_updated, key=k)
            #     )
            # else:
            ax = axes.pop()
            control = kwarg_to_widget(k, v, ax, play_button=_play_buttons[k])
            # TODO: make the try except silliness less ugly
            # the complexity of hiding away the val vs value vs whatever needs to
            # be hidden away somewhere - but probably not here
            if k in index_kwargs:
                self.params[k] = control.index
                try:
                    control.observe(partial(self._slider_updated, key=k), names="index")
                except AttributeError:
                    self._setup_mpl_widget_callback(control, k)
            else:
                self.params[k] = control.value
                try:
                    control.observe(partial(self._slider_updated, key=k), names="value")
                except AttributeError:
                    self._setup_mpl_widget_callback(control, k)

            if control:
                self.controls[k] = control
                if ax is None:
                    disp = maybe_get_widget_for_display(control)
                    if disp is not None:
                        self.vbox.children = list(self.vbox.children) + [disp]
            if k == "vmin_vmax":
                self.params["vmin"] = self.params["vmin_vmax"][0]
                self.params["vmax"] = self.params["vmin_vmax"][1]

    def _setup_mpl_widget_callback(self, widget, key):
        def on_changed(val):
            self._slider_updated({"new": val}, key=key)

        widget.on_changed(on_changed)

    def _slider_updated(self, change, key):
        """
        gotta also give the indices in order to support hyperslicer without horrifying contortions
        """
        self.params[key] = change["new"]
        if key == "vmin_vmax":
            self.params["vmin"] = self.params[key][0]
            self.params["vmax"] = self.params[key][1]
        if self.use_cache:
            cache = {}
        else:
            cache = None

        for f, params in self._update_funcs[key]:
            ps = {}
            for k in params:
                ps[k] = self.params[k]
            f(params=ps, cache=cache)
        # TODO: see if can combine these with update_funcs for only one loop
        for f, params in self._user_callbacks[key]:
            f(**{key: self.params[key] for key in params})
        for f in self.figs[key]:
            f.canvas.draw_idle()

    def slider_updated(self, change, key, values):
        """
        thin wrapper to enable splitting of special cased range sliders.
        e.g. of `vmin_vmax` -> `vmin` and `vmax`. In the future maybe
        generalize this to any range slider with an underscore in the name?
        """
        self._slider_updated(change, key, values)
        if key == "vmin_vmax":
            self._slider_updated({"new": change["new"][0]}, "vmin", values)
            self._slider_updated({"new": change["new"][1]}, "vmax", values)

    def register_callback(self, callback, params=None, eager=False):
        """
        Register a callback to be called anytime one of the specified params changes.

        Parameters
        ----------
        callback : callable
            A function called. Should accept all of the parameters specified by *params*
            as a kwargs.
        params : str, list of str, or None
            The params to be passed to the callback. If *None* then all params
            currently registered with this controls object will be used.
        eager : bool, default: False
            If True, call the callback immediately upon registration
        """
        if isinstance(params, str):
            params = [params]
        if eager:
            if params is None:
                callback(**self.params)
            else:
                callback(**{key: self.params[key] for key in params})
        self._register_function(callback, fig=None, params=params)

    def _register_function(self, f, fig=None, params=None):
        """
        if params is None use the entire current set of params
        """
        if params is None:
            params = self.params.keys()
        # listify to ensure it's not a reference to dicts keys
        # bc that's mutable
        params = list(params)
        for p in params:
            if fig is None:
                self._user_callbacks[p].append((f, params))
            else:
                self._update_funcs[p].append((f, params))
                if fig not in self.figs[p] and fig is not None:
                    self.figs[p].append(fig)  # maybe should use a weakref?
                    # also should probably register a close_event callback to remove
                    # the figure

    def __getitem__(self, key):
        """
        hack to allow calls like
        interactive_plot(...beta=(0,1), controls = controls["tau"])
        also allows [None] to grab None of the current params
        to imply that we only want tau from the existing set of commands
        """

        # make sure keys is a list
        # bc in gogogo_controls it may get added to another list
        if isinstance(key, str):
            key = [key]
        elif key is None:
            key = []
        return self, key

    def save_animation(
        self, filename, fig, param, interval=20, func_anim_kwargs={}, N_frames=None, **kwargs
    ):
        """
        Save an animation over one of the parameters controlled by this `controls` object.

        Parameters
        ----------
        filename : str
        fig : figure
        param : str
            the name of the kwarg to use to animate
        interval : int, default: 20
            interval between frames in ms
        func_anim_kwargs : dict
            kwargs to pass the creation of the underlying FuncAnimation
        N_frames : int
            Only used if the param is a matplotlib slider that was created without a
            valstep argument. This will only be relevant if you passed your own matplotlib
            slider as a kwarg when plotting. If needed but not given it will default to
            a value of 200.
        **kwargs
            Passed through to anim.save

        Returns
        -------
        anim : matplotlib.animation.FuncAniation
        """
        slider = self.controls[param]
        # at this point every slider should be wrapped by at least a .widgets.WidgetWrapper
        if isinstance(slider, IndexSlider):
            N = len(slider.values)

            def f(i):
                slider.index = i
                return []

        elif isinstance(slider, SliderWrapper):
            min = slider.min
            max = slider.max
            if slider.step is None:
                n_steps = N_frames if N_frames else 200
                step = (max - min) / n_steps
            else:
                step = slider.valstep
            N = int((max - min) / step)

            def f(i):
                slider.value = min + step * i
                return []

        else:
            raise NotImplementedError(
                "Cannot save animation for param of type %s".format(type(slider))
            )

        repeat = func_anim_kwargs.pop("repeat", False)
        anim = FuncAnimation(fig, f, frames=N, interval=interval, repeat=repeat, **func_anim_kwargs)
        # draw then stop necessary to prevent an extra loop after finished saving
        # see https://discourse.matplotlib.org/t/how-to-prevent-funcanimation-looping-a-single-time-after-save/21680/2
        fig.canvas.draw()
        anim.event_source.stop()
        anim.save(filename, **kwargs)
        return anim

    def display(self):
        """
        Display the display the ipywidgets controls or show the control figures
        """
        if self.use_ipywidgets:
            ipy_display(self.vbox)
        else:
            for fig in self.control_figures:
                if fig is not None:
                    fig.show()

    def show(self):
        """
        Show the control figures or display the ipywidgets controls
        """
        self.display()

    def _ipython_display_(self):
        ipy_display(self.vbox)


def gogogo_controls(
    kwargs,
    controls,
    display_controls,
    slider_formats,
    play_buttons,
    extra_controls=None,
    allow_dupes=False,
    index_kwargs=[],
):
    if controls or (extra_controls and not all([e is None for e in extra_controls])):
        if extra_controls is not None:
            if isinstance(controls, Controls):
                # e.g. plt.scatter(x,y, s=ctrls['size'], controls=ctrls)
                # so now we pretend as if the controls object was indexed with all of its
                # parameters
                controls = (controls, list(controls.params.keys()))
            controls = [controls] + extra_controls

        if isinstance(controls, tuple):
            # it was indexed by the user when passed in
            extra_keys = controls[1]
            controls = controls[0]
            controls.add_kwargs(
                kwargs,
                slider_formats,
                play_buttons,
                allow_duplicates=allow_dupes,
                index_kwargs=index_kwargs,
            )
            params = {k: controls.params[k] for k in list(kwargs.keys()) + list(extra_keys)}
        elif isinstance(controls, list):
            # collected from extra controls
            ctrls = []
            kwgs = []
            for c in controls:
                if c is not None:
                    # c[0] is a controls object
                    ctrls.append(c[0])
                    if c[1] is not None:
                        # at this point c[1] is a list of the the values indexed from controls
                        kwgs += [*c[1]]
            extra_keys = set(kwgs)
            controls = set(ctrls)
            if len(controls) != 1:
                raise ValueError("Only one controls object may be used per function")
            # now we are garunteed to only have a single entry in controls, so it's ok to pop
            controls = controls.pop()
            controls.add_kwargs(
                kwargs,
                slider_formats,
                play_buttons,
                allow_duplicates=allow_dupes,
                index_kwargs=index_kwargs,
            )
            params = {k: controls.params[k] for k in list(kwargs.keys()) + list(extra_keys)}
        else:
            controls.add_kwargs(
                kwargs,
                slider_formats,
                play_buttons,
                allow_duplicates=allow_dupes,
                index_kwargs=index_kwargs,
            )
            params = controls.params
        return controls, params
    else:
        controls = Controls(
            slider_formats=slider_formats,
            play_buttons=play_buttons,
            index_kwargs=index_kwargs,
            **kwargs
        )
        params = controls.params
        if display_controls:
            controls.display()
        return controls, params


def prep_scalar(arg, name=None):
    if isinstance(arg, tuple):
        if isinstance(arg[0], Controls):
            # index controls. e.g. ctrls['size']

            def f(*args, **kwargs):
                return kwargs[arg[1][0]]

            return f, arg, None
        elif name is not None:
            # name will be set by calling function if from ipyplot
            # this case is if given an abbreviation e.g.: `s = (0, 10)`
            def f(*args, **kwargs):
                return kwargs[name]

            return f, None, (name, arg)
    return arg, None, None
