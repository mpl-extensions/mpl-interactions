===
API
===


pyplot
------

Control the output of standard plotting functions such as ``plot`` and ``hist`` using sliders and other
widgets. When using the ``ipympl`` backend these functions will leverage ipywidgets for the controls, otherwise they
will use the built-in Matplotlib widgets.

.. currentmodule:: mpl_interactions
.. autosummary::
   :toctree: autoapi
   :nosignatures:

   ~mpl_interactions.interactive_plot
   ~mpl_interactions.interactive_hist
   ~mpl_interactions.interactive_scatter
   ~mpl_interactions.interactive_imshow
   ~mpl_interactions.interactive_axhline
   ~mpl_interactions.interactive_axvline


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
   ~mpl_interactions.image_segmenter
   ~mpl_interactions.hyperslicer

utilities
---------

Functions that make some features in Matplotlib a bit more convenient.

.. currentmodule:: mpl_interactions
.. autosummary::
   :toctree: autoapi
   :nosignatures:

   ~mpl_interactions.ioff
   ~mpl_interactions.figure
   ~mpl_interactions.nearest_idx
