# mpl-interactions
[![Documentation Status](https://readthedocs.org/projects/mpl-interactions/badge/?version=latest)](https://mpl-interactions.readthedocs.io/en/latest/?badge=latest)[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ianhi/mpl-interactions/master?urlpath=lab) (warning: this will be laggy)

<img src=https://raw.githubusercontent.com/ianhi/mpl-interactions/master/docs/images/short-interactive.gif height=200>  <img src=https://raw.githubusercontent.com/ianhi/mpl-interactions/master/docs/images/heatmap_slicer.gif height=200>

This library provides helpful ways to interact with Matplotlib plots. There are three submodules:

**jupyter**

Provides a different approach than `ipywidgets.interact` to making sliders that affect a matplotlib plot. When using `interact` you are responsible for:
1. Defining the function to plot `f(x,...) => y`
2. Handling the plotting logic (`plt.plot`, `fig.cla`, `ax.set_ylim`, etc)

In contrast, with `mpl-interactions` you only need provide `f(x, ...) => y` and the plotting and updating boilerplate are handled for you.

```python
x = np.linspace(0,6,100)
beta = np.linspace(0,5*np.pi)
def f(x, beta):
    return np.sin(x*4+beta)
interactive_plot(f, x=x, beta=beta)
```

While this will work with any backend except for `%matplotlib inline` you should try to use these with `%matplotlib ipympl` which uses [ipympl](https://github.com/matplotlib/ipympl) as this will have the best performance and UX in a notebook.


**generic**

Ways to interact with matplotlib that will work outside of a jupyter notebook and should work equally well with any backend.
1. A very niche (but very cool) way to compare 2D heatmaps
2. scroll to zoom
3. middle click to pan

**utils**

utility functions that make things just the little bit easier

1. `ioff` as a context manager

```python
from mpl_interactions.utils import ioff
with ioff:
    # interactive mode will be off
    fig = plt.figure()
    # other stuff
# interactive mode will be on
```
2. `figure` that accepts a scalar for `figsize` - this will scale the default dimensions
```python
from mpl_interactions.utils import figure
fig = figure(3)
# the default figsize is [6.4, 4.8], this figure will have figsize = [6.4*3, 4.8*3]
```

3. `nearest_idx` - avoid ever having to write `np.argmin(np.abs(arr - value))` again.


## Installation
```bash
pip install mpl_interactions

# if using jupyterlab
conda install -c conda-forge nodejs>10
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```
If you use jupyterlab make sure you follow the full instructions in the ipympl readme https://github.com/matplotlib/ipympl#install-the-jupyterlab-extension in particular installing jupyterlab-manager.
## Contributing / feature requests / roadmap

I use the Github [issues](https://github.com/ianhi/mpl-interactions/issues) to keep track of ideas I have, looking through those should serve as a roadmap of sorts. For the most part I add to the library when I create a function that is useful for the science I am doing. If you create somethign that seems useful a PR would be most welcome so we can share it easily with more people. I'm also open to feature requests if you have an idea.

## Documentation
Definitely a work in progress - I would recommend checking out the examples directory for now.
https://mpl-interactions.readthedocs.io/en/latest/

## Examples with GIFs!
Tragically neither github nor the sphinx documentation render the actual moving plots so here are gifs of the functions. The code for these can be found in the notebooks in the examples directory.


### interactive_plot
Easily make a line plot interactive:
![](docs/images/interactive-plot.gif)


### heatmap_slicer
Compare vertical and horizontal slices across multiple heatmaps:
![](docs/images/heatmap_slicer.gif)


### scrolling zoom + middle click pan
![](docs/images/zoom-and-pan.gif)