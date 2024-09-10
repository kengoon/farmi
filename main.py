"""
The entry point to the application.

The application uses the MVC template. Adhering to the principles of clean
architecture means ensuring that your application is easy to test, maintain,
and modernize.

You can read more about this template at the links below:

https://github.com/HeaTTheatR/LoginAppMVC
https://en.wikipedia.org/wiki/Model–view–controller
"""
import os
from os import path

from kivy.loader import Loader
from kivymd import images_path
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.transition import MDSharedAxisTransition
from kivymd.uix.progressindicator import MDCircularProgressIndicator
from kivy.uix.modalview import ModalView
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.utils.set_bars_colors import set_bars_colors
from kivy.core.window import Window

from View.screens import screens
from Model.database import DataBase
from Components.factory import register_factory

register_factory()
# Loader.error_image = path.join(images_path, "transparent.png")
# Loader.loading_image = path.join(images_path, "transparent.png")
Window.softinput_mode = "below_target"


class Farmi(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.database = DataBase()
        self.screens = []
        self.dialog = None
        self.theme_cls.bind(
            theme_style=self.update_colors,
            surfaceColor=Window.setter("clearcolor")
        )
        self.theme_cls.bind(
            surfaceColor=self.update_colors
        )
        Window.bind(on_keyboard=self.on_back_button)

    def build(self):
        # Uncomment me if you need me
        Builder.load_file("imports.kv")
        # self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        # self.theme_cls.dynamic_scheme_contrast = -1

        spinner = MDCircularProgressIndicator(line_width=dp(1.5))
        self.dialog = ModalView(
            auto_dismiss=False,
            background="",
            background_color=[0] * 4,
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            on_pre_open=lambda _: setattr(spinner, "active", True),
            on_dismiss=lambda _: setattr(spinner, "active", False)
        )
        self.dialog.add_widget(spinner)

        # This is the screen manager that will contain all the screens of your
        # application.
        self.root = MDScreenManager(transition=MDSharedAxisTransition())
        self.add_screen("home screen", first=True)

    @staticmethod
    def update_colors(instance, value):
        set_bars_colors(
            instance.surfaceColor,
            instance.surfaceColor,
            "Dark" if value == "Light" else "Light"
        )

    def add_screen(self, name_screen, switch=True, first=False):
        if first:
            self.load_screen(name_screen, switch, first)
            return
        if not self.root.has_screen(name_screen):
            self.dialog.open()
            Clock.schedule_once(lambda _: self.load_screen(name_screen, switch, first), 1)
        elif switch:
            if self.root.current:
                self.screens.append(self.root.current)
            self.root.current = name_screen
            self.dialog.dismiss()

    def load_screen(self, name_screen, switch, first):
        Builder.load_file(screens[name_screen]["kv"])
        model = screens[name_screen]["model"](self.database)
        controller = screens[name_screen]["controller"](self, model)
        view = screens[name_screen]["view"](self, model=model, controller=controller)
        controller.set_view(view)
        self.root.add_widget(view)
        if switch:
            if self.root.current and not first:
                self.screens.append(self.root.current)
            self.root.current = name_screen
        self.dialog.dismiss()

    def on_back_button(self, _, key, *__):
        if key in [27, 1001]:
            try:
                self.root.current = self.screens.pop()
                return True
            except IndexError:
                return False

    def on_stop(self):
        os.rmdir("images")


if __name__ == "__main__":
    Farmi().run()
