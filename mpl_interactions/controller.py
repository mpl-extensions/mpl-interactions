from IPython.display import display as ipy_display
from collections import defaultdict
from .helpers import create_slider_format_dict, kwarg_to_ipywidget
from functools import partial
from ipywidgets import widgets
from collections import Iterable


class Controls:
    def __init__(
        self, out=None, slider_formats=None, play_buttons=False, play_button_pos="right", **kwargs
    ):
        # it might make sense to also accept kwargs as a straight up arg
        # to allow for passing the dictionary, but then it would need a different name
        # and we'd have to combine dicitonarys whihc looks like a hassle

        if out is not None:
            self.out = out
        else:
            self.out = widgets.Output()
        self.kwargs = kwargs
        self.slider_format_strings = create_slider_format_dict(slider_formats, True)
        self.controls = {}
        self.params = {}
        self.figs = defaultdict(list)  # maybe should only store weakrefs?
        self.indices = defaultdict(lambda: 0)
        self._update_funcs = defaultdict(list)
        self.controller_list = []
        self.vbox = widgets.VBox([])
        self.add_kwargs(kwargs, slider_formats, play_buttons, play_button_pos)

    def add_kwargs(self, kwargs, slider_formats=None, play_buttons=False, play_button_pos="right"):
        """
        If you pass a redundant kwarg it will just be overwritten
        maybe should only raise a warning rather than an error?

        need to implement matplotlib widgets
        also a big question is how to dynamically update the display of matplotlib widgets.
        """
        if isinstance(play_buttons, bool):
            has_play_button = defaultdict(lambda: play_buttons)
        elif isinstance(play_buttons, defaultdict):
            has_play_button = play_buttons
        elif isinstance(play_buttons, dict):
            has_play_button = defaultdict(lambda: False, play_buttons)
        elif isinstance(play_buttons, Iterable) and all([isinstance(p, str) for p in play_buttons]):
            has_play_button = defaultdict(
                lambda: False, dict(zip(play_buttons, [True] * len(play_buttons)))
            )
        else:
            has_play_button = play_buttons
        if slider_formats is not None:
            slider_formats = create_slider_format_dict(slider_formats, True)
            for k, v in slider_formats.items():
                self.slider_format_strings[k] = v
        for k, v in kwargs.items():
            if k in self.params:
                raise ValueError("can't overwrite an existing param in the controller")
            # create slider
            self.params[k], control = kwarg_to_ipywidget(
                k,
                v,
                partial(self.slider_updated, key=k),
                self.slider_format_strings[k],
                play_button=has_play_button[k],
                play_button_pos=play_button_pos,
            )
            if control:
                self.controls[k] = control
                self.indices
                self.vbox.children = list(self.vbox.children) + [control]

    def slider_updated(self, change, key, values):
        """
        gotta also give the indices in order to support hyperslicer without horrifying contortions
        """
        with self.out:
            if values is None:
                self.params[key] = change["new"]
            else:
                self.params[key] = values[change["new"]]
            self.indices[key] = change["new"]
            for f, params in self._update_funcs[key]:
                ps = {}
                idxs = {}
                for k in params:
                    ps[k] = self.params[k]
                    idxs[k] = self.indices[k]
                f(params=ps, indices=idxs)
            for f in self.figs[key]:
                f.canvas.draw_idle()

    def register_function(self, f, fig, params=None):
        """
        if params is None use the entire current set of params
        """
        if params is None:
            params = self.params.keys()
        # listify to ensure it's not a reference to dicts keys
        # bc thats mutable
        params = list(params)
        for p in params:
            self._update_funcs[p].append((f, params))
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

    def _ipython_display_(self):
        ipy_display(self.vbox)


def gogogo_controls(
    kwargs, controls, display_controls, slider_formats, play_buttons, play_button_pos
):
    if controls:
        if isinstance(controls, tuple):
            # it was indexed by the user when passed in
            extra_keys = controls[1]
            controls = controls[0]
            controls.add_kwargs(kwargs, slider_formats, play_buttons, play_button_pos)
            params = {k: controls.params[k] for k in list(kwargs.keys()) + list(extra_keys)}
        else:
            controls.add_kwargs(kwargs, slider_formats, play_buttons, play_button_pos)
            params = controls.params
    else:
        out = widgets.Output()
        controls = Controls(
            out,
            slider_formats=slider_formats,
            play_buttons=play_buttons,
            play_button_pos=play_button_pos,
            **kwargs
        )
        params = controls.params
        if display_controls:
            display(controls)
    return controls, params
