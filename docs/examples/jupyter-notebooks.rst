====================
In Jupyter Notebooks
====================

Unfortunately the interactive plots won't work on a website as there is no Python kernel
running. So for all the interactive outputs have been replaced by gifs of what you should expect.

As discussed in the [Add a link to backend discussion] page you will have the best
performance with the ipympl backed, so make sure you set that using ``%matplotlib ipympl``.


.. jupyter-execute::

    %matplotlib ipympl
    import matplotlib.pyplot as plt
    import numpy as np
    import ipywidgets as widgets
    from mpl_interactions import interactive_plot, interactive_plot_factory


Simple Example
--------------

To use the interactive plot function all you need to do is write a function that will
return a numpy array or a list of numbers. You can provide the parameters that you want
to vary with sliders as keyword arguments to the `.interactive_plot` function. 

.. jupyter-execute::

    x = np.linspace(0,np.pi,100)
    tau = np.linspace(1,10, 100)
    beta = np.linspace(1,10)
    def f(x, tau, beta):
        return np.sin(x*tau)*x**beta

and then to display the plot:: python

    fig, ax, sliders = interactive_plot(f, x=x, τ = τ, β = β)


.. image:: interactive-plot-images/simple.gif

Other ways to set parameter values
----------------------------------

You can set parameters with any of the following:

- **numpy array/list** - Creates a slider with the values in the array
- **tuple** - Acts as an argument to linspace. Can have either 2 or 3 items
- **set** - Creates a categorical selector (order will not preserved)
- **set(tuple())** - Categorical selector with order maintained
- **scalar** - Fixed value
- **ipywidgets.Widget** any subclass of `ipywidgets.Widget` that has a ``value`` attribute can be used as is

Here is an example using all of the possibilities with a dummy function. The `display=False`
prevent the widgets from being automatically displayed which makes it easier to render them in this webpage,
but in general you should not need to use that.


One other caveat is that the slider's label will not update as that also requires a Python kernel.

.. jupyter-execute::

    def foo(x, **kwargs):
        return x
    
    a = np.linspace(0,10)
    b = (0, 10, 15)
    c = {'this', 'set will be', 'unordered'}
    d = {('this', 'set will be', 'ordered')}
    e = 0 # this will not get a slider
    f = widgets.Checkbox(value=True, description='A checkbox!!')
    display(interactive_plot(foo, x=x, a=a, b=b, c=c, d=d, e=e, f_=f, display=False)[-1])
