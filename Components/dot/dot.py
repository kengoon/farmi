from kivymd.uix.widget import MDWidget
from kivy.properties import NumericProperty, ColorProperty, BooleanProperty
from os.path import join, basename, dirname
from kivy.lang import Builder

Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))

__all__ = ("Dot",)


class Dot(MDWidget):
    index = NumericProperty(0)
    normal_color = ColorProperty("#A9A9A9")
    active_color = ColorProperty(None)
    active = BooleanProperty(False)
