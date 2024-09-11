import contextlib
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse
from kivy.lang.builder import Builder
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.utils import get_color_from_hex
from kivymd.theming import ThemableBehavior
from kivymd.uix.label import MDLabel
from os.path import join, dirname, basename
from libs.helper import point_on_circle
from Components.drawtools import DrawTools
from Components.drawtools import draw_shape

"""issues
color_mode
"""

__all__ = (
    "PieChart",
    "LineChart",
    "BarChart",
)

Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))


class EmptyValueException(Exception):
    pass


class PieChartNumberLabel(MDLabel):
    percent = NumericProperty(0)
    title = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda x: self._update())

    def _update(self):
        self.x -= self.width / 2
        self.y -= self.height / 2


class PieChart(ThemableBehavior, BoxLayout):
    items = ListProperty()
    order = BooleanProperty(True)
    starting_animation = BooleanProperty(True)
    transition = StringProperty("out_cubic")
    duration = NumericProperty(1)
    color_mode = OptionProperty(
        "colors", options=["primary_color", "accent_color"]
    )  # not solved

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _format_items(self, items):
        percentage_sum = sum(v for k, v in items[0].items())
        if percentage_sum != 100:
            raise ValueError("Sum of percentages must be 100")

        new_items = {k: 360 * v / 100 for k, v in items[0].items()}
        if self.order:
            new_items = dict(sorted(new_items.items(), key=lambda item: item[1]))

        return new_items

    def _make_chart(self, items):
        self.size = (min(self.size), min(self.size))
        if not items:
            raise EmptyValueException("Items cannot be empty.")

        items = self._format_items(items)
        angle_start = 0
        circle_center = [
            self.pos[0] + self.size[0] / 2,
            self.pos[1] + self.size[1] / 2,
        ]

        for title, value in items.items():
            with self.canvas.before:

                alpha = 0 if self.starting_animation else 1
                if title == "Healthy Area":
                    color = self.theme_cls.primaryColor
                else:
                    color = self.theme_cls.errorColor

                c = Color(rgb=color, a=alpha)
                if self.starting_animation:
                    e = Ellipse(
                        pos=self.pos,
                        size=self.size,
                        angle_start=angle_start,
                        angle_end=angle_start + 0.01,
                    )

                    anim = Animation(
                        size=self.size,
                        angle_end=angle_start + value,
                        duration=self.duration,
                        t=self.transition,
                    )
                    anim_opcity = Animation(a=1, duration=self.duration * 0.5)

                    anim_opcity.start(c)
                    anim.start(e)
                else:
                    Ellipse(
                        pos=self.pos,
                        size=self.size,
                        angle_start=angle_start,
                        angle_end=angle_start + value,
                    )
            angle_start += value

        angle_start = 0
        for title, value in items.items():
            with self.canvas.after:
                label_pos = point_on_circle(
                    (angle_start + angle_start + value) / 2,
                    circle_center,
                    self.size[0] / 3,
                )
                number_anim = PieChartNumberLabel(
                    x=label_pos[0], y=label_pos[1], title=title
                )
                Animation(percent=value * 100 / 360).start(number_anim)

            angle_start += value

    def _clear_canvas(self):
        with contextlib.suppress(BaseException):
            self.canvas.before.clear()
            self.canvas.after.clear()

    def on_pos(self, *_):
        self._clear_canvas()
        Clock.schedule_once(lambda x: self._make_chart(self.items))

    def on_items(self, *_):
        self._clear_canvas()
        Clock.schedule_once(lambda x: self._make_chart(self.items))


class ChartLabel(MDLabel):
    _owner = ObjectProperty()
    _mypos = ListProperty([0, 0])


class ChartBase(DrawTools, ThemableBehavior, RelativeLayout):
    x_values = ListProperty([])
    x_labels = ListProperty([])
    y_values = ListProperty([])
    y_labels = ListProperty([])
    bg_color = ColorProperty(None, allownone=True)
    radius = ListProperty(None, alllownone=True)
    anim = BooleanProperty(True)
    d = NumericProperty(1)
    t = StringProperty("out_quad")
    labels = BooleanProperty(True)
    labels_color = ColorProperty([1, 1, 1, 1])
    label_size = NumericProperty("15dp")
    bars_color = ColorProperty([1, 1, 1, 1])
    line_width = NumericProperty("2dp")
    lines_color = ColorProperty([1, 1, 1, 1])
    lines = BooleanProperty(True)
    trim = BooleanProperty(True)
    _loaded = NumericProperty(1)
    _labels_y_box = ObjectProperty()
    _labels_x_box = ObjectProperty()
    _canvas = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self._myinit = True
        self.bind(
            _loaded=lambda *args: self._update(anim=True),
        )
        Clock.schedule_once(self.update)

    def _get_normalized_cor(self, val, mode, f_update=1):
        x_values = self.x_values
        y_values = self.y_values
        trim = self.trim
        padding = self.padding
        size = self.size
        min_x = min(x_values) if trim else 0
        max_x = max(x_values)
        min_y = min(y_values) if trim else 0
        max_y = max(y_values)
        x_distance = (max_x - min_x) if trim else max_x
        y_distance = (max_y - min_y) if trim else max_y

        if mode == "x":
            _min = min_x
            _distance = x_distance
            _size = size[0]
            f_update = 1
        else:
            _min = min_y
            _distance = y_distance
            _size = size[1]

        res = ((val - _min) / _distance) * (
                _size - self._bottom_line_y() - padding
        )
        return f_update * res + self._bottom_line_y()

    def do_layout(self, *args, **kwargs):
        super().do_layout(*args, **kwargs)
        self._update()

    def update(self, *_):
        self._myinit = True
        if self.anim:
            self._loaded = 0
            anim = Animation(_loaded=1, t=self.t, d=self.d)
            anim.start(self)
        else:
            self._update()
            self._update()

    def _update(self, anim=False, *args):
        x_values = self.x_values
        y_values = self.y_values
        x_labels = self.x_labels
        y_labels = self.y_labels
        canvas = self._canvas.canvas
        canvas.clear()
        canvas.after.clear()
        if self._myinit:
            self._labels_y_box.clear_widgets()
            self._labels_x_box.clear_widgets()

        dis = self._bottom_line_y()
        draw_shape(
            "line",
            shape_name="line",
            canvas=canvas,
            points=[
                [dis, dis],
                [self.width - dis, dis],
            ],
            line_width=self.line_width,
            color=self.lines_color,
        )

        if not x_values or not y_values:
            raise ValueError("x_values and y_values cannot be empty")

        if len(x_values) != len(y_values):
            raise ValueError("x_values and y_values must have equal length")

        if (
                ((len(x_labels) != len(y_values)) and len(x_labels) > 0)
                or (len(y_labels) != len(y_values))
                and len(y_labels) > 0
        ):
            raise ValueError(
                "x_values and y_values and x_labels must have equal length"
            )

    def _bottom_line_y(self):
        return self.label_size * 2

    def draw_label(self, text_x, text_y, center_pos_x, center_pos_y, idx):
        labels_y_box = self._labels_y_box
        labels_x_box = self._labels_x_box
        if self._myinit:
            label_y = ChartLabel(
                text=text_y,
                center=center_pos_y,
                _owner=self,
                height=self.label_size * 2,
            )
            label_y.font_size = self.label_size
            label_x = ChartLabel(
                text=text_x,
                center=center_pos_x,
                _owner=self,
                adaptive_height=True,
                padding=(0, "5dp"),
            )
            label_x.font_size = self.label_size
            labels_y_box.add_widget(label_y)
            labels_x_box.add_widget(label_x)
        else:
            self.reposition(labels_y_box, idx, center_pos_y)
            self.reposition(labels_x_box, idx, center_pos_x)

    @staticmethod
    def reposition(arg0, idx, arg2):
        child = arg0.children[idx]
        child.center_x = arg2[0]
        child.y = arg2[1]


class LineChart(ChartBase):
    circles_color = ColorProperty([1, 1, 1, 1])
    circles_radius = NumericProperty("5dp")
    circles = BooleanProperty(True)

    def _update(self, anim=False, *args):
        super()._update()
        x_values = self.x_values
        y_values = self.y_values
        canvas = self._canvas.canvas
        f_update = self._loaded if anim else 1
        drawer = draw_shape
        last_point = False
        x_y = []
        for i in range(len(x_values)):
            x = x_values[i]
            x_label = self.x_labels[i] if self.x_labels else False
            y_label = self.y_labels[i] if self.y_labels else False
            y = y_values[i]
            new_x = self._get_normalized_cor(x, "x", f_update)
            new_y = self._get_normalized_cor(y, "y", f_update)
            x_y += [new_x, new_y]
            if self.circles:
                drawer(
                    "circle",
                    shape_name="circle",
                    canvas=canvas.after,
                    color=self.circles_color,
                    size=[self.circles_radius, self.circles_radius],
                    center_pos=[new_x, new_y],
                )
            # if last_point and self.lines:
            #     drawer(
            #         "line",
            #         shape_name="line",
            #         canvas=canvas,
            #         points=last_point + [new_x, new_y],
            #         line_width=self.line_width,
            #         color=self.lines_color,
            #     )
            last_point = [new_x, new_y]

            if self.labels:
                y_pos = [
                    new_x,
                    new_y + self.circles_radius / 2,
                ]
                x_pos = [new_x, 0]
                self.draw_label(
                    text_x=x_label or str(x),
                    text_y=y_label or str(y),
                    center_pos_x=x_pos,
                    center_pos_y=y_pos,
                    idx=len(x_values) - i - 1,
                )
        drawer(
            "line",
            shape_name="line",
            canvas=canvas,
            points=x_y,
            line_width=self.line_width,
            color=self.lines_color,
        )
        self._myinit = False


class BarChart(ChartBase):
    max_bar_width = NumericProperty("80dp")
    min_bar_width = NumericProperty("10dp")
    bars_spacing = NumericProperty("10dp")
    bars_radius = NumericProperty("5dp")
    bars_color = ColorProperty([1, 1, 1, 1])

    def _update(self, anim=False, *args):
        super()._update()
        x_values = self.x_values
        y_values = self.y_values
        canvas = self._canvas.canvas
        drawer = draw_shape
        # bottom line
        bottom_line_y = self._bottom_line_y()
        count = len(self.y_values)
        bars_x_list = self.get_bar_x(count)
        bar_width = self.get_bar_width()
        f_update = self._loaded if anim else 1
        for i in range(count):
            x_label = self.x_labels[i] if self.x_labels else False
            y_label = self.y_labels[i] if self.y_labels else False
            y = y_values[i]
            new_x = bars_x_list[i]
            new_y = self._get_normalized_cor(y, "y", f_update)
            drawer(
                "bars",
                shape_name="roundedRectangle",
                canvas=canvas.after,
                color=self.bars_color,
                radius=[self.bars_radius, self.bars_radius, 0, 0],
                size=[bar_width, new_y - bottom_line_y],
                pos=[new_x, bottom_line_y],
            )

            if self.labels:
                y_pos = [new_x + bar_width / 2, new_y]
                x_pos = [new_x + bar_width / 2, 0]
                x = x_values[i]
                self.draw_label(
                    text_x=x_label or str(x),
                    text_y=y_label or str(y),
                    center_pos_x=x_pos,
                    center_pos_y=y_pos,
                    idx=len(x_values) - i - 1,
                )
        self._myinit = False

    def get_bar_x(self, bar_count):
        bar_width = self.get_bar_width()
        total_width = (
                bar_width * bar_count
                + (bar_count - 1) * self.bars_spacing
                + self.label_size * 4
        )
        start_pos = (self.width - total_width) / 2
        x_list = []
        for x in range(bar_count):
            x_pos = (
                    start_pos
                    + (bar_width + self.bars_spacing) * x
                    + self.label_size * 2
            )
            x_list.append(x_pos)
        return x_list

    def get_bar_width(self):
        bars_count = len(self.x_values)
        spacing = self.bars_spacing
        width = self.width
        bar_width = (
                            width - (bars_count + 1) * spacing - self.label_size * 4
                    ) / bars_count
        if bar_width > self.max_bar_width:
            return self.max_bar_width
        elif bar_width < self.min_bar_width:
            return self.min_bar_width
        else:
            return bar_width
