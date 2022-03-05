from os.path import dirname, realpath

import matplotlib.pyplot as plt
import numpy as np

from mpl_interactions.generic import heatmap_slicer, image_segmenter


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
