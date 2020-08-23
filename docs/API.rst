===
API
===


pyplot
------

Connect control the output of standard plotting functions such as ``plot`` and ``hist`` using sliders and other
control widgets. When using the ``ipympl`` backend these functions will leverage ipywidgets for the controls, otherwise they
will use the builtin Matplotlib widgets.

.. currentmodule:: mpl_interactions
.. autosummary::
   :toctree: autoapi
   :nosignatures:

   ~mpl_interactions.interactive_plot
   ~mpl_interactions.interactive_plot_factory
   ~mpl_interactions.interactive_hist


generic
-------

Functions that will be useful irrespective of backend.

.. currentmodule:: mpl_interactions
.. autosummary::
   :toctree: autoapi
   :nosignatures:

   ~mpl_interactions.heatmap_slicer
   ~mpl_interactions.zoom_factory
   ~mpl_interactions.panhandler


utilities
---------

Functions that make it a bit more convenient to do some things in matplotlib.

.. currentmodule:: mpl_interactions
.. autosummary::
   :toctree: autoapi
   :nosignatures:

   ~mpl_interactions.ioff
   ~mpl_interactions.figure
   ~mpl_interactions.nearest_idx
