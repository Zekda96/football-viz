from colorsys import rgb_to_hsv, hsv_to_rgb
from PIL import ImageColor
from matplotlib.colors import LinearSegmentedColormap


"""
Small lib to create custom colormaps
"""


def short_hex(hex_tpl: tuple):
    out = []
    for i in hex_tpl:
        if len(i) == 3:
            out.append(f'0{i[-1]}')
        elif len(i) == 4:
            out.append(f'{i[-2:]}')
    return tuple(out)


def rgb2hex(rgbv: tuple):
    rgbh = (hex(round(rgbv[0])), hex(round(rgbv[1])), hex(round(rgbv[2])))
    rgbh = short_hex(rgbh)
    hex_vals = f'#{rgbh[0]}{rgbh[1]}{rgbh[2]}'
    return hex_vals


def custom_cmap(clr: str, sat_diff1=0.2, sat_diff2=0.25, bright_diff=0.6):
    c3 = clr
    c3_rgb = ImageColor.getcolor(c3, "RGB")
    c3_hsv = rgb_to_hsv(c3_rgb[0], c3_rgb[1], c3_rgb[2])

    c1 = hsv_to_rgb(c3_hsv[0], c3_hsv[1] * sat_diff1, 255)
    c1 = rgb2hex(c1)
    c2 = hsv_to_rgb(c3_hsv[0], c3_hsv[1] * sat_diff2, 255)
    c2 = rgb2hex(c2)
    c4 = hsv_to_rgb(c3_hsv[0], c3_hsv[1], c3_hsv[2] * bright_diff)
    c4 = rgb2hex(c4)

    color_list = [c1, c2, c3, c4]
    cmap = LinearSegmentedColormap.from_list("custom", color_list)
    return cmap
