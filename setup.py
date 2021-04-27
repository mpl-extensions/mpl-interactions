from os import path

from setuptools import setup

# extract version
VERSION_PATH = path.realpath("mpl_interactions/_version.py")
version_ns = {}
with open(VERSION_PATH, encoding="utf8") as STREAM:
    exec(STREAM.read(), {}, version_ns)
version = version_ns["__version__"]

if __name__ == "__main__":
    setup(
        version=version_ns["__version__"],
    )
