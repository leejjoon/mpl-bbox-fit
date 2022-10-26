from matplotlib.artist import Artist
import matplotlib.transforms as mtrans
from matplotlib.image import BboxImage as _BboxImage

from matplotlib.patches import Patch, draw_bbox

from .bbox_util import expand_to_aspect
from .bbox_fit_mode import BboxFitMode

# for debugging
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


class BboxImage(_BboxImage):
    """The Image class whose size is determined by the given bbox."""

    def __init__(self, bbox,
                 mode=BboxFitMode.FILL,
                 aspect=1,
                 anchor="C",
                 **kwargs
                 ):
        """
        Parameters
        ----------
        mode : 'fill', 'contain' or 'cover'

        aspect : float

        anchor : (float, float) or str
            May be either:

            * A sequence (*cx*, *cy*) where *cx* and *cy* range from 0
              to 1, where 0 is left or bottom and 1 is right or top

            * a string:
              - 'C' for centered
              - 'S' for bottom-center
              - 'SE' for bottom-left
              - 'E' for left
              - etc.

        kwargs are an optional list of Artist keyword args
        """
        super().__init__(
            bbox,
            **kwargs
        )
        self._aspect = aspect
        self._anchor = anchor
        self._mode = BboxFitMode(mode)

    def get_window_extent(self, renderer=None):
        """get the window extent from the given bbox, then apply aspec and anchor."""
        bbox = super().get_window_extent(renderer)

        if self._mode == BboxFitMode.FILL:
            return bbox

        ny, nx = self._A.shape[:2]

        box_aspect = self._aspect * ny / nx
        if self._mode == BboxFitMode.CONTAIN:
            r = bbox.shrunk_to_aspect(box_aspect)
        else:
            r = expand_to_aspect(bbox, box_aspect)

        return r.anchored(self._anchor, bbox)

