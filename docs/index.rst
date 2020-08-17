Welcome to mpl-interactions' documentation!
===========================================


mpl-interactions' design creates helpful ways of interacting with `Matplotlib <http://www.matplotlib.org>`_ plots. 
The library provides three key types of utility for easy-to-use, accessible infographics. These modules 
include Generic, Utils, and Jupyter.

mpl-interactions' functions are written to use with `ipympl <https://github.com/matplotlib/ipympl>`_, the backend 
designed for use in Jupyter notebooks. For optimal performance, ensure you set the backend with `%matplotlib ipympl`. 
That said, these functions will also work with any interactive backend (e.g. `%matplotlib qt5`).

Generic
^^^^^^^
Provides a way to interact with Matplotlib that will function outside of a Jupyter notebook. 
Three new features are created:

* A very niche way to compare 2D heatmaps 
* Scroll to zoom
* Middle click to pan

Again, this module is also compatible with any backend. 

Utils
^^^^^
This module includes utility functions to make user experience just that little bit easier. 

* `ioff` as a context manager

.. code-block:: python

   from mpl_interactions.utils import ioff
   with ioff:
      # interactive mode will be off
      fig = plt.figure()
      # other stuff
   # interactive mode will be on

* `figure` that accepts a scalar for `figsize` (this will scale the default dimensions)

.. code-block:: python

   from mpl_interactions.utils import figure
   fig = figure(3)
   # the default figsize is [6.4, 4.8], this figure will have figsize = [6.4 *3, 4.8 *3]

* `nearest_idx` allows you to avoid ever having to write `np.argmin(np.abs(arr - value))` ever again

Jupyter
^^^^^^^
Provides a different approach than `ipywidgets.interact` for making sliders that affect a Matplotlib plot. 
When using `ipywidgets.interact` you are responsible for:

1. Defining the function to plot `f(x, ...) => y`
2. Handling the plotting logic (`plt.plot`, `fig.cla`, `ax.set_ylim`, etc.)

In contrast, with mpl-interactions, you only need to provide `f(x, ...) => y` to have the plotting and 
updating boilerplate handled for you. 

.. code-block:: python

   x = np.linspace(0,6,100)
   beta = np.linspace(0,5*np.pi)
   def f(x, beta):
      return np.sin(x*4+beta)
   interactive_plot(f, x=x, beta=beta)

Follow the links below for further information on installation, functions, and plot examples.

.. toctree::
   :maxdepth: 3

   Installation
   Backends
   compare-to-ipywidgets
   API
   Examples
   Contributing
   

.. image:: images/interactive-plot.gif
.. image:: images/heatmap_slicer.gif

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
