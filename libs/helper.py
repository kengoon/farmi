from math import cos, radians, sin
import random


def point_on_circle(degree, center, dis):
    """
    Finding the x,y coordinates on circle, based on given angle
    """

    if 0 <= degree <= 90:
        degree = 90 - degree
    elif 90 < degree < 360:
        degree = 450 - degree

    radius = dis
    angle = radians(degree)

    x = center[0] + (radius * cos(angle))
    y = center[1] + (radius * sin(angle))

    return [x, y]


def generate_distinct_material_color():
    # Hue (0 to 360 degrees) - picking from the color wheel
    hue = random.uniform(0, 360)

    # Saturation (0.5 to 1) for vibrant colors
    saturation = random.uniform(0.5, 1.0)

    # Lightness (0.4 to 0.7) to avoid too dark or too light colors
    lightness = random.uniform(0.4, 0.7)

    # Convert HSL to RGB
    chroma = (1 - abs(2 * lightness - 1)) * saturation
    x = chroma * (1 - abs((hue / 60) % 2 - 1))
    m = lightness - chroma / 2

    if 0 <= hue < 60:
        r, g, b = chroma, x, 0
    elif 60 <= hue < 120:
        r, g, b = x, chroma, 0
    elif 120 <= hue < 180:
        r, g, b = 0, chroma, x
    elif 180 <= hue < 240:
        r, g, b = 0, x, chroma
    elif 240 <= hue < 300:
        r, g, b = x, 0, chroma
    else:
        r, g, b = chroma, 0, x

    # Adjust the values to be between 0 and 1
    r, g, b = r + m, g + m, b + m

    # Keep alpha fully opaque
    a = 1.0

    return [r, g, b, a]
