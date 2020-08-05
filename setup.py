from setuptools import setup, find_packages
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="mpl_interactions",
    version="0.2.0-dev",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires = [
        'ipywidgets',
        'matplotlib',
        'ipympl>=0.5.7'
    ],
    author          = 'Ian Hunt-Isaak',
    author_email    = 'ianhuntisaak@gmail.com',
    license         = 'BSD',
    platforms       = "Linux, Mac OS X, Windows",
    description     = 'Matplotlib aware interact functions',
    keywords        = ['Jupyter', 'Widgets', 'IPython', 'Matplotlib'],
    classifiers     = [
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework :: Jupyter',
        'Framework :: Matplotlib'
    ],
    url = 'https://github.com/ianhi/mpl-interactions',
    extras_require = {
        'docs': [
            'sphinx>=1.5',
            'mock',
            'numpydoc',
            'recommonmark',
            'sphinx_rtd_theme',
            'nbsphinx>=0.2.13,<0.4.0',
            'jupyter_sphinx',
            'nbsphinx-link',
            'pytest_check_links',
            'pypandoc',
        ],
    }
)
