from kivy.animation import Animation
from kivy.core.window import Window as w
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ListProperty, BooleanProperty, ColorProperty, StringProperty
from kivy.uix.widget import Widget
from kivymd.uix.badge import MDBadge
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem, MDNavigationItemLabel, MDNavigationItemIcon
from os.path import join, dirname, basename
from kivymd.uix.appbar import (
    MDTopAppBar,
    MDTopAppBarTitle,
    MDTopAppBarTrailingButtonContainer,
    MDTopAppBarLeadingButtonContainer,
    MDActionTopAppBarButton
)

Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))

__all__ = ("MDCustomNavigationBar", "MDCustomNavigationItem", "base_bar", "win_md_bnb", "win_md_tb", "win_button")


# --------------NavBar-----------------------#
class MDCustomNavigationItem(MDNavigationItem):
    icon = StringProperty()
    icon_color_active = ColorProperty(None)
    icon_color_normal = ColorProperty(None)
    text = StringProperty()
    text_color_active = ColorProperty(None)
    text_color_normal = ColorProperty(None)
    use_text = BooleanProperty(True)
    use_badge = BooleanProperty(False)
    badge_text = StringProperty()
    badge_text_color = ColorProperty(None)
    badge_bg_color = ColorProperty(None)
    ripple_effect = BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Clock.schedule_once(lambda _: self.prepare_badge_and_text())

    def prepare_badge_and_text(self):
        icon = MDNavigationItemIcon(
            icon=self.icon,
            icon_color_normal=self.icon_color_normal,
            icon_color_active=self.icon_color_active
        )
        self.bind(
            icon=icon.setter("icon"),
            icon_color_normal=icon.setter("icon_color_normal"),
            icon_color_active=icon.setter("icon_color_active")
        )
        if self.use_badge:
            badge = MDBadge(text=self.badge_text)
            if self.badge_text_color:
                badge.text_color = self.badge_text_color
            if self.badge_bg_color:
                badge.md_bg_color = self.badge_bg_color
            self.bind(
                badge_text=badge.setter("text"),
                badge_text_color=badge.setter("text_color"),
                badge_bg_color=badge.setter("md_bg_color")
            )
            icon.add_widget(badge)
        self.add_widget(icon)
        if self.use_text:
            lbl = MDNavigationItemLabel(
                text=self.text,
                text_color_active=self.text_color_active,
                text_color_normal=self.text_color_normal
            )
            self.bind(
                text=lbl.setter("text"),
                text_color_normal=lbl.setter("text_color_normal"),
                text_color_active=lbl.setter("text_color_active"),
            )
            self.add_widget(lbl)


class MDCustomNavigationBar(MDNavigationBar):
    tabs = ListProperty()
    use_text = BooleanProperty(True)
    indicator_color = ColorProperty(None)
    variant_icon = BooleanProperty(True)
    text_color_active = ColorProperty(None, allownone=True)
    text_color_normal = ColorProperty(None, allownone=True)
    icon_color_active = ColorProperty(None, allownone=True)
    icon_color_normal = ColorProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda _: self._add_tabs())

    def _add_tabs(self):
        for tab in self.tabs:
            btn = MDCustomNavigationItem(
                text=tab["text"],
                badge_text=tab.get("badge_text", ""),
                use_badge=tab.get("use_badge", False),
                active=tab.get("active", False),
                indicator_color=self.indicator_color,
                on_release=tab.get("on_release", lambda _: None)
            )
            self._variant_assignment(btn, tab)
            if self.text_color_active:
                btn.text_color_active = self.text_color_active
            if self.text_color_normal:
                btn.text_color_normal = self.text_color_normal
            if self.icon_color_active:
                btn.icon_color_active = self.icon_color_active
            if self.icon_color_normal:
                btn.icon_color_normal = self.icon_color_normal
            btn.bind(on_release=self._switch_active)
            self.bind(
                text_color_normal=btn.setter("text_color_normal"),
                text_color_active=btn.setter("text_color_active"),
                icon_color_normal=btn.setter("icon_color_normal"),
                icon_color_active=btn.setter("icon_color_active")
            )
            self.add_widget(btn)

    def _switch_active(self, instance):
        for child, tab in zip(self.children[::-1], self.tabs):
            if child == instance:
                child.active = True
                child.icon = tab["icon"]
                continue
            child.active = False
            self._variant_assignment(child, tab)
        anim = Animation(y=dp(-5), d=.05) + Animation(y=0, d=.05)
        anim.start(instance)

    def _variant_assignment(self, btn, tab):
        if self.variant_icon and not btn.active:
            btn.icon = tab["icon_variant"]
        else:
            btn.icon = tab["icon"]


# ---------------NavBar-----------------------------------------#


# ------------------AppBar------------------------------------- #
class MDCustomTopAppBar(MDTopAppBar):
    actions = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda _: self._add_actions())

    def on_type(self, instance, value) -> None:
        pass

    def _add_actions(self):
        for action in self.actions:
            match action["type"]:
                case "lead":
                    self.add_widget(
                        MDTopAppBarLeadingButtonContainer(
                            MDActionTopAppBarButton(
                                icon=action["icon"],
                                on_release=action.get("on_release", lambda _: None)
                            )
                        )
                    )
                case "title":
                    self.add_widget(
                        MDTopAppBarTitle(
                            text=action["title"]
                        )
                    )

                case "trail":
                    self.add_widget(
                        MDTopAppBarTrailingButtonContainer(
                            MDActionTopAppBarButton(
                                icon=action["icon"],
                                on_release=action.get("on_release", lambda _: None)
                            )
                        )
                    )

                case _:
                    raise TypeError("'type' must be one of ['lead', 'title', 'trail']")
        self.on_size(None, [])
        if self.type in ("medium", "large"):
            Clock.schedule_once(
                lambda _: self.ids.root_box.add_widget(Widget(), index=1),
                .2
            )


# --------------------------AppBar--------------------------------------------------#


# -----------------------------DisturbButton------------------------ #
class DisturbButton(MDBoxLayout):
    text = StringProperty()

    def __init__(self, *args, **kwargs):
        self.register_event_type("on_release")
        super().__init__(*args, **kwargs)

    def on_release(self, *args):
        pass


class base_bar:
    bar = None
    state = "pop"
    bind_win_size_to_bar_pos = None
    _pop_listeners = []
    _push_listeners = []
    _push_height = 0
    _y = 0

    @classmethod
    def push(cls):
        cls.state = "push"
        for func in cls._push_listeners:
            func()

    @classmethod
    def pop(cls):
        cls.state = "pop"
        for func in cls._pop_listeners:
            func()

    @classmethod
    def remove_bnb(cls):
        cls.pop()
        w.remove_widget(cls.bar)
        cls.bar = None
        cls.bind_win_size_to_bnb_pos = None
        cls._pop_listeners.clear()
        cls._push_listeners.clear()

    @classmethod
    def _bind_win_size_width(cls):
        if cls.bar:
            w.bind(size=cls.bind_win_size_to_bar_pos)

    @classmethod
    def _unbind_win_size_width(cls):
        if cls.bar:
            w.unbind(size=cls.bind_win_size_to_bar_pos)

    @classmethod
    def register_listener(cls, **kwargs):
        if func := kwargs.get("pop"):
            cls._pop_listeners.append(func)
        if func := kwargs.get("push"):
            cls._push_listeners.append(func)


class win_md_bnb(base_bar):
    @classmethod
    def create_bnb(
            cls,
            md_bg_color=None,
            use_text=True,
            indicator_color=None,
            variant_icon=True,
            tabs=None,
            text_color_active=None,
            text_color_normal=None,
            icon_color_active=None,
            icon_color_normal=None,
            radius=0,
            set_bars_color=False
    ):
        if cls.bar:
            return
        if tabs is None:
            tabs = []
        cls.bar = MDCustomNavigationBar(
            tabs=tabs,
            variant_icon=variant_icon,
            indicator_color=indicator_color,
            use_text=use_text,
            text_color_active=text_color_active,
            text_color_normal=text_color_normal,
            icon_color_active=icon_color_active,
            icon_color_normal=icon_color_normal,
            set_bars_color=set_bars_color
        )
        if md_bg_color:
            cls.bar.md_bg_color = md_bg_color
        if radius is not None:
            cls.bar.radius = radius
        cls.bar.y = -cls.bar.height - dp(20)
        w.add_widget(cls.bar)

    @classmethod
    def push(cls):
        Animation(y=-0.5, d=.2).start(cls.bar)
        super().pop()

    @classmethod
    def pop(cls):
        Animation(y=-cls.bar.height - dp(20), d=.2).start(cls.bar)
        super().pop()


class win_md_tb(base_bar):
    @classmethod
    def create_tb(cls, actions, type="small", set_bars_color=False):
        if cls.bar:
            return
        if actions is None:
            actions = []
        cls.bar = MDCustomTopAppBar(
            actions=actions,
            type=type,
            set_bars_color=set_bars_color,
        )
        cls._y = w.height + dp(20)
        cls.bar.y = cls._y
        cls.bind_win_size_to_bar_pos = lambda _, s: setattr(cls.bar, "y", cls._y)
        cls._bind_win_size_width()
        w.add_widget(cls.bar)

    @classmethod
    def push(cls):
        cls._y = w.height - cls.bar.height
        Animation(y=cls._y, d=.2).start(cls.bar)
        super().pop()

    @classmethod
    def pop(cls):
        cls._y = w.height + dp(20)
        Animation(y=cls._y, d=.2).start(cls.bar)
        super().pop()


class win_button(base_bar):
    @classmethod
    def create_button(
            cls,
            text,
            on_release=lambda _: None,
    ):
        cls.bar = DisturbButton(
            text=text,
            on_release=on_release
        )
        cls.bar.y = -cls.bar.height - dp(20)
        w.add_widget(cls.bar)

    @classmethod
    def push(cls):
        Animation(y=0, d=.2).start(cls.bar)
        super().push()

    @classmethod
    def pop(cls):
        Animation(y=-cls.bar.height - dp(20), d=.2).start(cls.bar)
        super().pop()


if __name__ == "__main__":
    from kivymd.app import MDApp


    class TestApp(MDApp):
        def on_start(self):
            super().on_start()
            win_md_bnb.create_bnb(
                tabs=[
                    {
                        "icon": "web",
                        "icon_variant": "web",
                        "text": "Discover",
                        "active": True,
                        "use_badge": True,
                        "badge_text": "900"
                    },
                    {
                        "icon": "fire-circle",
                        "icon_variant": "fire",
                        "text": "Memoir",
                    },
                    {
                        "icon": "dots-horizontal",
                        "icon_variant": "dots-horizontal",
                        "text": "More",
                    }
                ],
            )
            win_md_bnb.push()

            win_md_tb.create_tb(
                actions=[
                    {
                        "type": "lead",
                        "icon": "arrow-left"
                    },
                    {
                        "type": "title",
                        "title": "AppBar"
                    },
                    {
                        "type": "trail",
                        "icon": "magnify"
                    }
                ],
            )
            win_md_tb.push()

            win_button.create_button(text="hello")
            win_button.push()


    TestApp().run()
