# mpl_interactions
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-7-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->
[![Documentation Status](https://readthedocs.org/projects/mpl-interactions/badge/?version=stable)](https://mpl-interactions.readthedocs.io/en/stable/?badge=stable)[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ianhi/mpl-interactions/master?urlpath=lab) (Warning: The interactions will be laggy when on binder)

## Welcome!

mpl_interactions' library provides helpful ways to interact with [Matplotlib](https://matplotlib.org/) plots. Full narrative documentation and example can be found on [ReadtheDocs](https://mpl-interactions.readthedocs.io/en/stable/#).

<img src=https://raw.githubusercontent.com/ianhi/mpl-interactions/master/docs/_static/images/short-interactive.gif width=45%>  <img src=https://raw.githubusercontent.com/ianhi/mpl-interactions/master/docs/_static/images/heatmap_slicer.gif width=45%>


## Installation
```bash
pip install mpl_interactions["jupyter"] # will install necessary deps for using in jupyter

# for use only outside of jupyter:
pip install mpl_interactions

# if using jupyterlab
conda install -c conda-forge nodejs=13
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

If you use JupyterLab, make sure you follow the full instructions in the ipympl [readme](https://github.com/matplotlib/ipympl#install-the-jupyterlab-extension) in particular installing jupyterlab-manager.
## Contributing / feature requests / roadmap

I use the GitHub [issues](https://github.com/ianhi/mpl-interactions/issues) to keep track of ideas I have, so looking through those should serve as a roadmap of sorts. For the most part I add to the library when I create a function that is useful for the science I am doing. If you create something that seems useful a PR would be most welcome so we can share it easily with more people. I'm also open to feature requests if you have an idea.

## Documentation

The fuller narrative documentation can be found on [ReadTheDocs](https://mpl-interactions.readthedocs.io/en/latest/). You may also find it helpful to check out the [examples directory](https://github.com/ianhi/mpl-interactions/tree/master/examples).

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="http://ianhi.github.io"><img src="https://avatars0.githubusercontent.com/u/10111092?v=4" width="100px;" alt=""/><br /><sub><b>Ian Hunt-Isaak</b></sub></a><br /><a href="https://github.com/ianhi/mpl-interactions/commits?author=ianhi" title="Code">💻</a></td>
    <td align="center"><a href="https://darlingdocs.wordpress.com/"><img src="https://avatars1.githubusercontent.com/u/67113216?v=4" width="100px;" alt=""/><br /><sub><b>Sam</b></sub></a><br /><a href="https://github.com/ianhi/mpl-interactions/commits?author=samanthahamilton" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/jcoulter12"><img src="https://avatars1.githubusercontent.com/u/14036348?v=4" width="100px;" alt=""/><br /><sub><b>Jenny Coulter</b></sub></a><br /><a href="#userTesting-jcoulter12" title="User Testing">📓</a></td>
    <td align="center"><a href="https://sjhaque14.wixsite.com/sjhaque"><img src="https://avatars3.githubusercontent.com/u/61242473?v=4" width="100px;" alt=""/><br /><sub><b>Sabina Haque</b></sub></a><br /><a href="https://github.com/ianhi/mpl-interactions/commits?author=sjhaque14" title="Documentation">📖</a> <a href="#userTesting-sjhaque14" title="User Testing">📓</a> <a href="https://github.com/ianhi/mpl-interactions/commits?author=sjhaque14" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/jrussell25"><img src="https://avatars2.githubusercontent.com/u/35578729?v=4" width="100px;" alt=""/><br /><sub><b>John Russell</b></sub></a><br /><a href="https://github.com/ianhi/mpl-interactions/commits?author=jrussell25" title="Code">💻</a> <a href="#userTesting-jrussell25" title="User Testing">📓</a> <a href="https://github.com/ianhi/mpl-interactions/commits?author=jrussell25" title="Documentation">📖</a></td>
    <td align="center"><a href="http://maxshinnpotential.com"><img src="https://avatars2.githubusercontent.com/u/951986?v=4" width="100px;" alt=""/><br /><sub><b>Max Shinn</b></sub></a><br /><a href="https://github.com/ianhi/mpl-interactions/commits?author=mwshinn" title="Code">💻</a> <a href="#userTesting-mwshinn" title="User Testing">📓</a></td>
    <td align="center"><a href="https://github.com/kmdalton"><img src="https://avatars2.githubusercontent.com/u/2790777?v=4" width="100px;" alt=""/><br /><sub><b>Kevin Dalton</b></sub></a><br /><a href="#userTesting-kmdalton" title="User Testing">📓</a></td>
  </tr>
</table>

<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
