try:
    from IPython.display import display as ipy_display
    from ipywidgets import widgets

    _not_ipython = False
except ImportError:
    _not_ipython = True
from collections import defaultdict
from collections.abc import Iterable
from functools import partial

from matplotlib.animation import FuncAnimation
from matplotlib.widgets import AxesWidget
from matplotlib.widgets import Slider as mSlider

from .helpers import (
    create_mpl_controls_fig,
    create_slider_format_dict,
    kwarg_to_ipywidget,
    kwarg_to_mpl_widget,
    notebook_backend,
    process_mpl_widget,
)


class Controls:
    def __init__(
        self,
        slider_formats=None,
        play_buttons=False,
        play_button_pos="right",
        use_ipywidgets=None,
        use_cache=True,
        **kwargs,
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
            self.control_figures = []
            """Storage for figures made of matplotlib sliders."""

        self.use_cache = use_cache
        self.kwargs = kwargs
        self.slider_format_strings = create_slider_format_dict(slider_formats)
        self.controls = {}
        self.params = {}
        """Parameters in the controller, see :doc:`/examples/custom-callbacks`."""
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
            # int casting due to a bug in numpy < 1.19
            # see https://github.com/ianhi/mpl-interactions/pull/155
            if isinstance(c, Iterable):
                # range sliders return two indices
                # check for iterable as mpl and ipywidgets sliders don't both use
                # tuples - https://github.com/ianhi/mpl-interactions/issues/195
                self.params[key] = values[[int(c) for c in change["new"]]]
                if key == "vmin_vmax":
                    self.params["vmin"] = self.params[key][0]
                    self.params["vmax"] = self.params[key][1]
            else:
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
        e.g. of ``vmin_vmax`` -> ``vmin`` and ``vmax``. In the future maybe
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

    def save_animation(
        self, filename, fig, param, interval=20, func_anim_kwargs={}, N_frames=None, **kwargs
    ):
        """
        Save an animation over one of the parameters controlled by this `Controls` object.

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
        **kwargs
            Passed through to anim.save

        Returns
        -------
        anim : matplotlib.animation.FuncAniation
        """
        slider = self.controls[param]
        ipywidgets_slider = False
        if "Box" in str(slider.__class__):
            for obj in slider.children:
                if "Slider" in str(obj.__class__):
                    slider = obj

        if isinstance(slider, mSlider):
            min_ = slider.valmin
            max_ = slider.valmax
            if slider.valstep is None:
                n_steps = N_frames if N_frames else 200
                step = (max_ - min_) / n_steps
            else:
                step = slider.valstep
        elif "Slider" in str(slider.__class__):
            ipywidgets_slider = True
            min_ = slider.min
            max_ = slider.max
            step = slider.step
        else:
            raise NotImplementedError(
                "Cannot save animation for slider of type {slider.__class__.__name__}"
            )

        N = int((max_ - min_) / step)

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

    def __getitem__(self, key):
        """
        hack to allow calls like
        interactive_plot(...beta=(0,1), controls = controls["tau"])
        also allows [None] to grab None of the current params
        to imply that we only want tau from the existing set of commands

        I think ideally this would give another controls object with just the given
        params that has this one as a parent - I think that that is most consistent with
        the idea of indexing (e.g. indexing a numpy array gives you a numpy array).
        But it's not clear how to implement that with all the sliders and such that get
        created. So for now do a sort of half-measure by returing the controls_proxy object.
        """

        # make sure keys is a list
        # bc in gogogo_controls it may get added to another list
        keys = key
        if isinstance(key, str):
            keys = [key]
        if keys is not None:
            for k in keys:
                if k not in self.params:
                    raise IndexError(f"{k} is not a param in this Controls object.")

        return _controls_proxy(self, context=False, keys=keys)

    def __enter__(self):
        self._context = _controls_proxy(self, context=True, keys=list(self.params.keys()))
        return self._context

    def __exit__(self, exc_type, exc_value, traceback):
        self._context._stack.remove(self._context)


class _controls_proxy:
    _stack = []

    def __init__(self, ctrl, context, keys=None):
        self.ctrl = ctrl
        if keys is None:
            self.keys = []
        else:
            self.keys = keys
        if context:
            self.__enter__()

    def __enter__(self):
        self._stack.append(self)

    def __exit__(self, exc_type, exc_value, traceback):
        self._stack.remove(self)


def gogogo_controls(
    kwargs,
    controls,
    display_controls,
    slider_formats,
    play_buttons,
    extra_controls=None,
    allow_dupes=False,
):
    # check if we're in a controls context manager
    if len(_controls_proxy._stack) > 0:
        ctrl_context = _controls_proxy._stack[-1]
        if extra_controls is None:
            extra_controls = [ctrl_context]
        else:
            extra_controls.append(ctrl_context)

    # Squash controls + extra_controls and make sure we have a unique controller object

    # first check whether we go an argument of controls = controls
    # or somethign like controls=controls['param1', 'param2']
    if isinstance(controls, Controls):
        ctrls = [controls]
        keys = list(controls.params.keys())
    elif isinstance(controls, _controls_proxy):
        ctrls = [controls.ctrl]
        keys = list(controls.keys)
    else:
        ctrls = []
        keys = []

    # loop over extra_controls to collect all of them
    if extra_controls is not None:
        for ec in extra_controls:
            if isinstance(ec, _controls_proxy):
                # e.g. indexed ctrls for scalar arg
                # or in context manager
                ctrls.append(ec.ctrl)
                keys.extend(ec.keys)
            elif isinstance(ec, Controls):
                # I don't think we should ever get here?
                # if we do not sure what should be happening with the keys
                ctrls.append(ec)
    ctrls = set(ctrls)
    keys = set(keys + list(kwargs.keys()))

    if len(ctrls) > 1:
        raise ValueError("Only one controls object may be used per function")

    # now we are garunteed to only have either no controls and must make one
    # or have a single controls object that we should add to.
    if None in ctrls or len(ctrls) == 0:
        controls = Controls(slider_formats=slider_formats, play_buttons=play_buttons, **kwargs)
        params = controls.params
        if display_controls:
            controls.display()
    else:
        controls = ctrls.pop()
        controls.add_kwargs(kwargs, slider_formats, play_buttons, allow_duplicates=allow_dupes)
        params = {k: controls.params[k] for k in keys}
    return controls, params


def _gen_f(key):
    def f(*args, **kwargs):
        return kwargs[key]

    return f


def _gen_param_excluder(added_kwargs):
    """
    Pass through all the original keys, but exclude any kwargs that we added
    manually through prep_scalar

    Parameters
    ----------
    added_kwargs : list of str

    Returns
    -------
    excluder : callable
    """

    def excluder(params, except_=None):
        """
        Parameters
        ----------
        params : dict
        except : str
        """
        return {k: v for k, v in params.items() if k not in added_kwargs or k == except_}

    return excluder


def prep_scalars(kwarg_dict, **kwargs):
    """
    Process potentially scalar arguments. This allows for passing in
    slider shorthands for these arguments, and for passing indexed controls objects for them.

    Parameters
    ----------
    kwarg_dict : dict
        The kwargs passed to the calling functions
    kwargs :
        The arguments to process

    Returns
    -------
    funcs : dict
        The processed arguments. Re-assign the args as ``s = funcs['s']`` to
        make use of any autogenerated functions to connect callbacks to these
        scalar values.
    extra_ctrls : list of Controls
        Any extra controls objects that need to be used. Useful for `gogogo_controls`
    param_excluder : function
        A function to exclude any scalar kwargs we added from params. Use this in the
        update functions to avoid calling user provided functions with the kwargs that
        we added here.
    """
    extra_ctrls = []
    added_kwargs = []

    for name, arg in kwargs.items():
        if isinstance(arg, tuple) and name is not None:
            # name will be set by calling function if from ipyplot
            # this case is if given an abbreviation e.g.: `s = (0, 10)`

            kwargs[name] = _gen_f(name)

            # Modify the calling functions kwargs in place to add the arg
            kwarg_dict[name] = arg
            added_kwargs.append(name)
        elif isinstance(arg, _controls_proxy) and len(arg.keys) == 1:
            # indexed controls. e.g. ctrls['vmin']
            kwargs[name] = _gen_f(arg.keys[0])
            extra_ctrls.append(arg)

    if len(added_kwargs) == 0:
        # shortcircuit options
        def param_excluder(params, except_=None):
            return params

    else:
        param_excluder = _gen_param_excluder(added_kwargs)
    return kwargs, extra_ctrls, param_excluder
