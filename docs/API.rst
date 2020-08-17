===
API
===


Jupyter
-------

These functions will only work in the context of a jupyter notebook as they leverage ipywidgets sliders. Consequently
you will have the best perfomance when using the ipympl backend ``%matplotlib ipympl``

.. currentmodule:: mpl_interactions
.. autosummary::
   :toctree: autoapi
   :nosignatures:

   ~mpl_interactions.interactive_plot
   ~mpl_interactions.interactive_plot_factory


Generic
-------

Functions that will be useful irrespective of backend.

.. currentmodule:: mpl_interactions
.. autosummary::
   :toctree: autoapi
   :nosignatures:

   ~mpl_interactions.heatmap_slicer
   ~mpl_interactions.zoom_factory
   ~mpl_interactions.panhandler


Utilities
---------

Functions that make it a bit more convenient to do some things in matplotlib.

.. currentmodule:: mpl_interactions
.. autosummary::
   :toctree: autoapi
   :nosignatures:

   ~mpl_interactions.ioff
   ~mpl_interactions.figure
   ~mpl_interactions.nearest_idx
