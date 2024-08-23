from kivy.clock import Clock
from kivy.properties import StringProperty
from kivymd.uix.behaviors import StencilBehavior
from os.path import join, basename, dirname
from kivy.lang import Builder
from kivy.uix.image import AsyncImage

from libs import shorten_text

Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))

__all__ = ("CoverImage", )


class CoverImage(AsyncImage, StencilBehavior):
    fit_mode = StringProperty("cover")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clock = Clock.create_trigger(self.try_load_image, 1, True)

    def try_load_image(self, _):
        self.reload()
        self.clock.cancel()

    def on_load(self, *args):
        self.clock.cancel()

    def on_error(self, error):
        self.clock()
