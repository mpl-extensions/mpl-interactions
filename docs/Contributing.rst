============
Contributing
============

Thanks for thinking of a way to help improve this library! Remember that contributions come in all
shapes and sizes beyond writing bug fixes. Contributing documentation or opening new `issues <https://github.com/ianhi/mpl-interactions/issues>`_ for bugs, clarification on things you
found unclear, and requesting new features are all super valuable contributions. 

Code Improvements
-----------------

Seeing your changes
^^^^^^^^^^^^^^^^^^^

If you are working in a Jupyter notebook then in order to be able to see your code changes you will either need to restart
the Kernel every time you make a change to the code. Or you make the function be reloaded from the source file every time you run it
using `autoreload <https://ipython.readthedocs.io/en/stable/config/extensions/autoreload.html>`_.


.. code-block:: python

    %load_ext autoreload
    %autoreload 2

    from mpl_interactions import ....

Working with Git
^^^^^^^^^^^^^^^^

Using Git/Github can confusing (https://xkcd.com/1597/) so if you're new to Git you may find
it helpful to use a program like `Github Desktop <desktop.github.com>`_ as well as to follow
a `guide <https://github.com/firstcontributions/first-contributions#first-contributions>`_. 

Also feel free to ask for help/advice on the relevant Github `issue <https://github.com/ianhi/mpl-interactions/issues>`_.

Documentation
-------------

Building the documentation:

First make sure you have installed the requirements for building the documentation

.. code-block:: bash

    pip install -e.[docs]

Then run the following commands

.. code-block:: bash

    cd docs
    make html

If you open the ``index.html`` file in your browser then you should now be able to see the rendered documentation.

Autobuild the documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can also use `sphinx-autobuild <https://github.com/GaretJax/sphinx-autobuild>`_ to continuously watch the documentation for changes and rebuild it for you.
sphinx-autobuild will be installed automatically by the above ``pip`` command so all you need to do is:

.. code-block:: bash

    cd docs
    sphinx-autobuild . _build/html -B

and then in a few seconds your webbrowser should open up the documentation. Then whenever you save a file
the documentation will automatically regenerate and the webpage should even refresh for you!