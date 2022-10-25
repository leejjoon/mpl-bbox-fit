import matplotlib.pyplot as plt
from matplotlib.offsetbox import TextArea as _TextArea

from matplotlib.patheffects import (PathEffectRenderer as _PathEffectRenderer,
                                    Normal)

import matplotlib.transforms as mtrans

class PathEffectRenderer(_PathEffectRenderer):
    def set_scale(self, scale):
        self._scale = scale

    def _draw_text_as_path(self, gc, x, y, s, prop, angle, ismath):
        # Implements the naive text drawing as is found in RendererBase.
        # print("55", self._scale)
        path, transform = self._get_text_path_transform(x, y, s, prop,
                                                        angle, ismath)
        color = gc.get_rgb()
        gc.set_linewidth(0.0)

        scale_transform = mtrans.Affine2D().scale(self._scale)
        self.draw_path(gc, path, scale_transform + transform, rgbFace=color)

# class ScaledTextRenderer(RendererBase):
#     def __init__(self, renderer):
#         """
#         Parameters
#         ----------
#         path_effects : iterable of :class:`AbstractPathEffect`
#             The path effects which this renderer represents.
#         renderer : `matplotlib.backend_bases.RendererBase` subclass

#         """
#         self._renderer = renderer

#     def _get_text_path_transform(self, x, y, s, prop, angle, ismath):
#         path, trans = super()._get_text_path_transform(x, y, s, prop, angle, ismath)
#         print(2)
#         return path, trans + mtrans.Affine2D.scale(2)

#     def _draw_text_as_path(self, gc, x, y, s, prop, angle, ismath):
#         print(3)
#         return self._renderer._draw_text_as_path(gc, x, y, s, prop, angle, ismath)

#     def draw_text(self, gc, x, y, s, prop, angle, ismath, mtext):
#         # in the BackendBase, it calls, self._draw_text_as_path.

#         print(4)
#         return self.renderer.draw_text(gc, x, y, s, prop, angle, ismath=ismath, mtext=mtext)

#     # def __getattribute__(self, name):
#     #     if name in [
#     #             'draw_path', 'draw_markers', 'draw_path_collection',
#     #             'flipy', 'get_canvas_width_height', 'new_gc',
#     #             'points_to_pixels', '_text2path', 'height', 'width']:
#     #         return getattr(self._renderer, name)
#     #     else:
#     #         return object.__getattribute__(self, name)

#     def __getattribute__(self, name):
#         if name not in ['_get_text_path_transform', '_renderer',
#                         '_draw_text_as_path']:
#             return getattr(self._renderer, name)
#         else:
#             return object.__getattribute__(self, name)

import numpy as np
import matplotlib.text as mtext

class TTT(mtext.Text):
    def draw(self, renderer, scale=1):
        # docstring inherited

        if renderer is not None:
            self._renderer = renderer
        if not self.get_visible():
            return
        if self.get_text() == '':
            return

        renderer.open_group('text', self.get_gid())

        with self._cm_set(text=self._get_wrapped_text()):
            bbox, info, descent = self._get_layout(renderer)
            trans = self.get_transform()

            # don't use self.get_position here, which refers to text
            # position in Text:
            posx = float(self.convert_xunits(self._x))
            posy = float(self.convert_yunits(self._y))
            posx, posy = trans.transform((posx, posy))
            if not np.isfinite(posx) or not np.isfinite(posy):
                # _log.warning("posx and posy should be finite values")
                return
            canvasw, canvash = renderer.get_canvas_width_height()

            # Update the location and size of the bbox
            # (`.patches.FancyBboxPatch`), and draw it.
            if self._bbox_patch:
                self.update_bbox_position_size(renderer)
                self._bbox_patch.draw(renderer)

            gc = renderer.new_gc()
            gc.set_foreground(self.get_color())
            gc.set_alpha(self.get_alpha())
            gc.set_url(self._url)
            self._set_gc_clip(gc)

            angle = self.get_rotation()

            for line, wh, x, y in info:

                mtext = self if len(info) == 1 else None
                x = x + posx
                y = y + posy
                if renderer.flipy():
                    y = canvash - y
                clean_line, ismath = self._preprocess_math(line)

                # we always render text as path
                pe = self.get_path_effects()
                if not pe:
                    pe = [Normal()]
                textrenderer = PathEffectRenderer(pe, renderer)
                textrenderer.set_scale(scale)
                # if self.get_path_effects():
                #     # from matplotlib.patheffects import PathEffectRenderer
                #     textrenderer = PathEffectRenderer(
                #         self.get_path_effects(), renderer)
                #     textrenderer.set_scale(scale)
                # else:
                #     textrenderer = renderer

                if self.get_usetex():
                    textrenderer.draw_tex(gc, x, y, clean_line,
                                          self._fontproperties, angle,
                                          mtext=mtext)
                else:
                    textrenderer.draw_text(gc, x, y, clean_line,
                                           self._fontproperties, angle,
                                           ismath=ismath, mtext=mtext)

        gc.restore()
        renderer.close_group('text')
        self.stale = False


class TextArea(_TextArea):
    def __init__(self, s,
                 textprops=None,
                 multilinebaseline=False,
                 scale=None):
        super().__init__(s, textprops=textprops, multilinebaseline=multilinebaseline)

        self._scale = scale

    def set_scale(self, scale):
        self._scale = scale

    def get_extent(self, renderer):
        # print("ee", self._scale)
        extent = super().get_extent(renderer)
        if self._scale is None:
            return extent
        else:
            return [self._scale*s for s in extent]

    def draw(self, renderer):
        # print(1)
        # new_renderer = ScaledTextRenderer(renderer)

        # TTT.draw(self._text, new_renderer)
        if self._scale is None:
            self._text.draw(renderer)
        else:
            TTT.draw(self._text, renderer, scale=self._scale)
        # self._text.draw(new_renderer)
        # bbox_artist(self, renderer, fill=False, props=dict(pad=0.))
        self.stale = False


def monkey_patch():
    import matplotlib.offsetbox
    matplotlib.offsetbox.TextArea = TextArea
