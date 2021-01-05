try:
    from ipywidgets import widgets
    from IPython.display import display as ipy_display

    _not_ipython = False
except ImportError:
    _not_ipython = True
    pass
from collections import defaultdict
from .helpers import (
    create_slider_format_dict,
    kwarg_to_ipywidget,
    kwarg_to_mpl_widget,
    create_mpl_controls_fig,
    notebook_backend,
    process_mpl_widget,
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
        **kwargs
    ):
        # it might make sense to also accept kwargs as a straight up arg
        # to allow for passing the dictionary, but then it would need a different name
        # and we'd have to combine dicitonarys whihc looks like a hassle

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

        self.use_cache = use_cache
        self.kwargs = kwargs
        self.slider_format_strings = create_slider_format_dict(slider_formats)
        self.controls = {}
        self.params = {}
        self.figs = defaultdict(list)  # maybe should only store weakrefs?
        self.indices = defaultdict(lambda: 0)
        self._update_funcs = defaultdict(list)
        self._user_callbacks = defaultdict(list)
        self.add_kwargs(kwargs, slider_formats, play_buttons)

    def add_kwargs(self, kwargs, slider_formats=None, play_buttons=None, allow_duplicates=False):
        """
        If you pass a redundant kwarg it will just be overwritten
        maybe should only raise a warning rather than an error?

        need to implement matplotlib widgets
        also a big question is how to dynamically update the display of matplotlib widgets.
        """
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
        if self.use_ipywidgets:
            for k, v in kwargs.items():
                if k in self.params:
                    if allow_duplicates:
                        continue
                    else:
                        raise ValueError("can't overwrite an existing param in the controller")
                if isinstance(v, AxesWidget):
                    self.params[k], self.controls[k], _ = process_mpl_widget(
                        v, partial(self.slider_updated, key=k)
                    )
                else:
                    self.params[k], control = kwarg_to_ipywidget(
                        k,
                        v,
                        partial(self.slider_updated, key=k),
                        self.slider_format_strings[k],
                        play_button=_play_buttons[k],
                    )
                    if control:
                        self.controls[k] = control
                        self.vbox.children = list(self.vbox.children) + [control]
                if k == "vmin_vmax":
                    self.params["vmin"] = self.params["vmin_vmax"][0]
                    self.params["vmax"] = self.params["vmin_vmax"][1]
        else:
            if len(kwargs) > 0:
                mpl_layout = create_mpl_controls_fig(kwargs)
                self.control_figures.append(mpl_layout[0])
                widget_y = 0.05
                for k, v in kwargs.items():
                    if k in self.params:
                        if allow_duplicates:
                            continue
                        else:
                            raise ValueError("Can't overwrite an existing param in the controller")
                    self.params[k], control, cb, widget_y = kwarg_to_mpl_widget(
                        mpl_layout[0],
                        mpl_layout[1:],
                        widget_y,
                        k,
                        v,
                        partial(self.slider_updated, key=k),
                        self.slider_format_strings[k],
                    )
                    if control:
                        self.controls[k] = control
                    if k == "vmin_vmax":
                        self.params["vmin"] = self.params["vmin_vmax"][0]
                        self.params["vmax"] = self.params["vmin_vmax"][1]

    def _slider_updated(self, change, key, values):
        """
        gotta also give the indices in order to support hyperslicer without horrifying contortions
        """
        if values is None:
            self.params[key] = change["new"]
        else:
            c = change["new"]
            if isinstance(c, tuple):
                # This is for range sliders which return 2 indices
                self.params[key] = values[[*change["new"]]]
                if key == "vmin_vmax":
                    self.params["vmin"] = self.params[key][0]
                    self.params["vmax"] = self.params[key][1]
            else:
                # int casting due to a bug in numpy < 1.19
                # see https://github.com/ianhi/mpl-interactions/pull/155
                self.params[key] = values[int(change["new"])]
        self.indices[key] = change["new"]
        if self.use_cache:
            cache = {}
        else:
            cache = None

        for f, params in self._update_funcs[key]:
            ps = {}
            idxs = {}
            for k in params:
                ps[k] = self.params[k]
                idxs[k] = self.indices[k]
            f(params=ps, indices=idxs, cache=cache)
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
            a function called
        params : list of str, str, or None
            the params to be passed to the callback
        eager : bool
            Whether to call the callback immediately upon registration
        """
        if isinstance(params, str):
            params = [params]
        if eager:
            callback(**{key: self.params[key] for key in params})
        self._register_function(callback, fig=None, params=params)

    def _register_function(self, f, fig=None, params=None):
        """
        if params is None use the entire current set of params
        """
        if params is None:
            params = self.params.keys()
        # listify to ensure it's not a reference to dicts keys
        # bc thats mutable
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
        interval : int, default: 2o
            interval between frames in ms
        func_anim_kwargs : dict
            kwargs to pass the creation of the underlying FuncAnimation
        N_frames : int
            Only used if the param is a matplotlib slider that was created without a
            valstep argument. This will only be relevant if you passed your own matplotlib
            slider as a kwarg when plotting. If needed but not given it will default to
            a value of 200.
        **kwargs :
            Passed through to anim.save

        Returns
        -------
        anim : matplotlib.animation.FuncAniation
        """
        slider = self.controls[param]
        ipywidgets_slider = False
        if "Box" in str(slider.__class__):
            ipywidgets_slider = True
            for obj in slider.children:
                if "Slider" in str(obj.__class__):
                    slider = obj
            N = int((slider.max - slider.min) / slider.step)
            min_ = slider.min
            max_ = slider.max
            step = slider.step
        elif isinstance(slider, mSlider):
            min_ = slider.valmin
            max_ = slider.valmax
            if slider.valstep is None:
                N = N_frames if N_frames else 200
                step = (max_ - min_) / N
            else:
                N = int((max_ - min_) / slider.valstep)
                step = slider.valstep

        def f(i):
            val = min_ + step * i
            if ipywidgets_slider:
                slider.value = val
            else:
                slider.set_val(val)
            return []

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
            controls.add_kwargs(kwargs, slider_formats, play_buttons, allow_duplicates=allow_dupes)
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
            controls.add_kwargs(kwargs, slider_formats, play_buttons, allow_duplicates=allow_dupes)
            params = {k: controls.params[k] for k in list(kwargs.keys()) + list(extra_keys)}
        else:
            controls.add_kwargs(kwargs, slider_formats, play_buttons, allow_duplicates=allow_dupes)
            params = controls.params
        return controls, params
    else:
        controls = Controls(slider_formats=slider_formats, play_buttons=play_buttons, **kwargs)
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
