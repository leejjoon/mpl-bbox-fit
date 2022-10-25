import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import matplotlib.transforms as mtrans
# or

from mpl_bbox_image.bbox_image import BboxDrawingArea
from mpl_bbox_image.patch_hltext import monkey_patch
monkey_patch()

from mpl_bbox_image.bbox_hltext import BboxHighlightText
from highlight_text import HighlightText

def path_effect_stroke(**kwargs):
    return [path_effects.Stroke(**kwargs), path_effects.Normal()]
pe = path_effect_stroke(linewidth=3, foreground="orange")

highlight_textprops =\
[{"color": "yellow", "path_effects": pe},
 {"color": "#969696", "fontstyle": "italic", "fontweight": "bold"}]

fig, ax = plt.subplots(figsize=(4, 4))

bbox2 = mtrans.Bbox.from_extents(0, 0.9, 1, 1.)
# ax.add_artist(hlt.annotation_bbox)

# hlt.annotation_bbox.set_transform(da2.get_bbox_transform())
hlt = HighlightText(x=0, y=1.,
                    fontsize=16,
                    ha='left', va='bottom',
                    s='The weather is <sunny>\nYesterday it was <cloudy>',
                    highlight_textprops=highlight_textprops,
                    annotationbbox_kw={"xycoords": "axes fraction",
                                       "boxcoords": "offset points",
                                       "xybox": (3, 3)
                                       },
                    fig=fig, ax=ax)

da2 = BboxHighlightText(bbox2, hlt, transform=ax.transAxes)
ax.add_artist(da2)

from mpl_bbox_image.bbox_image import BboxPatch
bp = BboxPatch(bbox2, trans=ax.transAxes)
ax.add_artist(bp)

plt.show()
