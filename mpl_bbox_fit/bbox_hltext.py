# or

from .bbox_image import BboxDrawingArea

# For now, we assume HLT is already added to the axes, so that its figure has
# been set. This is required fro now since get_window_extent in the init
# requires the figure (or renderer). We may use blank renderer. Or we can defer
# this after figure is set on BHLT. The latter approach could be better as this
# can work when text changes.

class BboxHighlightText(BboxDrawingArea):
    def __init__(self, bbox, hlt, clip=False,
                 aspect=1, anchor="C", mode="contain", transform=None):

        # hlt.annotation_bbox.set_figure(self.fig)
        self._hlt = hlt
        extent = hlt.annotation_bbox.get_window_extent()

        self._hlt_w, self._hlt_h = w, h = extent.width, extent.height

        super().__init__(bbox, extent=(-w/2, 0, w/2, h), clip=clip,
                         aspect=aspect, anchor=anchor, mode=mode,
                         transform=transform)

        # self.add_artist(hlt)

        # hlt.annotation_bbox.xycoords = self.get_bbox_transform()
        # hlt.annotation_bbox.boxcoords = self.get_bbox_transform()

        def set_scale(renrerer, bboxout):
            scale = bboxout.height / h
            self.set_scale(scale)
            # print(bboxout, scale)

        self._pre_draw_hooks.append(set_scale)

    def set_scale(self, scale):
        for ta in self._hlt.text_areas:
            ta.set_scale(scale)
