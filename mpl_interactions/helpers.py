from collections.abc import Callable
from numbers import Number

import numpy as np
from matplotlib import get_backend
from numpy.distutils.misc_util import is_sequence

__all__ = [
    "decompose_bbox",
    "update_datalim_from_xy",
    "update_datalim_from_bbox",
    "is_jagged",
    "broadcast_to",
    "prep_broadcast",
    "broadcast_arrays",
    "broadcast_many",
    "notebook_backend",
    "callable_else_value",
]


def decompose_bbox(bbox):
    return bbox.x0, bbox.y0, bbox.x1, bbox.y1


def _update_limits(ax, x0, y0, x1, y1, x0_, y0_, x1_, y1_, stretch_x, stretch_y):
    if stretch_x:
        x0 = np.min([x0, x0_])
        x1 = np.max([x1, x1_])
    else:
        x0 = x0_
        x1 = x1_

    if stretch_y:
        y0 = np.min([y0, y0_])
        y1 = np.max([y1, y1_])
    else:
        y0 = y0_
        y1 = y1_
    # now relim and always take the maximum extent
    ax.relim()
    ax.dataLim.update_from_data_xy(np.asarray([[x0, y0], [x1, y1]]), ignore=False)


def update_datalim_from_bbox(ax, bbox, stretch_x=True, stretch_y=True):
    _update_limits(ax, *decompose_bbox(ax.dataLim), *decompose_bbox(bbox), stretch_x, stretch_y)


def update_datalim_from_xy(ax, x, y, stretch_x=True, stretch_y=True):
    """
    current : ax.dataLim
    x : array
        the new x datavalues to include
    y : array
        the new y datavalues to include
    """
    # this part bc scatter not affect by relim
    # so need this to keep stretchign working for scatter
    x0_ = np.min(x)
    x1_ = np.max(x)
    y0_ = np.min(y)
    y1_ = np.max(y)
    _update_limits(ax, *decompose_bbox(ax.dataLim), x0_, y0_, x1_, y1_, stretch_x, stretch_y)


def is_jagged(seq):
    """
    checks for jaggedness up to two dimensions
    don't need more because more doesn't make any sense for this library
    need this bc numpy is unhappy about being passed jagged arrays now :(
    """
    lens = []
    if is_sequence(seq):
        for y in seq:
            if isinstance(y, Number) or isinstance(y, Callable):
                lens.append(0)
                continue
            try:
                lens.append(len(y))
            except TypeError:
                return True
        if not all(lens[0] == l for l in lens):
            return True
    return False


def prep_broadcast(arr):
    if arr is None:
        return np.atleast_1d(None)
    if is_jagged(arr):
        arr = np.asarray(arr, dtype=np.object)
    elif isinstance(arr, Number) or isinstance(arr, Callable):
        arr = np.atleast_1d(arr)
    else:
        arr = np.atleast_1d(arr)
        if np.issubdtype(arr.dtype, np.number) and arr.ndim == 1:
            arr = arr[None, :]
    return arr


def broadcast_to(arr, to_shape, names):
    """
    happily this doesn't increase memory footprint e.g:
    import sys
    xs = np.arange(5)
    print(sys.getsizeof(xs.nbytes))
    print(sys.getsizeof(np.broadcast_to(xs, (19000, xs.shape[0]))))

    gives 28 and 112. Note 112/28 != 19000
    """
    if arr.shape[0] == to_shape[0]:
        return arr

    if arr.ndim > 1:
        if arr.shape[0] == 1:
            return np.broadcast_to(arr, (to_shape[0], *arr.shape[1:]))
        else:
            raise ValueError(f"can't broadcast {names[0]} {arr.shape} onto {names[1]} {to_shape}")
    elif arr.shape[0] == 1:
        return np.broadcast_to(arr, (to_shape[0],))
    else:
        raise ValueError(f"can't broadcast {names[0]} {arr.shape} onto {names[1]} {to_shape}")


def broadcast_arrays(*args):
    """
    This is a modifed version the numpy `broadcast_arrays` function
    that uses a verion of _broadcast_to that only considers the first axis
    """

    shapes = [array.shape[0] for (array, name) in args]
    idx = np.argmax(shapes)
    if all([shapes[0] == s for s in shapes]):
        # case where nothing needs to be broadcasted.
        return [array for (array, name) in args]
    return [broadcast_to(array, args[idx][0].shape, [name, args[idx][1]]) for (array, name) in args]


def broadcast_many(*args):
    """
    helper to call prep_broadcast followed by broadcast arrays
    keep as a separate function to keep the idea of broadcast_arrays the same
    """
    return broadcast_arrays(*[(prep_broadcast(arg[0]), arg[1]) for arg in args])


def notebook_backend():
    """
    returns True if the backend is ipympl or nbagg, otherwise False
    """
    backend = get_backend().lower()
    if "ipympl" in backend:
        return True
    elif backend == "nbAgg".lower():
        return True
    return False


def callable_else_value(arg, params):
    if isinstance(arg, Callable):
        return arg(**params)
    return arg
