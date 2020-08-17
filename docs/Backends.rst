===================
Matplotlib Backends
===================

.. note::
        For discussion of what a Matplotlib backend is see: https://matplotlib.org/faq/usage_faq.html#what-is-a-backend

All the functions in the library will work with any interactive backend to Matplotlib. However, if you are working in a Jupyter
Notebook then you should make sure to use the `ipympl <https://github.com/matplotlib/ipympl>`_ backend. If you use a different backend
such as ``qt5agg`` the interactions will still work, but the interactions will be significantly laggier than with the ipympl backend.
You can make sure that you use the ipympl backend by including the `Jupyter Magic <https://ipython.readthedocs.io/en/stable/interactive/magics.html>`_:

.. code-block:: python

        %matplotlib ipympl
