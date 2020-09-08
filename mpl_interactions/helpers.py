import numpy as np

__all__ = [
    "decompose_bbox",
    "update_datalim_from_xy",
    "update_datalim_from_bbox",
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
