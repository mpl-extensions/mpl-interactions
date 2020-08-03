# ipympl-interactions
[![Documentation Status](https://readthedocs.org/projects/ipympl-interactions/badge/?version=latest)](https://ipympl-interactions.readthedocs.io/en/latest/?badge=latest)

<img src=docs/images/short-interactive.gif height=200>  <img src=docs/images/tight-layout-heatmap-slicer.gif height=200>

The main purpose of this library is to provide a different approach than `ipywidgets.interact` to making an interactive matplotlib plot. When using `interact` you are responsible for:
1. Defining the function to plot `f(x,...) => y`
2. Handling the plotting logic (`plt.plot`, `fig.cla`, `ax.set_ylim`, etc)

In contrast, with `mpl-interactions` you only need provide `f(x, ...) => y` and the plotting and updating boilerplate are handled for you.

Additionally there are other useful functions for greater interactivity with matplolib. These are not necessarily dependent on `ipympl` and will probably work in all backends except for inline backends.
Currently these extra goodies are:
1. A very niche (but very cool) way to compare 2D heatmaps
2. scroll to zoom
3. middle click to pan
4. `ioff` as a context manager
5. `figure` that accepts a scalars as `figsize` that will scale the default dimensions

Future functions:
1. interactive_plot2D
2. Others?
    - As I discover a need for more tools I will create them and have them live here. 
    - If you have an idea feel free to add it :)


## Installation
```bash
git clone https://github.com/ianhi/mpl-interactions.git
cd ipympl-interactions
pip install .
# hopefully to be published on pypi soon
```
If you use jupyterlab make sure you follow the full instructions in the ipympl readme https://github.com/matplotlib/ipympl#install-the-jupyterlab-extension in particular installing jupyterlab-manager.


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