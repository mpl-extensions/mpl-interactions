import matplotlib.cbook as cbook
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib import __version__ as mpl_version
from packaging import version

from mpl_interactions.generic import *

if version.parse(mpl_version) >= version.parse("3.3"):
    mplsuffix = ""
else:
    mplsuffix = 32


@pytest.mark.mpl_image_compare(style="default", filename=f"test_heatmap_slicer{mplsuffix}.png")
def test_heatmap_slicer():
    x = np.linspace(0, np.pi, 100)
    y = np.linspace(0, 10, 200)
    X, Y = np.meshgrid(x, y)
    data1 = np.sin(X) + np.exp(np.cos(Y))
    data2 = np.cos(X) + np.exp(np.sin(Y))
    fig, axes = heatmap_slicer(
        x,
        y,
        (data1, data2),
        slices="both",
        heatmap_names=("dataset 1", "dataset 2"),
        labels=("Some wild X variable", "Y axis"),
        interaction_type="move",
        cmap="plasma",
    )
    return fig


@pytest.mark.mpl_image_compare(style="default")
def test_image_segmentation():
    with cbook.get_sample_data("ada.png") as image_file:
        image = plt.imread(image_file)
    try:
        mask = np.load("../../examples/ada-mask.npy")
    except FileNotFoundError:
        mask = np.load("examples/ada-mask.npy")
    preloaded = image_segmenter(image, nclasses=3, mask=mask)

    return preloaded.fig
