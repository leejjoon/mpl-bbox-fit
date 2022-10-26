#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Jae-Joon Lee.
# Distributed under the terms of the Modified BSD License.

from ..bbox_image import BboxImage


import pytest
import matplotlib.pyplot as plt
import matplotlib.transforms as mtrans
import numpy as np


@pytest.mark.mpl_image_compare(filename="test_example.png")
def test_example():
    fig, ax = plt.subplots()
    data = np.arange(100).reshape((10, 10))

    bbox1 = mtrans.TransformedBbox(mtrans.Bbox.from_extents(0.1, 0.1, 0.4, 0.9),
                                   ax.transData)
    bbox_image1 = BboxImage(bbox1,
                            origin="lower",
                            data=data,
                            cmap="viridis",
                            aspect="auto",
                            )

    ax.add_artist(bbox_image1)

    bbox2 = mtrans.TransformedBbox(mtrans.Bbox.from_extents(0.6, 0.1, 0.9, 0.9),
                                   ax.transData)
    bbox_image2 = BboxImage(bbox2,
                            origin="lower",
                            data=data,
                            cmap="viridis",
                            aspect=1
                            )

    ax.add_artist(bbox_image2)

    return fig
