import numpy as np
from .helpers import choose_fmt_str


def choose_datetime_nonsense(arr, timeunit="m"):
    """
    Try to do something reasonable to datetimes and timedeltas.

    Parameters
    ----------

    arr : np.array
        Array with values to be formatted.

    Returns
    -------

    out : np.array
        Array modified to format decently in a slider.

    """

    if np.issubdtype(arr.dtype, "datetime64"):
        # print('datetime')
        out = arr.astype(f"datetime64[{timeunit}]")
    elif np.issubdtype(arr.dtype, "timedelta64"):
        out = arr.astype(f"timedelta64[{timeunit}]").astype(int)
    else:
        out = arr
    return out


def get_hs_axes(xarr, is_color_image=False, timeunit="m"):
    """
    Read the dims and coordinates from an xarray and construct the
    axes argument for hyperslicer. Called internally by hyperslicer.

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
    # print(coords_list)
    axes = zip(dims, coords_list)
    return list(axes)


def get_hs_extent(xarr, is_color_image=False):
    """
    Read the "XY" coordinates of an xarray.DataArray to set extent of image for
    imshow.

    Parameters
    ----------

    xarr : xarray.DataArray
        DataArray being viewed with hyperslicer

    is_color_image : bool, default False
        Whether the individual images of the hyperstack are color images.

    Returns
    -------
    extent : list
        Extent argument for imshow. [d0_min, d0_max, d1_min, d1_max]

    """

    if not is_color_image:
        dims = xarr.dims[-2:]
    else:
        dims = xarr.dims[-3:-1]
    extent = []
    for d in dims:
        vals = xarr[d].values
        extent.append(vals.min())
        extent.append(vals.max())
    return extent


def get_hs_fmts(xarr, units=None, is_color_image=False):
    """
    Get appropriate slider format strings from xarray coordinates
    based the dtype of corresponding values.

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
                fmt_strs[d] += " {}".format(units[i])
            except:
                continue
    return fmt_strs
