import json
import base64
import os
import glob
import shutil
import nbformat


def gogogo_all(source_dir, dest_dir):
    """
    copy and render all the notebooks from one dir to another
    """
    notebooks = glob.glob(os.path.join(source_dir, "*.ipynb"))
    gifs = glob.glob(os.path.join(source_dir, "*.gif"))
    for nb in notebooks:
        to = os.path.join(dest_dir, os.path.basename(nb))
        gogogo_gif(nb, to)
    for gif in gifs:
        to = os.path.join(dest_dir, os.path.basename(gif))
        shutil.copyfile(gif, to)


def gogogo_gif(notebook_from, notebook_to):
    """
    convert the output of cells with `gif` in their metadata tag to be those
    gifs

    parameters
    ----------
    notebook_from : string
        path of source notebook
    notebook_to : string
        where to put the rendered notebook
    """
    with open(notebook_from) as f:
        nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)
    for i, cell in enumerate(nb["cells"]):
        if "gif" in cell["metadata"]:
            gif = cell["metadata"]["gif"]
            gif = os.path.join("../_static/images/", gif)
            cell["outputs"] = [
                {
                    "data": {"text/html": f'<img src="{gif}">'},
                    "execution_count": 1,
                    "metadata": {},
                    "output_type": "execute_result",
                }
            ]
    with open(notebook_to, "w") as f:
        nbformat.write(nb, f)
