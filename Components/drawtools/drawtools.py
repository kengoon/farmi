from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.graphics import Color, Line, RoundedRectangle, Bezier
from kivy.properties import ObjectProperty

__all__ = ("DrawTools", "draw_shape")


class DrawTools(EventDispatcher):
    target_canvas = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        Clock.schedule_once(self._update)
        self.register_event_type("on_select")

    def _update(self, *args):
        if not self.target_canvas:
            self.target_canvas = self.canvas

    def on_select(self, *args):
        pass

    def on_touch_down(self, touch):
        pos = touch.pos
        if not self.collide_point(*pos):
            return False
        pos = self.to_local(*pos, relative=True)
        i = self.check_collision(pos)
        if i != -1:
            self.dispatch("on_select", i, *touch.pos)
        return True

    def on_touch_move(self, touch):
        pos = touch.pos
        if not self.collide_point(*pos):
            return False
        pos = self.to_local(*pos, relative=True)
        if i := self.check_collision(pos):
            self.dispatch("on_select", i, *touch.pos)
        return True

    def check_collision(self, touch_pos: list):
        children = self.target_canvas.children
        i = 0
        for child in children:
            # touchable instructions must be a subclass of RoundedRectangle
            if not issubclass(child.__class__, RoundedRectangle):
                continue
            pos = child.pos
            size = child.size
            x, y = pos
            w, h = size

            if (x <= touch_pos[0] <= x + w) and (y <= touch_pos[1] <= y + h):
                return i
            i += 1
        return -1


class InvalidShapeException(Exception):
    pass


def draw_shape(
        group,
        canvas,
        shape_name="rectangle",
        radius=None,
        pos=None,
        texture=None,
        center_pos=None,
        color=None,
        size=None,
        points=None,
        line_width=2,
):
    """
    shapes: rectangle, roundedRectangle, circle
    """

    if size is None:
        size = [10, 10]
    if color is None:
        color = [0, 0, 0, 1]
    canvas.add(Color(group=group, rgba=color))

    if shape_name != "line":
        shape = RoundedRectangle(
            group=group,
            size=size,
            pos=[
                center_pos[0] - size[0] / 2,
                center_pos[1] - size[1] / 2,
            ]
            if center_pos
            else pos,
        )
    if shape_name == "line":
        shape = Line(
            points=points,
            cap="none",
            joint="round",
            width=line_width
        )
    elif shape_name == "rectangle":
        shape.radius = [
            0,
        ]
    elif shape_name == "roundedRectangle":
        shape.radius = radius
    elif shape_name == "circle":
        shape.radius = [
            size[1] / 2,
        ]
    else:
        raise InvalidShapeException(f"Invalid shape name {shape}")

    if texture:
        shape.texture = texture

    canvas.add(shape)
    return True
