============
Installation
============

User install
------------
To install simply run:
``pip install mpl_interactions``

Jupyterlab setup
----------------

If you plan on using `mpl_interactions` in the notebook then you need to ensure you have a fully working
installation of `ipympl <https://github.com/matplotlib/ipympl>`_. The ``ipympl`` python package is installed as dependency, however you
may need to take a few extra steps to get it to work in jupyterlab. In particular you need to make sure ``nodejs > 10`` is availiable
and that you have installed ``jupyterlab-manager``


.. code-block:: bash

   conda install nodejs=12
   jupyter labextension install @jupyter-widgets/jupyterlab-manager


.. index::
   pair: Syntax; Code Example

Development Installation
------------------------

First create your own fork of https://github.com/ianhi/mpl-interactions.

.. code-block:: bash
   
   git clone <your fork>
   cd mpl-interactions
   pip install -e.[docs]
