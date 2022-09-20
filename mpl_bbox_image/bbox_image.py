from matplotlib.image import BboxImage as _BboxImage


class BboxImage(_BboxImage):
    """The Image class whose size is determined by the given bbox."""

    def __init__(self, bbox,
                 aspect=1,
                 anchor="C",
                 **kwargs
                 ):
        """
        Parameters
        ----------
        aspect : float or "auto"

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

    def get_window_extent(self, renderer=None):
        """get the window extent from the given bbox, then apply aspec and anchor."""
        bbox = super().get_window_extent(renderer)

        if self._aspect == "auto":
            return bbox

        ny, nx = self._A.shape[:2]

        box_aspect = self._aspect * ny / nx
        return bbox.shrunk_to_aspect(box_aspect).anchored(self._anchor, bbox)

