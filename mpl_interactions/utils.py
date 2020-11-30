from collections.abc import Iterable

from matplotlib import interactive, is_interactive
from matplotlib.pyplot import figure as mpl_figure
from matplotlib.pyplot import install_repl_displayhook, rcParams, uninstall_repl_displayhook
from numpy import abs, argmin, asarray, take
import numpy as np

__all__ = [
    "figure",
    "nearest_idx",
    "ioff",
    "indexer",
]


class _ioff_class:
    """
    A context manager for turning interactive mode off. Now
    that https://github.com/matplotlib/matplotlib/pull/17371 has been merged this will
    be availiable via ``plt.ioff`` starting in Matplotlib 3.4
    """

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


def figure(figsize=1, *args, **kwargs):
    """
    Matplotlib figure but a scalar figsize will multiply rcParams figsize.

    Examples
    --------

    The figure size of the two figures will be equivalent::

        plt.rcParams['figure.figsize'] = [6.4, 4.8]
        fig1 = figure(2)
        fig2 = plt.figure(figsize=(12.8, 9.6))
    """
    if not isinstance(figsize, Iterable) and figsize is not None:
        figsize = [figsize * x for x in rcParams["figure.figsize"]]
    return mpl_figure(figsize=figsize, *args, **kwargs)


def nearest_idx(array, value, axis=None):
    """
    Return the index of the array that is closest to value. Equivalent to
    ``np.argmin(np.abs(array-value), axis=axis)``

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
    return argmin(abs(array - value), axis=axis)


def indexer(arr, index_name=None, axis=0):
    """
    Utility function for when you want to index an array as part of an interactive function.
    For example: ``iplt.plot(indexor(arr), idx = np.arange(5))``

    Parameters
    ----------
    arr : arraylike
        The array to be indexed
    index_name : str, default: None
        The name of the variable the returned function should expect to receive.
        If ``None`` then the function will check for ``idx``, ``index``, ``ind``, and ``indx``.
    axis : int
        which axis to index, default to first axis

    Returns
    -------
    f : function
        Function to be passed as an argument to an interactive plotting function
    """

    if index_name is None:
        idxs = ["idx", "index", "indx", "ind"]
    else:
        idxs = [index_name]

    def f(*args, **kwargs):
        for i in idxs:
            if i in kwargs:
                return np.take(arr, kwargs[i], axis=axis)
        raise ValueError(f"indexer did not receive a kwarg with a name in {idxs}")

    return f
