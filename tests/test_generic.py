from os.path import dirname, realpath

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from mpl_interactions.generic import heatmap_slicer, hyperslicer, image_segmenter


# just smoketests here. hadn't set image comparison styling properly
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


def test_image_segmentation():
    image = plt.imread(
        "https://github.com/matplotlib/matplotlib/raw/v3.3.0/lib/matplotlib/mpl-data/sample_data/ada.png"
    )
    script_dir = realpath(dirname(__file__))
    mask = np.load(f"{script_dir}/../docs/examples/ada-mask.npy")
    preloaded = image_segmenter(image, nclasses=3, mask=mask)

    return preloaded.fig


def test_xr_hyperslicer_extents():
    arr = np.zeros([10, 150, 200])
    arr[:, 50:100, 50:150] = 1

    arr_xr = xr.DataArray(arr, dims=("whatever", "y", "x"))

    _, axs = plt.subplots(2, 2)

    axs[0, 0].imshow(arr[0], origin="upper")
    hyperslicer(arr_xr, ax=axs[0, 1], origin="upper")

    axs[1, 0].imshow(arr[0], origin="lower")
    hyperslicer(arr_xr, ax=axs[1, 1], origin="lower")
    assert axs[0, 0].get_xlim() == axs[0, 1].get_xlim()
    assert axs[0, 0].get_ylim() == axs[0, 1].get_ylim()

    assert axs[1, 0].get_xlim() == axs[1, 1].get_xlim()
    assert axs[1, 0].get_ylim() == axs[1, 1].get_ylim()


def test_duplicate_axis_names():
    plt.subplots()
    img_stack = np.random.rand(5, 512, 512)

    with hyperslicer(img_stack):
        hyperslicer(img_stack)
