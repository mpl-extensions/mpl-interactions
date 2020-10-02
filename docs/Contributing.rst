============
Contributing
============

Thanks for thinking of a way to help improve this library! Remember that contributions come in all
shapes and sizes beyond writing bug fixes. Contributing to documentation, opening new `issues <https://github.com/ianhi/mpl-interactions/issues>`_ for bugs, asking for clarification 
on things you find unclear, and requesting new features, are all super valuable contributions. 

Code Improvements
-----------------

All development for this library happens on Github at `mpl_interactions <https://github.com/ianhi/mpl-interactions>`_.

.. code-block:: bash
   
   git clone <your fork>
   cd mpl-interactions
   pip install -e ".[dev, doc, test, jupyter]"
   pre-commit install

.. code-block:: bash

   conda install nodejs=12
   jupyter labextension install @jupyter-widgets/jupyterlab-manager


Seeing your changes
^^^^^^^^^^^^^^^^^^^

If you are working in a Jupyter Notebook, then in order to see your code changes you will need to either:

* Restart the Kernel every time you make a change to the code.
* **Or:** Make the function reload from the source file every time you run it by using `autoreload <https://ipython.readthedocs.io/en/stable/config/extensions/autoreload.html>`_.

.. code-block:: python

    %load_ext autoreload
    %autoreload 2

    from mpl_interactions import ....

Working with Git
^^^^^^^^^^^^^^^^

Using Git/Github can confusing (https://xkcd.com/1597/) so if you're new to Git, you may find
it helpful to use a program like `Github Desktop <desktop.github.com>`_ and to follow
a `guide <https://github.com/firstcontributions/first-contributions#first-contributions>`_. 

Also feel free to ask for help/advice on the relevant Github `issue <https://github.com/ianhi/mpl-interactions/issues>`_.

Documentation
-------------

Following changes to the source files, you can view recent adjustments by building the documentation.

1. Make sure you have installed the requirements for building the documentation:

.. code-block:: bash

    cd mpl-interactions
    pip install -e ".[doc, jupyter]"

2. Run the following commands:

.. code-block:: bash

    cd docs
    make html

If you open the ``index.html`` file in your browser you should now be able to see the rendered documentation.

Autobuild the documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Alternatively, you can use `sphinx-autobuild <https://github.com/GaretJax/sphinx-autobuild>`_ to continuously watch the documentation for changes and rebuild it for you.
Sphinx-autobuild will be installed automatically by the above ``pip`` command, and we've added it to the ``Makefile``. All you need to do is:

.. code-block:: bash

    cd docs
    make watch

In a few seconds your web browser should open up the documentation. Now whenever you save a file
the documentation will automatically regenerate and the webpage will refresh for you!

Thank you to our current team!
------------------------------

This project follows the `all-contributors <https://github.com/all-contributors/all-contributors>`_ specification. 
Contributors members can be found on mpl_interactions' `README <https://github.com/ianhi/mpl-interactions#contributors->`_ page.
