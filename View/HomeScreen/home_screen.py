from View.base_screen import BaseScreenView
from kivymd.utils.set_bars_colors import set_bars_colors


class HomeScreenView(BaseScreenView):
    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """

    def on_enter(self, *args):
        set_bars_colors(
            self.theme_cls.surfaceColor,
            self.theme_cls.surfaceContainerHighestColor,
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )

    def on_leave(self, *args):
        set_bars_colors(
            self.theme_cls.surfaceColor,
            self.theme_cls.surfaceColor,
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )
