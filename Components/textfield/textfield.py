from os.path import join, dirname, basename

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, OptionProperty, NumericProperty, \
    ColorProperty, VariableListProperty
from kivy.lang import Builder
from kivy.resources import resource_find
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDIcon
from kivymd.uix.card import MDCard

Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))

__all__ = ("TextField", "TagTextField")


class TextField(MDCard):
    icon_right_color = ColorProperty(None)
    icon_left_color = ColorProperty(None)
    md_font = StringProperty(resource_find("materialdesignicons-webfont.ttf"))
    icon_left_font_style = StringProperty("Icons")
    icon_right_font_style = StringProperty("Icons")
    text = StringProperty()
    field_disabled = BooleanProperty(False)
    cursor_color = ColorProperty(None)
    foreground_color = ColorProperty([0, 0, 0, 1])
    disabled_foreground_color = ColorProperty([0, 0, 0, .5])
    focus_type = OptionProperty("null", options=["line", "shadow", "null"])
    focus_line_color = ColorProperty(None)
    focus_shadow_color = ColorProperty(None)
    multiline = BooleanProperty(False)
    password = BooleanProperty(False)
    keyboard_suggestions = BooleanProperty(True)
    password_mask = StringProperty('*')
    hint_text = StringProperty()
    radius = VariableListProperty("10dp")
    padding = VariableListProperty("10dp")
    halign = OptionProperty('auto', options=['left', 'center', 'right',
                            'auto'])
    write_tab = BooleanProperty(False)
    icon_left = StringProperty()
    icon_right = StringProperty()
    focus = BooleanProperty(False)
    font_size = NumericProperty('16sp')
    input_filter = ObjectProperty(None, allownone=True)
    input_type = OptionProperty(
        'text',
        options=(
            'null',
            'text',
            'number',
            'url',
            'mail',
            'datetime',
            'tel',
            'address'
        )
    )
    theme_icon_left_color = OptionProperty(
        "Primary",
        allownone=True,
        options=[
            "Primary",
            "Secondary",
            "Hint",
            "Error",
            "Custom"
        ],
    )
    theme_icon_right_color = OptionProperty(
        "Primary",
        allownone=True,
        options=[
            "Primary",
            "Secondary",
            "Hint",
            "Error",
            "Custom"
        ],
    )

    def __init__(self, *args, **kwargs):
        self._unfocus_md_bg_color = None
        self._unfocus_line_width = None
        self._unfocus_elevation = None
        self.register_event_type("on_icon_left_release")
        self.register_event_type("on_icon_right_release")
        self.register_event_type("on_text_validate")
        super().__init__(*args, **kwargs)
        self.bind(focus=self.activate_field)
        Clock.schedule_once(lambda _: self.add_icons())
        self._unfocus_shadow_color = None
        self._unfocus_line_color = None

    def add_icons(self):
        if self.icon_left:
            icon = MDIcon(
                pos_hint={"center_y": .5},
                icon=self.icon_left,
                icon_color=self.icon_left_color,
                theme_icon_color=self.theme_icon_left_color,
                font_size=self.font_size,
                font_name=self.icon_left_font_style,
                on_touch_up=self._dispatch_icon_left_touch
            )
            self.bind(
                icon_left=icon.setter("icon"),
                font_size=icon.setter("font_size"),
                icon_left_font_style=icon.setter("font_name"),
                icon_left_color=icon.setter("icon_color"),
                theme_icon_left_color=icon.setter("theme_icon_color")
            )
            self.add_widget(icon, index=len(self.children))

        if self.icon_right:
            icon = MDIcon(
                adaptive_size=True,
                pos_hint={"center_y": .5},
                icon=self.icon_right,
                icon_color=self.icon_right_color,
                theme_icon_color=self.theme_icon_right_color,
                font_size=self.font_size,
                font_name=self.icon_right_font_style,
                on_touch_up=self._dispatch_icon_right_touch
            )
            self.bind(
                icon_right=icon.setter("icon"),
                icon_right_color=icon.setter("icon_color"),
                theme_icon_right_color=icon.setter("theme_icon_color"),
                font_size=icon.setter("font_size"),
                icon_right_font_style=icon.setter("font_name")
            )
            self.add_widget(icon)

    def activate_field(self, _, value):  # sourcery skip: merge-else-if-into-elif
        if self.focus_type == "null":
            return
        if value:
            self._unfocus_md_bg_color = self.md_bg_color
            if self.focus_type == "line":
                self._unfocus_line_color = self.line_color
                self._unfocus_line_width = self.line_width
                Animation(
                    line_color=self.focus_line_color or self.theme_cls.primary_color,
                    line_width=max(self.line_width, 1.2),
                    md_bg_color=(0, 0, 0, 0),
                    duration=.2,
                ).start(self)
            else:
                self._unfocus_shadow_color = self.shadow_color
                self._unfocus_elevation = self.elevation
                Animation(
                    shadow_color=self.focus_shadow_color or self.theme_cls.primary_color,
                    elevation=max(2, self.elevation),
                    md_bg_color=(0, 0, 0, 0),
                    duration=.2,
                ).start(self)
        else:
            if self.focus_type == "line":
                Animation(
                    line_color=self._unfocus_line_color,
                    line_width=self._unfocus_line_width,
                    md_bg_color=self._unfocus_md_bg_color,
                    duration=.2
                ).start(self)
            else:
                Animation(
                    shadow_color=self._unfocus_shadow_color,
                    elevation=self._unfocus_elevation,
                    md_bg_color=self._unfocus_md_bg_color,
                    duration=.2
                ).start(self)

    def _dispatch_icon_left_touch(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.dispatch("on_icon_left_release")

    def _dispatch_icon_right_touch(self, instance, touch):
        if instance.collide_point(*touch.pos):
            self.dispatch("on_icon_right_release")

    def on_icon_right_release(self, *args):
        pass

    def on_icon_left_release(self, *args):
        pass

    def on_text_validate(self, *args):
        pass


class TagTextField(MDBoxLayout):
    tag = StringProperty()
    icon_right_color = ColorProperty(None)
    icon_left_color = ColorProperty(None)
    md_font = StringProperty(resource_find("materialdesignicons-webfont.ttf"))
    icon_left_font_style = StringProperty("Icons")
    icon_right_font_style = StringProperty("Icons")
    text = StringProperty()
    keyboard_suggestions = BooleanProperty(True)
    focus_type = OptionProperty("null", options=["line", "shadow", "null"])
    focus_line_color = ColorProperty(None)
    focus_shadow_color = ColorProperty(None)
    disabled_foreground_color = ColorProperty([0, 0, 0, .5])
    foreground_color = ColorProperty([0, 0, 0, 1])
    multiline = BooleanProperty(False)
    password = BooleanProperty(False)
    password_mask = StringProperty('*')
    hint_text = StringProperty()
    write_tab = BooleanProperty(False)
    icon_left = StringProperty()
    icon_right = StringProperty()
    focus = BooleanProperty(False)
    font_size = NumericProperty('15sp')
    input_filter = ObjectProperty(None, allownone=True)
    line_width = NumericProperty(1)
    line_color = ColorProperty([0, 0, 0, 0])
    bg_color = ColorProperty("#F1F1F1")
    radius = VariableListProperty([dp(6), dp(6), dp(6), dp(6)])
    field_padding = VariableListProperty("10dp")
    input_type = OptionProperty('null', options=('null', 'text', 'number',
                                                 'url', 'mail', 'datetime',
                                                 'tel', 'address'))
    theme_icon_color = OptionProperty(
        "Primary",
        allownone=True,
        options=[
            "Primary",
            "Secondary",
            "Hint",
            "Error",
            "Custom",
            "ContrastParentBackground",
        ],
    )

    def __init__(self, **kwargs):
        self.register_event_type("on_text_validate")
        self.register_event_type("on_icon_left_release")
        self.register_event_type("on_icon_right_release")
        super().__init__(**kwargs)

    def on_text_validate(self, *args):
        pass

    def on_icon_left_release(self, *args):
        pass

    def on_icon_right_release(self, *args):
        pass

