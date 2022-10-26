import matplotlib.transforms as mtrans

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

