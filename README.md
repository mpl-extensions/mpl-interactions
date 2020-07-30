# ipympl-interactions
[![Documentation Status](https://readthedocs.org/projects/ipympl-interactions/badge/?version=latest)](https://ipympl-interactions.readthedocs.io/en/latest/?badge=latest)

<img src=docs/images/short-interactive.gif height=200>  <img src=docs/images/tight-layout-heatmap-slicer.gif height=200>

This library provides a different approach than `ipywidgets.interact` to make an interactive matplotlib plot. When using `interact` you are responsible for:
1. Defining the function to plot `f(x,...) => y`
2. Handling the plotting logic (`plt.plot`, `fig.cla`, `ax.set_ylim`, etc)

In contrast `ipympl-interactions` accepts functions in a more mathematical sense, you only need provide `f(x, ...) => y` and the plotting and updating boilerplate are handled for you.


`ipympl-interaction` has three main goals:
1. Make it easier to make an interactive line plot
    - Accept numpy arrays as arugments. They will become sliders with the value displayed rather than the index (contrast to selectionSlider)
    - Handle all the logic for updating the plot - you are only responsible for defining the function you want to plot
2. Provide a very niche (but very cool) way to compare 2D heatmaps
3. Provide other useful matplotlib interactions
    - scroll to zoom
    - middle click to pan
    - `ioff` as a context manager
4. Eventually
    - interactive_plot2D


## Installation
```bash
git clone https://github.com/ianhi/ipympl-interactions.git
cd ipympl-interactions
pip install .
# soon to be published on pypi
```
If you use jupyterlab make sure you follow the full instructions in the ipympl readme https://github.com/matplotlib/ipympl#install-the-jupyterlab-extension in particular installing jupyterlab-manager.


## Documentation
https://ianhi.github.io/ipympl-interactions/_build/html/Installation.html

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