# This package is for additional application modules.
from kivy.core.text import Label
from kivy.metrics import sp


def shorten_text(text, lbl_width, lines=1, suffix="... See more", font_size=sp(12)):
    """
    Used to shorten text in kivy to number of lines you want unlike kivy which only shortens for
    one line

    :param text: text to shorten
    :param lbl_width: width of the original label containing the text to shorten
    :param lines: number of lines to shorten to
    :param suffix: suffix to add at the end of the text (e.g "suffix=.... see more")
    :param font_size: font_size of the original label containing the text to shorten
    :return: returns shorten text
    """
    lbl = Label(font_size=font_size)
    new_text = text
    text_width = lbl.get_cached_extents()
    t = 0
    lbl_width *= lines
    if lbl_width <= 0:
        return ""
    while text_width(new_text + suffix + " more")[0] > lbl_width:
        new_text = new_text.split(" ")
        del new_text[-1]
        new_text = " ".join(new_text)
        if text_width(new_text + suffix + " more")[0] == t:
            return ""
        t = text_width(new_text + suffix + " more")[0]
    return new_text + suffix


def get_dict_pos(lst, key, value):
    return next((index for (index, d) in enumerate(lst) if d[key] == value), None)


def search_dict(search_term, data_key, data):
    a = filter(lambda search_found: search_term in search_found[data_key], data)
    return list(a)
