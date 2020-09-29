import matplotlib.pyplot as plt
import numpy as np
import pytest

from mpl_interactions.helpers import update_datalim_from_bbox, update_datalim_from_xy


def test_bbox_update():
    fig, ax = plt.subplots()
    x = np.arange(10) / 10
    ax.plot(x)
    scat = ax.scatter([0], [0])
    x_scat = np.arange(3)
    y_scat_big = x_scat * 5
    y_scat_small = x_scat * 2
    scat.set_offsets(np.c_[x_scat, y_scat_big])
    update_datalim_from_bbox(ax, scat.get_datalim(ax.transData))
    assert ax.dataLim.bounds == (0, 0, 9, 10)
    scat.set_offsets(np.c_[x_scat, y_scat_small])
    update_datalim_from_bbox(ax, scat.get_datalim(ax.transData))
    assert ax.dataLim.bounds == (0, 0, 9, 10)
    scat.set_offsets(np.c_[x_scat, y_scat_big])
    update_datalim_from_bbox(ax, scat.get_datalim(ax.transData))
    assert ax.dataLim.bounds == (0, 0, 9, 10)
    scat.set_offsets(np.c_[x_scat, y_scat_small])
    update_datalim_from_bbox(ax, scat.get_datalim(ax.transData), stretch_y=False)
    assert ax.dataLim.bounds == (0.0, 0.0, 9.0, 4.0)


def test_xy_update():
    fig, ax = plt.subplots()
    x = np.arange(10) / 10
    ax.plot(x)
    scat = ax.scatter([0], [0])
    x_scat = np.arange(3)
    y_scat_big = x_scat * 5
    y_scat_small = x_scat * 2
    update_datalim_from_xy(ax, x_scat, y_scat_big)
    assert ax.dataLim.bounds == (0, 0, 9, 10)
    scat.set_offsets(np.c_[x_scat, y_scat_small])
    update_datalim_from_xy(ax, x_scat, y_scat_small)
    assert ax.dataLim.bounds == (0, 0, 9, 10)
    update_datalim_from_xy(ax, x_scat, y_scat_big)
    assert ax.dataLim.bounds == (0, 0, 9, 10)
    update_datalim_from_xy(ax, x_scat, y_scat_small, stretch_y=False)
    assert ax.dataLim.bounds == (0.0, 0.0, 9.0, 4.0)
