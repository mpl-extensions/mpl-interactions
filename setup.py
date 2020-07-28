from setuptools import setup
setup(
    name="ipympl_interactions",
    version="0.1",
    py_modules=['ipympl_interactions']
    install_requires = [
        'ipympl>=0.5.6',
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
    ],
    url = 'https://github.com/ianhi/ipympl-interactions',
)
