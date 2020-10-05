=================================
Attaching play buttons to sliders
=================================

.. note:: 
    The labels will not update as that requires a Python kernel.


If you are working in Jupyter then you can add
`ipywidgets.Play <https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20List.html#Play-(Animation)-widget>`_ widgets
to the sliders for any of the ``interactive_*`` functions.

In this tutorial all the functions are ``scatter`` but this will work for ``plot``, ``hist``, ``imshow``, etc...

Specifying Which Sliders Get Play buttons
-----------------------------------------


.. jupyter-execute::

    %matplotlib ipympl
    import matplotlib.pyplot as plt
    import numpy as np
    from mpl_interactions import *

    # turn off interactive mode so that broken
    # plots don't render in the docs
    plt.ioff()

Boolean: All get a button
^^^^^^^^^^^^^^^^^^^^^^^^^

.. jupyter-execute::

    N = 50
    x = np.random.rand(N)


    def f_y(x, tau, beta):
        return np.sin(x * tau) ** 2 + np.random.randn(N) * 0.01 * beta


    fig, ax = plt.subplots()
    controls = interactive_scatter(
        x, f_y, tau=(1, 2 * np.pi, 100), beta=(0, 2), play_buttons=True)

List: Choose by name
^^^^^^^^^^^^^^^^^^^^

.. jupyter-execute::

    fig, ax = plt.subplots()
    controls = interactive_scatter(
        x, f_y, tau=(1, 2 * np.pi, 100), beta=(0, 2), play_buttons=["tau"])

defaultdict: Specify by name and choose default
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have many parameters and you want the most, but not all, of them to have a Play button then
you should use a `defaultdict``

.. jupyter-execute::

    from collections import defaultdict

    def f(x, **kwargs):
        return x
    play_buttons = defaultdict(lambda: True)
    play_buttons["tau"] = False
    fig, ax = plt.subplots()
    controls = interactive_scatter(
        x,
        f,
        tau=(1, 2 * np.pi, 100),
        beta=(0, 2),
        zeta=(0, 1),
        psi=(0, 1),
        play_buttons=play_buttons,
    )

Choosing Play Button Position
-----------------------------

The ``play_button_pos`` argument controls where the Play button will be displayed relative to the slider. Valid options are
``'left'`` and ``'right'``. Play buttons on the right was chosen as default because of the potential for slider misalignment
if not all sliders have a Play button. (If you have a better idea for how to do
this please open an `issue <https://github.com/ianhi/mpl-interactions/issues/new?labels=enhancement&template=enhancement.md>`_
and suggest how to improve this)


.. jupyter-execute::

    from collections import defaultdict

    def f(x, **kwargs):
        return x

    play_buttons = defaultdict(lambda: True)
    play_buttons["tau"] = False
    fig, ax = plt.subplots()
    controls = interactive_scatter(
        x,
        f,
        tau=(1, 2 * np.pi, 100),
        beta=(0, 2),
        zeta=(0, 1),
        psi=(0, 1),
        play_buttons=play_buttons,
        play_button_pos="left",
    )