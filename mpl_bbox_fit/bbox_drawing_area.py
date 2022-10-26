from matplotlib.artist import Artist
import matplotlib.transforms as mtrans

from .bbox_util import expand_to_aspect
from .bbox_fit_mode import BboxFitMode


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
        self._mode = BboxFitMode(mode)

        self._boxout = mtrans.Bbox.from_extents(0, 0, 1, 1)
        # boxout in canvas coordinate. Should be updated at drawing time.

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

        for c in self._children:
            c.draw(renderer)

        # bbox_artist(self, renderer, fill=False, props=dict(pad=0.))
        self.stale = False

    def _update_bbox_out(self, renderer):
        outbox = self.get_window_extent(renderer)
        self._boxout.bounds = outbox.bounds

    def get_bbox_window_extent(self, renderer):
        boxout = mtrans.TransformedBbox(self._bbox, self.get_transform())
        return boxout

    def get_window_extent(self, renderer=None):
        """get the window extent from the given bbox, then apply aspec and anchor."""
        bbox = self.get_bbox_window_extent(renderer)

        if self._mode == BboxFitMode.FILL:
            return bbox

        ny, nx = self._extent_bbox.height, self._extent_bbox.width
        # ny, nx = self._A.shape[:2]

        box_aspect = self._aspect * ny / nx
        if self._mode == BboxFitMode.CONTAIN:
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
