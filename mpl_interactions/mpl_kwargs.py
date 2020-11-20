# this is a list of options to Line2D partially taken from
# https://github.com/matplotlib/matplotlib/blob/f9d29189507cfe4121a231f6ab63539d216c37bd/lib/matplotlib/lines.py#L271
# many of these can also be made into functions
plot_kwargs_list = [
    "alpha",
    "linewidth",
    "linestyle",
    "color",
    "marker",
    "markersize",
    "markeredgewidth",
    "markeredgecolor",
    "markerfacecolor",
    "markerfacecoloralt",
    "fillstyle",
    "antialiased",
    "dash_capstyle",
    "solid_capstyle",
    "dash_joinstyle",
    "solid_joinstyle",
    "pickradius",
    "drawstyle",
    "markevery",
    "label",
]

imshow_kwargs_list = [
    "cmap",
    "norm",
    "aspect",
    "interpolation",
    "alpha",
    "vmin",
    "vmax",
    "origin",
    "extent",
    "filternorm",
    "filterrad",
    "resample",
    "url",
]
Text_kwargs_list = [
    "agg_filter",
    "alpha",
    "animated",
    "backgroundcolor",
    "bbox",
    "clip_box",
    "clip_on",
    "clip_path",
    "color",
    "c",
    "contains",
    "figure",
    "fontfamily",
    "family",
    "fontproperties",
    "font_properties",
    "fontsize",
    "size",
    "fontstretch",
    "stretch",
    "fontstyle",
    "style",
    "fontvariant",
    "variant",
    "fontweight" "weight",
    "gid",
    "horizontalalignment" "ha",
    "in_layout",
    "label",
    "linespacing",
    "multialignment" "ma",
    "path_effects",
    "picker",
    "position",
    "rasterized",
    "rotation",
    "rotation_mode",
    "sketch_params",
    "snap",
    "text",
    "transform",
    "url",
    "usetex",
    "verticalalignment" "va",
    "visible",
    "wrap",
    "x",
    "y",
    "zorder",
]


def kwarg_popper(kwargs, mpl_kwargs):
    """
    This will not modify kwargs for you.

    Usage
    -----

    kwargs, plot_kwargs = kwarg_popper(kwargs, plot_kwargs_list)
    """
    kwargs = dict(kwargs)
    passthrough = {}
    for k in mpl_kwargs:
        if k in kwargs:
            passthrough[k] = kwargs.pop(k)
    return kwargs, passthrough
