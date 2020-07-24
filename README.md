# Jupyter-Jukebox

A collection of handy one off functions when working in jupyterlab.

## Installation

This very much depends on having [jupyter-matplotlib](https://github.com/matplotlib/jupyter-matplotlib) installed. So you will first need to install that and then install this library

```bash
conda install -c conda-forge ipympl

conda install nodejs
jupyter labextension install @jupyter-widgets/jupyterlab-manager
jupyter labextension install jupyter-matplotlib
git clone https://github.com/ianhi/jupyter-jukebox.git .
cd jupyter-jukebox
python setup.py install
```
## Documentation
https://ianhi.github.io/jupyter-jukebox/_build/html/Installation.html

## Examples with GIFs!
Tragically neither github nor the sphinx documentation render the actual moving plots so here are gifs of the functions. The code for these can be found in the notebooks in the examples directory.


### single_param_interact
Easily make a line plot interactive:
![](docs/images/single_param_interact.gif)


### heatmap_slicer
Compare vertical and horizontal slices across multiple heatmaps:
![](docs/images/heatmap_slicer.gif)
