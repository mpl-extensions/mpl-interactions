from numpy import asarray, abs, argmin
from matplotlib.pyplot import figure as mpl_figure
from matplotlib.pyplot import rcParams, install_repl_displayhook, uninstall_repl_displayhook
from matplotlib import is_interactive, interactive
from collections.abc import Iterable

__all__ = [
    'figure',
    'nearest_idx',
    'ioff'
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

def figure(figsize=1,*args,**kwargs):
    if not isinstance(figsize, Iterable):
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