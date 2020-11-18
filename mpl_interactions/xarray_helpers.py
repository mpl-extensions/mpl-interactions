import numpy as np

def choose_fmt_str(dtype=None):
    if np.issubdtype(dtype,'float'):
        fmt = r'{:0.2f}'
    elif np.issubdtype(dtype,'int'):
        fmt = r'{:d}'
    else:
        fmt =r'{:}'
    return fmt


def choose_datetime_nonsense(arr, timeunit='m'):
    if np.issubdtype(arr.dtype, 'datetime64'):
        #print('datetime')
        out = arr.astype(f'datetime64[{timeunit}]')
    elif np.issubdtype(arr.dtype, 'timedelta64'):
        out = arr.astype(f'timedelta64[{timeunit}]').astype(int)
    else:
        out = arr
    return out


def get_hs_axes(xarr, is_color_image=False, timeunit='m'):
    if not is_color_image:
        dims = xarr.dims[:-2]
    else: 
        dims = xarr.dims[:-3]
    coords_list = [choose_datetime_nonsense(xarr.coords[d].values, timeunit=timeunit) for d in dims]
    #print(coords_list)
    axes = zip(dims, coords_list)
    return list(axes)


def get_hs_extent(xarr, is_color_image=False):
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
    if not is_color_image:
        dims = xarr.dims[:-2]
    else:
        dims = xarr.dims[:-3]
    fmt_strs = {}
    for i,d in enumerate(dims):
        fmt_strs[d] = choose_fmt_str(xarr[d].dtype)
        if units is not None and units[i] is not None:
            try:
                fmt_strs[d] += " {}".format(units[i])
            except: continue
    return fmt_strs