from matplotlib.artist import Artist
import matplotlib.transforms as mtrans
from matplotlib.image import BboxImage as _BboxImage

from matplotlib.patches import Patch, draw_bbox

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

def expand_to_aspect(bbox, box_aspect, container=None, fig_aspect=1.0):
    """
    Return a copy of the `Bbox`, expand so that it is as
    small as it can be to include the container
    while having the desired aspect ratio,
    *box_aspect*.  If the box coordinates are relative (i.e.
    fractions of a larger box such as a figure) then the
    physical aspect ratio of that figure is specified with
    *fig_aspect*, so that *box_aspect* can also be given as a
    ratio of the absolute dimensions, not the relative dimensions.
    """
    if box_aspect <= 0 or fig_aspect <= 0:
        raise ValueError("'box_aspect' and 'fig_aspect' must be positive")
    if container is None:
        container = bbox
    w, h = container.size
    H = w * box_aspect / fig_aspect
    if H >= h:
        W = w
    else:
        W = h * fig_aspect / box_aspect
        H = h
    return mtrans.Bbox([bbox._points[0],
                        bbox._points[0] + (W, H)])

from enum import Enum


class BboxeMode(Enum):
    CONTAIN = "contain"
    FILL = "fill"
    COVER = "cover"


class BboxDrawingArea():
    pass

class BboxImage(_BboxImage):
    """The Image class whose size is determined by the given bbox."""

    def __init__(self, bbox,
                 mode=BboxeMode.FILL,
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
        self._mode = BboxeMode(mode)

    def get_window_extent(self, renderer=None):
        """get the window extent from the given bbox, then apply aspec and anchor."""
        bbox = super().get_window_extent(renderer)

        if self._mode == BboxeMode.FILL:
            return bbox

        ny, nx = self._A.shape[:2]

        box_aspect = self._aspect * ny / nx
        if self._mode == BboxeMode.CONTAIN:
            r = bbox.shrunk_to_aspect(box_aspect)
        else:
            r = expand_to_aspect(bbox, box_aspect)

        return r.anchored(self._anchor, bbox)


class BboxDrawingArea(Artist):
    """
    The DrawingArea can contain any Artist as a child. The DrawingArea
    has a fixed width and height. The position of children relative to
    the parent is fixed. The children can be clipped at the
    boundaries of the parent.
    """

    def __init__(self, bbox, extent=None, clip=False,
                 aspect=1, anchor="C", mode="fill", transform=None):
        """
        Parameters
        ----------
        clip : bool
            Whether to clip the children to the box. Otherwise,
            childrent are clipped by the axes.patch. Note that
            if clip is True, the artists won't be clipped with
            axes.patch.
        """
        super().__init__()
        if transform is not None:
            self.set_transform(transform)
        self._bbox = bbox
        self._clip_children = clip
        _extent = [0, 0, 1, 1] if extent is None else extent
        self._extent_bbox = mtrans.Bbox.from_extents(*_extent)
        self._children = []

        self._aspect = aspect
        self._anchor = anchor
        self._mode = BboxeMode(mode)

        # self._boxout = mtrans.TransformedBbox(self._bbox, self.get_transform())
        self._boxout = mtrans.Bbox.from_extents(0, 0, 1, 1) # boxout in canvas
                                                            # coordinate.
                                                            # Should be updated
                                                            # in drawing time.
        boxin = self._extent_bbox
        self._bbox_transform = mtrans.BboxTransform(boxin, self._boxout)
        self._pre_draw_hooks = []

    @property
    def clip_children(self):
        """
        If the children of this DrawingArea should be clipped
        by DrawingArea bounding box.
        """
        return self._clip_children

    @clip_children.setter
    def clip_children(self, val):
        self._clip_children = bool(val)
        self.stale = True

    def get_bbox_transform(self):
        # boxout = mtrans.TransformedBbox(self._bbox, self.get_transform())
        # # boxin = mtrans.Bbox.from_extents(self._extent)
        # boxin = self._extent_bbox
        # bbox_transform = mtrans.BboxTransform(boxin, boxout)
        # return bbox_transform

        return self._bbox_transform


    def add_artist(self, a):
        """Add an `.Artist` to the container box."""
        self._children.append(a)
        if not a.is_transform_set():
            a.set_transform(self.get_bbox_transform())
        if self.axes is not None:
            a.axes = self.axes
            a.set_clip_path(a.axes.patch)

        if self._clip_children:
            a.set_clip_box(self._boxout)

        fig = self.figure
        if fig is not None:
            a.set_figure(fig)

    def draw(self, renderer):
        # docstring inherited

        self._update_bbox_out(renderer)

        for f in self._pre_draw_hooks:
            f(renderer, self._boxout)

        # # At this point the DrawingArea has a transform
        # # to the display space so the path created is
        # # good for clipping children
        # tpath = mtransforms.TransformedPath(
        #     mpath.Path([[0, 0], [0, self.height],
        #                 [self.width, self.height],
        #                 [self.width, 0]]),
        #     self.get_transform())
        for c in self._children:
            # if self._clip_children and not (c.clipbox or c._clippath):
            #     c.set_clip_path(self._bbox_out)
            c.draw(renderer)

        # bbox_artist(self, renderer, fill=False, props=dict(pad=0.))
        self.stale = False


    def _update_bbox_out(self, renderer):
        outbox = self.get_window_extent(renderer)
        self._boxout.bounds = outbox.bounds


    def get_bbox_window_extent(self, renderer):
        boxout = mtrans.TransformedBbox(self._bbox, self.get_transform())
        return boxout
        # return super().get_window_extent(renderer)

    def get_window_extent(self, renderer=None):
        """get the window extent from the given bbox, then apply aspec and anchor."""
        bbox = self.get_bbox_window_extent(renderer)

        if self._mode == BboxeMode.FILL:
            return bbox

        ny, nx = self._extent_bbox.height, self._extent_bbox.width
        # ny, nx = self._A.shape[:2]

        box_aspect = self._aspect * ny / nx
        if self._mode == BboxeMode.CONTAIN:
            r = bbox.shrunk_to_aspect(box_aspect)
        else:
            r = expand_to_aspect(bbox, box_aspect)

        return r.anchored(self._anchor, bbox)

def main():

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1, clear=True, num=1)

    bbox = mtrans.Bbox.from_extents(0, 0, 1, 0.5)
    da = BboxDrawingArea(bbox, extent=(0, 0, 10, 1), mode="contain")
    bbox2 = mtrans.Bbox.from_extents(0, 0.5, 1, 1.)
    da2 = BboxDrawingArea(bbox2, extent=(0, 0, 10, 1), mode="contain",
                          trans=ax.transAxes, transform=ax.transAxes)
    ax.add_artist(da)
    ax.add_artist(da2)
    # ax.set(xlim=(-1, 2), ylim=(-1, 2))

    rect = plt.Rectangle((0, 0), 10, 1)
    da.add_artist(rect)
    rect = plt.Rectangle((0, 0), 10, 1)
    da2.add_artist(rect)

    ax.add_artist(BboxPatch(bbox, trans=ax.transData))

    plt.show()
