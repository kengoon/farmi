from typing import Union

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import BooleanProperty, NumericProperty, BoundedNumericProperty, ObjectProperty, ColorProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from textwrap import dedent
from Components.dot import Dot
from os.path import join, dirname, basename
Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))

__all__ = ("DotSpinner", "DotCarousel")


class DotCarousel(MDBoxLayout):
    index = NumericProperty()
    dash = NumericProperty(3)
    active_size = NumericProperty("60dp")
    normal_size = NumericProperty("48dp")
    active_color = ColorProperty()
    normal_color = ColorProperty("#AAAAAA")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_once(lambda _: self.add_dash())
        self.bind(index=self.switch_current)

    def switch_current(self, *_):
        current = None
        previous = None
        for child in self.children:
            if self.index == child.index:
                current = child
                continue
            if child.active:
                previous = child
        previous.active = False
        current.active = True
        Animation(width=self.active_size, duration=.3).start(current)
        Animation(width=self.normal_size, duration=.3).start(previous)

    def add_dash(self):
        for i in range(self.dash):
            self.add_widget(
                Dot(
                    index=i,
                    width=self.active_size if self.index == i else self.normal_size,
                    active_color=self.active_color,
                    normal_color=self.normal_color,
                    active=self.index == i
                )
            )


class DotSpinner(MDBoxLayout):
    active = BooleanProperty(False)
    dot_num = NumericProperty(5)
    speed = NumericProperty(.5)
    _current_active_dot_index = BoundedNumericProperty(0, min=0, max=dot_num.defaultvalue - 1, errorvalue=0)
    _animating = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clock = None

    def on_kv_post(self, base_widget):
        self.property("_current_active_dot_index").set_max(self, self.dot_num - 1)
        self.add_dots()

    def add_dots(self):
        for i in range(self.dot_num):
            self.add_widget(Dot(index=i))

    def get_current_active_dot(self) -> Union[Dot, None]:
        for dot in self.children:
            if dot.active:
                return dot

    def get_dot_index(self, index: int = 0) -> Dot:
        for dot in self.children:
            if dot.index == index:
                return dot

    def on_active(self, _, active_value: bool) -> None:
        if active_value:
            self.check_active()
        elif self.clock:
            self.clock.cancel()
            self.deactivate_dots_except()
            self._current_active_dot_index = 0
            self._animating = False

    def check_active(self):
        if self.active and not self._animating:
            self.clock = Clock.schedule_interval(self._animate_spinner, self.speed)
            self._animating = True

    def deactivate_dots_except(self, dot_instance: [Dot, None] = None) -> None:
        for dot in self.children:
            if dot == dot_instance:
                continue
            dot.active = False

    def _animate_spinner(self, _) -> None:
        index_max = self.property("_current_active_dot_index").get_max
        if not self.get_current_active_dot() or (self._current_active_dot_index == index_max):
            dot = self.get_dot_index()
        else:
            self._current_active_dot_index += 1
            dot = self.get_dot_index(self._current_active_dot_index)
        dot.active = True
        self.deactivate_dots_except(dot)


if __name__ == "__main__":
    from kivymd.app import MDApp
    from kivy.lang import Builder


    class Test(MDApp):
        def build(self):
            return Builder.load_string(
                dedent(
                    """
                FloatLayout:
                    DotSpinner
                        active: True
                        dot_num: 5
                        pos_hint:{"center": [.5, .5]}
                        on_touch_down: self.active = False if self.active else True
                """
                )
            )

        # def on_start(self):
        #     self.root.add_widget(DotSpinner(active=True, dot_num=5, pos_hint={"center": [.5, .5]}))


    Test().run()
