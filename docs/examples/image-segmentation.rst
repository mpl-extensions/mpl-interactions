==================
Image Segmentation
==================

Hopefully you won't often be faced with the task of manually segmenting images. However, for the times when you must
it's nice to not need to leave the comfort of python for some other program. Thus we arrive at the :class:`~mpl_interactions.image_segmenter` class.

(Credit where it's due: This tool was developed as part of a final project in Pavlos Protopapas' class `AC295 <https://harvard-iacs.github.io/2020-AC295/>`_, you can read more about it
in the project's final write up on `towards data science <https://towardsdatascience.com/how-we-built-an-easy-to-use-image-segmentation-tool-with-transfer-learning-546efb6ae98>`_)


.. code-block:: python

    import matplotlib.pyplot as plt
    import matplotlib.cbook as cbook
    import numpy as np
    from mpl_interactions import image_segmenter

    # load a sample image
    with cbook.get_sample_data('ada.png') as image_file:
        image = plt.imread(image_file)
    
    # If you don't keep a reference to the object the call backs will fail
    segmenter = image_segmenter(image, nclasses = 3, mask_colors='red', mask_alpha=.76, figsize=(7,7))
    
    # if working in a jupyter notebook
    display(segmenter)

This will create a matplotlib figure with the image in it. It will automatically apply 
:meth:`~mpl_interactions.zoom_factory` and :meth:`~mpl_interactions.panhandler` so you can scroll to
zoom and use middle click to pan. If you left click and drag you can start creating the mask over the image.

.. image:: ../_static/segment.gif

You can switch which class you are marking by directly modifying the `segmenter`'s `current_class` variable.

.. code-block:: python

    segmenter.current_class = 2

and you can always directly the 2D mask with:

.. code-block:: python

    plt.figure()
    plt.imshow(segmenter.mask)


Loading existing masks
----------------------

You can also load an existing mask. You will need to ensure that it does not contain values greater
than nclasses and that it has the same shape as the image. There are currently no safegaurds for
this and when there are exceptions in a matplotlib callback they can be hard to see in the notebook - so be careful!

.. code-block:: python

    # load the mask
    import requests
    import io

    response = requests.get('https://github.com/ianhi/mpl-interactions/raw/41ebd90674e2136e87240ba81ae509dee15a63a7/examples/ada-mask.npy')
    response.raise_for_status()
    mask = np.load(io.BytesIO(response.content))  # Works!

    preloaded = image_segmenter(image, nclasses=3, mask=mask)
    display(preloaded)

.. image:: ../_static/segment-preload-mask.png
