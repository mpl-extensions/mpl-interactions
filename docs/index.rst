Welcome to mpl-interactions' documentation!
===========================================

mpl_interactions: Easy and interactive Matplotlib plots
--------------------------------------------------------

mpl_interactions' aims to make it as easy as possible for users to create  `Matplotlib <http://www.matplotlib.org>`_ plots. 
In particular, you can:

* Better understand a function's change with respect to a parameter.
* Visualize your data interactively.

To achieve this, mpl_interactions provides:

* A Matplotlib/ipympl-aware interact function for Jupyter notebooks.
* A function to compare horizontal and vertical slices of heatmaps.
* A function allowing the user to zoom using the scroll wheel.

Installation
^^^^^^^^^^^^^

To install, simply run: ``pip install mpl_interactions``

Further instructions for installation from JupyterLab can be found on the :ref:`Installation` page. 

Basic example
^^^^^^^^^^^^^^

To control a plot with a slider:

.. code-block:: python

   %matplotlib ipympl
   from mpl_interactions import interactive_plot
   x = np.linspace(0,np.pi,100)
   τ = np.linspace(.5, 10, 100)
   β = np.linspace(1, 10, 100)
   def f1(x, τ, β):
       return np.sin(x*τ)*x*β
   def f2(x, τ, β):
       return np.sin(x*β)*x*τ
   fig, ax, sliders = interactive_plot([f1, f2], x=x, τ = τ, β = β)
   _ = plt.legend()

.. image:: images/interactive-plot.gif
.. image:: images/heatmap_slicer.gif

For other functionality and more detailed examples, visit the :ref:`Examples` page. 

Matplotlib backends
^^^^^^^^^^^^^^^^^^^^

mpl_interactions' functions are written for primary use with `ipympl <https://github.com/matplotlib/ipympl>`_, the backend 
designed for Jupyter Notebooks. Further explaination of how to run mpl_interactions optimally can be found 
on the :ref:`Matplotlib Backends` page. 

*Follow the links below for further information on installation, functions, and plot examples.* 

.. toctree::
   :maxdepth: 3

   Installation
   Backends
   compare-to-ipywidgets
   API
   Examples
   Contributing

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
