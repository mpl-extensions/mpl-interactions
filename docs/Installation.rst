============
Installation
============

User install
------------
To install simply run:
``pip install mpl_interactions``

The above only has Matplotlib as a dependency. If you plan on using ``mpl_interactions`` in a Jupyter Notebook or JupyterLab then you should
install with ``pip install mpl_interactions[jupyter]`` this will install `ipympl <https://github.com/matplotlib/ipympl>`_ and ipywidgets for you.
If you use JupyterLab it is significantly easier get working for JupyterLab 3+

Setup for Jupyterlab 3+
----------------------------------
Installation of widgets was made significantly easier for JupyterLab 3+. Simply make sure you have a new version of JupyterLab:

.. code-block:: bash

   pip install --upgrade jupyterlab mpl-interactions[jupyter]

Setup for JupyterLab <= 2
-------------------------

If you plan on using mpl_interactions in notebooks with `JupyterLab <https://jupyterlab.readthedocs.io/en/stable/#>`_ version 2.x or lower
then you need to follow the below steps to ensure you have a fully working installation of `ipympl <https://github.com/matplotlib/ipympl>`_.
In particular you need to make sure ``nodejs > 10`` is availiable and that you have installed ``jupyterlab-manager``.


.. code-block:: bash

   pip install --upgrade ipympl
   conda install -c conda-forge nodejs=13
   jupyter labextension install @jupyter-widgets/jupyterlab-manager jupyter-matplotlib


.. index::
   pair: Syntax; Code Example

Development installation
------------------------

First create your own fork of https://github.com/ianhi/mpl-interactions.

.. code-block:: bash
   
   git clone <your fork>
   cd mpl-interactions
   pip install -e ".[dev, doc, test]"
