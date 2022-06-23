# mpl_interactions: Easy interactive Matplotlib plots

mpl_interactions' aims to make it as easy as possible to create responsive [Matplotlib](http://www.matplotlib.org) plots. In particular, you can:

- Better understand a function's change with respect to a parameter.
- Visualize your data interactively.

To achieve this, `mpl_interactions` provides:

- A way to control the output of pyplot functions (e.g. {func}`~matplotlib.pyplot.plot` and {func}`~matplotlib.pyplot.hist`) with sliders.
- A function to compare horizontal and vertical slices of heatmaps.
- A function allowing zooming using the scroll wheel.

## Installation

To install, simply run:

```
pip install mpl_interactions
```

To also install version of [`ipympl`](https://github.com/matplotlib/ipympl) and {doc}`ipywidgets <ipywidgets:index>` that are known to work install the optional jupyter dependencies by running:

```
pip install mpl_interactions[jupyter]
```

Further instructions for installation from JupyterLab can be found on the {doc}`install` page.

## Getting Help

If you have a question on using this library a great place to ask it is: <https://discourse.matplotlib.org/c/3rdparty/18>. Feel free to mention [`@ianhi`](https://github.com/ianhi) in your post there.

## Basic example

To control a plot with a slider:

```python
# if running this code in a Jupter notbeook or JupyterLab
%matplotlib ipympl
```

```python
import mpl_interactions.ipyplot as iplt
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, np.pi, 100)
tau = np.linspace(0.5, 10, 100)

def f1(x, tau, beta):
    return np.sin(x * tau) * x * beta
def f2(x, tau, beta):
    return np.sin(x * beta) * x * tau


fig, ax = plt.subplots()
controls = iplt.plot(x, f1, tau=tau, beta=(1, 10, 100), label="f1")
iplt.plot(x, f2, controls=controls, label="f2")
_ = plt.legend()
plt.show()
```

**If you are in a Jupyter Notebook the output will look like this:**

```{image} _static/images/front-page.gif

```

**and from a script or ipython the output will use Matplotlib sliders:**

```{image} _static/images/front-page-mpl-widgets.gif

```

## Matplotlib backends

mpl_interactions' functions will work in any Matplotlib backend. In most backends they will use the Matplotlib Slider and Radio button widgets. However, if you are working in a Jupyter notebook the [`ipympl`](https://github.com/matplotlib/ipympl) backend then ipywidgets sliders will be used as the controls. Further discussion of the behavior as a function of backend can be found on the {doc}`backends` page.

_Follow the links below for further information on installation, functions, and plot examples._

```{toctree}
:maxdepth: 3

install
backends
comparison
API <api/mpl_interactions>
gallery/index
contributing
```

```{toctree}
:caption: Tutorials
:maxdepth: 1

examples/usage.ipynb
examples/context.ipynb
examples/mpl-sliders.ipynb
examples/custom-callbacks.ipynb
examples/animations.ipynb
examples/range-sliders.ipynb
examples/scalar-arguments.ipynb
examples/text-annotations.ipynb
examples/tidbits.md
```

```{toctree}
:caption: Specific Functions
:maxdepth: 1

examples/hyperslicer.ipynb
examples/plot.ipynb
examples/scatter.ipynb
examples/imshow.ipynb
examples/hist.ipynb
examples/scatter-selector.ipynb
examples/image-segmentation.ipynb
examples/zoom-factory.ipynb
examples/heatmap-slicer.ipynb
```

```{toctree}
:caption: Showcase
:maxdepth: 1

examples/lotka-volterra.ipynb
examples/rossler-attractor.ipynb
```

### Indices and Tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
