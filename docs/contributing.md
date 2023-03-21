# Contributing

Thanks for thinking of a way to help improve this library! Remember that contributions come in all shapes and sizes beyond writing bug fixes. Contributing to [documentation](#documentation), opening new [issues](https://github.com/mpl-extensions/mpl-interactions/issues) for bugs, asking for clarification on things you find unclear, and requesting new features, are all super valuable contributions.

## Code Improvements

All development for this library happens on GitHub at [mpl_interactions](https://github.com/mpl-extensions/mpl-interactions). We recommend you work with a [Conda](https://www.anaconda.com/products/individual) environment (or an alternative virtual environment like [`venv`](https://docs.python.org/3/library/venv.html)).

```bash
git clone <your fork>
cd mpl-interactions
conda env create
conda activate mpl-interactions
pre-commit install
```

The `conda env create` command installs all Python packages that are useful when working on the source code of `mpl_interactions` and its documentation. You can also install these packages separately:

```bash
pip install -e ".[dev]"
```

The {command}`-e .` flag installs the `mpl_interactions` folder in ["editable" mode](https://pip.pypa.io/en/stable/cli/pip_install/#editable-installs) and {command}`[dev]` installs the [optional dependencies](https://setuptools.readthedocs.io/en/latest/userguide/dependency_management.html#optional-dependencies) you need for developing `mpl_interacions`.

### Seeing your changes

If you are working in a Jupyter Notebook, then in order to see your code changes you will need to either:

- Restart the Kernel every time you make a change to the code.
- Make the function reload from the source file every time you run it by using [autoreload](https://ipython.readthedocs.io/en/stable/config/extensions/autoreload.html), e.g.:

  ```python
  %load_ext autoreload
  %autoreload 2

  from mpl_interactions import ....
  ```

### Working with Git

Using Git/GitHub can confusing (<https://xkcd.com/1597>), so if you're new to Git, you may find it helpful to use a program like [GitHub Desktop](https://desktop.github.com) and to follow a [guide](https://github.com/firstcontributions/first-contributions#first-contributions).

Also feel free to ask for help/advice on the relevant GitHub [issue](https://github.com/extensions/mpl-interactions/issues).

## Documentation

Our documentation on Read the Docs ([mpl-interactions.rtfd.io](https://mpl-interactions.readthedocs.io)) is built with [Sphinx](https://www.sphinx-doc.org) from the notebooks in the `docs` folder. It contains both Markdown files and Jupyter notebooks.

Examples are best written as Jupyter notebooks. To write a new example, create in a notebook in the `docs/examples` directory and list its path under one of the [`toctree`s](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-toctree) in the `index.md` file. When the docs are generated, they will be rendered as static html pages by [myst-nb](https://myst-nb.readthedocs.io).

If you have installed all developer dependencies (see [above](#contributing)), you can view recent modifications to the source files the following simple tox command:

```bash
tox -e doc
```

If you open the `index.html` file in your browser you should now be able to see the rendered documentation.

Alternatively, you can use [sphinx-autobuild](https://github.com/executablebooks/sphinx-autobuild) to continuously watch source files for changes and rebuild the documentation for you. Sphinx-autobuild will be installed automatically by the above `pip` command, so all you need to do is run:

```bash
tox -e doclive
```

In a few seconds your web browser should open up the documentation. Now whenever you save a file the documentation will automatically regenerate and the webpage will refresh for you!

### Embedding GIFs

Unfortunately, interactive plots are not interactive on [Read the Docs](https://readthedocs.org/projects/mpl-interactions), because widgets require an active Python kernel to work. Instead, we therefore shoot [gif](https://docs.fileformat.com/image/gif) or [apng](https://docs.fileformat.com/image/apng) screencasts of interacting with the plots and embed them in the Jupyter notebooks.

To accomplish, these GIFs are best stored in `docs/_static/images`. Then, below the input cell of which you want to render cell output, you create a Markdown cell below that code cell and insert the GIF there [as an image](https://www.markdownguide.org/basic-syntax/#images).

## Thank you to our current team!

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributors members can be found on `mpl_interactions`' [README](https://github.com/extensions/mpl-interactions#contributors-) page.
