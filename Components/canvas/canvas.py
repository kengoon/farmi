from os.path import join, basename, dirname

from kivy.clock import Clock
from kivy.graphics import Line, Color, PushMatrix, Rotate, PopMatrix, Rectangle
from kivy.lang import Builder
from kivy.properties import BooleanProperty, NumericProperty, ColorProperty, ListProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget

Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))

__all__ = ("GridCanvas", "MagnifyingGlassCanvas", "GridMagnifier", "HistogramCanvas")


class HistogramCanvas(RelativeLayout):
    color = ColorProperty("black")
    data = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda _: self.draw_histogram())
        self.bind(
            color=self.draw_histogram,
            data=self.draw_histogram,
            size=self.draw_histogram
        )

    def draw_histogram(self, *_):
        self.canvas.clear()
        num_bins = len(self.data)
        bin_width = self.width / num_bins
        max_value = max(self.data)

        with self.canvas:
            Color(*self.color)  # Gray color for the bars

            for i, value in enumerate(self.data):
                bar_height = (value / max_value) * self.height
                Rectangle(pos=(i * bin_width, 0), size=(bin_width, bar_height))

                # Draw vertical lines between bars
                Line(points=[(i + 1) * bin_width, 0, (i + 1) * bin_width, self.height])


class GridCanvas(Widget):
    close_grid = BooleanProperty(False)
    cols = NumericProperty(3)
    rows = NumericProperty(3)
    line_width = NumericProperty(1)
    color = ColorProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda *_: self.draw_grid())
        self.bind(
            width=self.draw_grid,
            height=self.draw_grid,
            cols=self.draw_grid,
            rows=self.draw_grid,
            close_grid=self.draw_grid,
            line_width=self.draw_grid,
            color=self.draw_grid
        )

    def draw_grid(self, *_):
        self.canvas.clear()
        cell_width = self.width / self.cols
        cell_height = self.height / self.rows

        with self.canvas:
            Color(*self.color)
            num = int(self.close_grid)  # convert close grid to 1 or 0
            self.cols += num
            for col in range(int(not num), self.cols):
                x = col * cell_width
                Line(points=[x, 0, x, self.height], width=self.line_width)

            self.rows += num
            for row in range(int(not num), self.rows):
                y = row * cell_height
                Line(points=[0, y, self.width, y], width=self.line_width)


class MagnifyingGlassCanvas(RelativeLayout):
    line_width = NumericProperty(10)
    pos_x = NumericProperty(0)
    pos_y = NumericProperty(0)
    radius = NumericProperty(50)
    angle = NumericProperty(45)
    color = ColorProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(lambda *_: self.draw_magnifying_glass())
        self.bind(
            pos_x=self.draw_magnifying_glass,
            pos_y=self.draw_magnifying_glass,
            line_width=self.draw_magnifying_glass,
            radius=self.draw_magnifying_glass,
            angle=self.draw_magnifying_glass
        )

    def draw_magnifying_glass(self, *_):
        with self.canvas:
            self.canvas.clear()
            Color(*self.color)

            # Tilt the magnifying glass by using PushMatrix and Rotate
            PushMatrix()
            Rotate(origin=(self.pos_x, self.pos_y), angle=self.angle)

            # Ellipse(pos=(center_x - radius, center_y - radius), size=(radius * 2, radius * 2))
            Line(circle=(self.pos_x, self.pos_y, self.radius), width=self.line_width)
            Line(
                points=[
                    self.pos_x, self.pos_y - self.radius * 1.5, self.pos_x, self.pos_y - self.radius * 2.8
                ], width=8
            )
            # Line(points=[center_x - radius * 2, center_y, center_x - radius * 4, center_y], width=4)

            PopMatrix()


class GridMagnifier(RelativeLayout):
    rows = NumericProperty(5)
    cols = NumericProperty(4)
    grid_color = ColorProperty("black")
    magnify_color = ColorProperty("black")
