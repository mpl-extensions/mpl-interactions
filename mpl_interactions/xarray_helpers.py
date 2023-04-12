import numpy as np

from .helpers import choose_fmt_str


def choose_datetime_nonsense(arr, timeunit="m"):
    """
    Try to do something reasonable to datetimes and timedeltas.

    Parameters
    ----------
    arr : np.array
        Array with values to be formatted.
    timeunit : str, default: m
        Truncation level for datetime and timedelta axes.

    Returns
    -------
    out : np.array
        Array modified to format decently in a slider.

    """
    if np.issubdtype(arr.dtype, "datetime64"):
        out = arr.astype(f"datetime64[{timeunit}]")
    elif np.issubdtype(arr.dtype, "timedelta64"):
        out = arr.astype(f"timedelta64[{timeunit}]").astype(int)
    else:
        out = arr
    return out


def get_hs_axes(xarr, is_color_image=False, timeunit="m"):
    """Read the dims and coordinates from an xarray and construct the axes argument for hyperslicer.

    Parameters
    ----------
    xarr : xarray.DataArray
        DataArray being viewed with hyperslicer
    is_color_image : bool, default False
        Whether the individual images of the hyperstack are color images.
    timeunit : str, default "m"
        Truncation level for datetime and timedelta axes.

    Returns
    -------
    axes : list
        axes kwarg for hyperslicer

    """
    if not is_color_image:
        dims = xarr.dims[:-2]
    else:
        dims = xarr.dims[:-3]
    coords_list = [choose_datetime_nonsense(xarr.coords[d].values, timeunit=timeunit) for d in dims]
    axes = zip(dims, coords_list)
    return list(axes)


def get_hs_extent(xarr, is_color_image=False, origin="upper"):
    """Read the "YX" coordinates of an xarray.DataArray to set extent of image for imshow.

    Parameters
    ----------
    xarr : xarray.DataArray
        DataArray being viewed with hyperslicer
    is_color_image : bool, default False
        Whether the individual images of the hyperstack are color images.
    origin : {'upper', 'lower'}
        Whether the imshow origin is in the top left or bottom left
        see: https://matplotlib.org/stable/tutorials/intermediate/imshow_extent.html

    Returns
    -------
    extent : list
        Extent argument for imshow.

    """
    if not is_color_image:
        dims = xarr.dims[-2:]
    else:
        dims = xarr.dims[-3:-1]

    # the reversal is because imshow transposes the array it receives
    dims = dims[::-1]
    extent = []
    for d in dims:
        vals = xarr[d].values
        # offset by 0.5 in order to exactly match imshow
        extent.append(vals.min() - 0.5)
        extent.append(vals.max() + 0.5)
    if origin == "upper":
        # for origin==upper imshow puts the small values at the top
        extent[2], extent[3] = extent[3], extent[2]
    return extent


def get_hs_fmts(xarr, units=None, is_color_image=False):
    """Get appropriate slider format strings from xarray coordinates.

    Parameters
    ----------
    xarr : xarray.DataArray
        DataArray being viewed with hyperslicer
    units : array-like
        Units to append to end of slider value. Must have the same length
        as number of non-image dimensions in xarray.
    is_color_image : bool, default False
        Whether the individual images of the hyperstack are color images.

    Returns
    -------
    fmt_strings : dict
        Slider format strings for hyperslicer (or other mpl-interactions?)
    """
    if not is_color_image:
        dims = xarr.dims[:-2]
    else:
        dims = xarr.dims[:-3]
    fmt_strs = {}
    for i, d in enumerate(dims):
        fmt_strs[d] = choose_fmt_str(xarr[d].dtype)
        if units is not None and units[i] is not None:
            try:
                fmt_strs[d] += f" {units[i]}"
            except KeyError:
                continue
    return fmt_strs
