#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Jae-Joon Lee.
# Distributed under the terms of the Modified BSD License.

from ..patch_hltext import monkey_patch
monkey_patch()

from ..bbox_hltext import BboxHighlightText
from highlight_text import HighlightText

import pytest
import matplotlib.pyplot as plt
import matplotlib.transforms as mtrans
import matplotlib.patheffects as path_effects

def path_effect_stroke(**kwargs):
    return [path_effects.Stroke(**kwargs), path_effects.Normal()]


@pytest.mark.mpl_image_compare(filename="test_hltext.png")
def test_example():
    fig, ax = plt.subplots()
    pe = path_effect_stroke(linewidth=3, foreground="orange")

    highlight_textprops =\
    [{"color": "yellow", "path_effects": pe},
     {"color": "#969696", "fontstyle": "italic", "fontweight": "bold"}]

    bbox2 = mtrans.Bbox.from_extents(0, 0, 1, 1.)
    # ax.add_artist(hlt.annotation_bbox)

    # hlt.annotation_bbox.set_transform(da2.get_bbox_transform())
    hlt = HighlightText(x=.5, y=.5,
                        fontsize=16,
                        ha='center', va='center',
                        s='The weather is <sunny>\nYesterday it was <cloudy>',
                        highlight_textprops=highlight_textprops,
                        fig=fig, ax=ax, zorder=99)

    da2 = BboxHighlightText(bbox2, hlt, transform=ax.transAxes)
    ax.add_artist(da2)

    return fig

def main():
    fig = test_example()
    plt.show()

if __name__ == '__main__':
    main()
