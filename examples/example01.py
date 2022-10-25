import numpy as np
from mpl_bbox_image import BboxImage
import matplotlib.pyplot as plt
import matplotlib.transforms as mtrans

from matplotlib.patches import Patch, draw_bbox
from matplotlib.artist import Artist

class BboxPatch(Artist):
    def __init__(self, bbox, trans=None):
        super().__init__()
        self.bbox = bbox
        self.trans = trans

    def draw(self, renderer):
        if self.trans is None:
            trans = getattr(self.bbox, "_transfrom", None)
        else:
            trans = self.trans

        draw_bbox(self.bbox, renderer, trans=trans, color="0.8")


def simple_bbox_image(ax):
    data = np.arange(100).reshape((10, 10))

    bbox2 = mtrans.TransformedBbox(mtrans.Bbox.from_extents(0.6, 0.2, 0.9, 0.8),
                                   ax.transData)
    bbox_image2 = BboxImage(bbox2,
                            origin="lower",
                            data=data,
                            cmap="viridis",
                            mode="contain"
                            )

    ax.add_artist(bbox_image2)
    bp = BboxPatch(bbox2)
    ax.add_artist(bp)

def main():
    fig, ax = plt.subplots()
    ax.set_aspect(1)
    data = np.arange(100).reshape((10, 10))

    simple_bbox_image(ax)

    plt.show()


if __name__ == '__main__':
    main()
