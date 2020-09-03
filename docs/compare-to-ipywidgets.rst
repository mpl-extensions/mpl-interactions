========================
Comparison to ipywidgets
========================

**ipywidgets** already provides both an ``interact`` and an ``interactive_output`` function, so why use **mpl_interactions** instead?
There are three reasons: performance, portability, and convenience.

Performance
-----------
.. note::
    This explanation is built on the description here: `matplotlib/ipympl#36 (comment) <https://github.com/matplotlib/ipympl/issues/36#issuecomment-361234270>`_

The ipywidgets functions expect the entire output to be regenerated every time a slider value changes. This means ipywidgets functions will work best with 
the ``inline`` backend. In fact, some `special casing <https://github.com/jupyter-widgets/ipywidgets/blob/6be18d9b75353f7b4a1c328c6ea06d8959f978f6/ipywidgets/widgets/interaction.py#L230>`_
is even available to better support the inline backend. Unfortunately this process does not work well with the interacive ``ipympl`` backend. The ``ipympl`` backend 
expects to be shown only once, then updated with Matplotlib methods as controls change. What results is you needing to make
multiple new figures---or recreate the entire plot---every time a slider value changes. 

It is possible to get around these performance issues by using the ``interact`` function and setting the called function to use Matplotlib updating methods 
(such as ``line.set_data``). However in this case, not only do you need to remember how to do this, but over time you will find you are repeating yourself.
Reducing these performance barriers was the initial motivation for the mpl_interactions library, and also brings us to the reason of convenience.

Portability
-----------

mpl_interactions will make use of the widgets provided by ipywidgets if they are available. Unlike interactive output, it will still 
work if called from a script or an (i)python REPL by falling back to the built in Matplotlib
`widgets <https://matplotlib.org/api/widgets_api.html?highlight=widgets#module-matplotlib.widgets>`_.

Convenience
-----------

With the interact function (**ipywidgets.interact**) you are responsible for generating the data to plot, and for handling the logic to update the plot.


1. ``f(x,...) => y``
2. Plotting logic (``plt.plot``, ``fig.cla``, ``ax.set_ylim``, etc)

In contrast, mpl_interactions only requires you specify the data you want to plot and will handle the plot creation and updating for you. 

Additionally, there are multiple valid strategies for choosing what selection widgets to create for a parameter. As a general
framework the choices made by ipywidgets are not always ideal for plotting scientific data. Unencumbered by generality, mpl_interactions makes
several slightly different choices that are more plotting focused.


Differences in generated widgets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. contents:: :local:

Tuple of floats
"""""""""""""""""""

Both mpl_interactions and ipywidgets will generate a slider. However, mpl_interactions will use ``np.linspace``
and ipywidgets will use ``np.arange``.


Here is a comparison of the generated widget for ``two_tuple = (1., 5)`` and ``three_tuple = (0., 1250, 100)``:


**mpl-interactions**

.. jupyter-execute::
    :hide-code:

    import numpy as np
    from ipywidgets import widgets
    from ipywidgets import interact

    # this isn't quite what is actually done
    # but mpl-interactions requries a kernel to update the label
    # so faking this here
    param1 = np.linspace(1, 5)
    slider1 = widgets.SelectionSlider(options = [("{:.2f}".format(i), i) for i in param1], description = 'two_tuple')
    param2 = np.linspace(0, 1250, 100)
    slider2 = widgets.SelectionSlider(options = [("{:.2f}".format(i), i) for i in param2], description = 'three_tuple')
    display(slider1)
    display(slider2)


**ipywidgets**

.. jupyter-execute::
    :hide-code:

    def f(two_tuple, three_tuple):
        pass
    _ = interact(f, two_tuple=(1., 5), three_tuple=(0., 1250, 100))

NumPy array or list
"""""""""""""""""""
ipywidgets will assume a NumPy array or list are categoricals. mpl_interactions will attempt to make a slider for the values.

For example, here is what ipywidgets and mpl_interactions will create for ``np.linspace(-5,5,100)``:

**mpl_interactions**

.. jupyter-execute::
    :hide-code:

    param = np.linspace(-5,5,100)
    slider = widgets.SelectionSlider(options = [("{:.2f}".format(i), i) for i in param])
    display(slider)


**ipywidgets**

.. jupyter-execute::
    :hide-code:

    def f(param):
        pass
    _ = interact(f, param = param)


Single number
"""""""""""""

In the context of a single number, for example, ``param = 10.``:

**mpl_interactions**

Treats the parameter as fixed.

**ipywidgets**

Creates a slider with a range of ``[-10,+3*10]``.

.. jupyter-execute::
    :hide-code:

    def f(param):
        pass
    _ = interact(f, param = 10.)
