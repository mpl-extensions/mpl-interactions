========================
Comparison to ipywidgets
========================

**ipywidgets** already provides both an ``interact`` and an ``interactive_output`` function, so why use **mpl_interactions** instead?
There are three reasons: performance, portability, and convenience.

Performance
-----------
.. note::
    This explanation is built on the description here: `matplotlib/ipympl#36 (comment) <https://github.com/matplotlib/ipympl/issues/36#issuecomment-361234270>`_

The ipywidgets functions expect the entire output to be regenerated everytime the slider value changes. This means that
these functions will work best with the inline backend. In fact they even have some `special casing <https://github.com/jupyter-widgets/ipywidgets/blob/6be18d9b75353f7b4a1c328c6ea06d8959f978f6/ipywidgets/widgets/interaction.py#L230>`_
to better support the inline backend. Unfortunately this does not work well with the interacive ``ipympl`` backend which
expects to be shown only once and then updated with Matplotlib methods as controls change. The result of this is that you will often end up making
many new figures or recreating the the entire plot every time the sliders change values. 

You can get around these performance issues by using the ``interact`` function and having the called function use the Matplotlib updating methods 
such as `line.set_data`. Unfortunately you then end up needing to remember how to do this as well find that you are repeating yourself.
This was the initial motivation for this library and brings us to the reason of convenience.

Portability
-----------

mpl_interactions will make use of the widgets provided by ipywidgets if they are available, but unlike interactive output, it will
work if called from a script or an (i)python repl by falling back to the builtin Matplotlib
`widgets <https://matplotlib.org/api/widgets_api.html?highlight=widgets#module-matplotlib.widgets>`_

Convenience
-----------

With **ipywidgets.interact** you are responsible for generating the data to plot, and for handling the logic to update the plot.


1. ``f(x,...) => y``
2. Plotting logic (``plt.plot``, ``fig.cla``, ``ax.set_ylim``, etc)

In contrast **mpl_interactions** only requires you specify the data you want to plot and will handle the creation and updating of the plot for you. 

Additionally there are multiple valid strategies for choosing what selection widgets to create for a parameter. As a general
framework the choices made by ipywidgets are not always ideal for plotting scientific data. Unencumbered by generality mpl-interactions makes
several slightly different choices that are more plotting focused.


Differences in generated widgets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. contents:: :local:

**tuple of floats**
"""""""""""""""""""

Both mpl-interactions and ipywidgets will generate a slider. However, mpl-interactions will use ``np.linspace``
and ipywidgets will use ``np.arange``.


Comparison of the generated widget for ``two_tuple = (1., 5)`` and ``three_tuple = (0., 1250, 100)``


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

numpy array or list
"""""""""""""""""""
ipywidgets will assume these are categoricals. mpl-interactions will try to make a slider for the values.

For example here are what each will create for ``np.linspace(-5,5,100)``

**mpl-interactions**

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

for ``param = 10.``

**mpl_interactions**

Treats the parameter as fixed

**ipywidgets**
Creates a slider with a range of ``[-10,+3*10]``

.. jupyter-execute::
    :hide-code:

    def f(param):
        pass
    _ = interact(f, param = 10.)
