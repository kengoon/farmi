import re

from kivy.animation import Animation
from kivy.clock import triggered, mainthread
from kivy.metrics import dp, sp
from kivy.properties import ObjectProperty
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from Components.frame import CoverImage
from Components.spinner import DotSpinner
from View.base_screen import BaseScreenView
from kivymd.uix.gridlayout import MDGridLayout
from libs.decorator import android_only
from kivymd.uix.relativelayout import MDRelativeLayout
from time import time
from kivymd.uix.behaviors import StencilBehavior
from libs.tools import get_bitmap
from os.path import splitext, join
from kivymd import fonts_path
from pickle import loads


class ChatScreenView(BaseScreenView):
    camera_icon = ObjectProperty()
    image_icon = ObjectProperty()
    plus_icon = ObjectProperty()
    chat_loader = ObjectProperty()
    _set_radius = False

    def __init__(self, app, **kw):
        super().__init__(app, **kw)
        self.future_callback = None
        self.response = None
        self.prompt = None
        self.chat = None
        self.bitmaps = []
        self.__android_init__()

    @android_only
    def __android_init__(self):
        from sjgeminifvai.jclass.fvai import FirebaseVertexAI
        from sjgeminifvai.jclass.gmf import GenerativeModelFutures
        from sjgeminifvai.jclass.optionals import RequestOptions
        from sjgeminifvai.jclass.contentbuilder import ContentBuilder

        # Initialize the Vertex AI service and the generative model
        # Specify a model that supports your use case
        # Gemini 1.5 models are versatile and can be used with all API capabilities
        vertex = FirebaseVertexAI.getInstance()
        with open("system_instructions/chat_instruction.prompt", "rb") as model:
            system_instruction = ContentBuilder().addText(
                loads(model.read())
            ).build()
        self.gm = vertex.generativeModel(
            "gemini-1.5-flash", None, None, RequestOptions(),
            None, None, system_instruction
        )

        # Use the GenerativeModelFutures Java compatibility layer which offers
        # support for ListenableFuture and Publisher APIs
        self.model = getattr(GenerativeModelFutures, "from")(self.gm)
        self.chat = self.model.startChat()

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """

    def on_enter(self, *args):
        if not self._set_radius:
            self.ids.text_field.radius = self.ids.text_field.height / 2
            self._set_radius = True

    def add_image_icons(self, box):
        if not self.camera_icon:
            self.camera_icon = MDIconButton(
                icon="camera-outline",
                on_release=lambda _: self.take_picture()
            )
        if not self.image_icon:
            self.image_icon = MDIconButton(
                icon="image-outline",
                on_release=lambda _: self.open_photo_picker()
            )
        box.clear_widgets()
        box.add_widget(self.camera_icon)
        box.add_widget(self.image_icon)

    def open_photo_picker(self):
        if len(self.bitmaps) >= 4:
            return self.toast("Max of 4 pictures only")

        from kvdroid.tools.photo_picker import action_pick_image
        action_pick_image(lambda path: self.add_image(path, get_bitmap(path)))

    def take_picture(self):
        if len(self.bitmaps) >= 4:
            return self.toast("Max of 4 pictures only")

        from plyer import camera
        camera.take_picture(
            filename=f"images/img{str(time()).replace('.', '')}.png",
            on_complete=self.add_image
        )

    def add_plus_icon(self, box):
        box.clear_widgets()
        box.add_widget(self.plus_icon)

    def _control_card_width(self, card, width):
        if width > self.width - dp(40) - dp(50):
            card.width = self.width - dp(40) - dp(50)
            card.children[0].adaptive_width = False
            card.children[0].text_size = self.width - dp(40) - dp(50) - dp(30), None

    def scroll_bottom(self):
        sv = self.ids.sv
        sv_list = self.ids.sv_list
        if sv.height < sv_list.height:
            Animation.cancel_all(sv, 'scroll_y')
            Animation(scroll_y=0, t='out_quad', d=.5).start(sv)

    @mainthread
    def add_image(self, filename, bitmap):
        img_ext = ["png", "jpg", "jpeg", "PNG", "JPG", "JPEG", "gif", "GIF"]
        ext = splitext(filename)[1].split(".")[1]
        if ext not in img_ext:
            return self.toast("Only images allowed")

        def remove_bitmap():
            self.bitmaps.remove(bitmap)
            self.ids.image_box.remove_widget(rel)
        icon = MDIconButton(
            icon="close",
            on_release=lambda _: remove_bitmap(),
            pos_hint={"top": 1, "right": 1},
            style="tonal",
            theme_font_size="Custom",
            font_size="15sp"
        )
        icon.size = ("20dp", "20dp")
        rel = MDRelativeLayout(
            CoverImage(
                source=filename,
                size_hint=(None, None),
                size=("72dp", "72dp"),
                radius="10dp",
                on_error=lambda _: remove_bitmap()
            ),
            icon,
            size_hint=(None, None),
            size=("72dp", "72dp"),
        )
        self.ids.image_box.add_widget(rel)
        self.bitmaps.append(bitmap)

    def user_chat(self, text):
        if not text:
            return
        text = text.strip()
        card = MDCard(
            MDLabel(
                adaptive_height=True,
                adaptive_width=not self.ids.image_box.children,
                text=text,
                theme_line_height="Custom",
                line_height=1
            ),
            spacing="15dp",
            radius=["16dp", "5dp", "16dp", "16dp"],
            padding="15dp",
            adaptive_height=True,
            adaptive_width=True,
            theme_bg_color="Custom",
            pos_hint={"right": 1},
            md_bg_color=self.theme_cls.surfaceContainerHighColor,
            orientation="vertical"
        )

        if self.ids.image_box.children:

            class CustomGridLayout(StencilBehavior, MDGridLayout):
                pass

            grid = CustomGridLayout(
                size_hint=(None, None),
                size=(self.width - dp(40) - dp(50) - dp(30), "150dp"),
                cols=2,
                spacing="3dp",
                radius="10dp"
            )
            for rel in self.ids.image_box.children:
                img = rel.children[-1]
                grid.add_widget(CoverImage(source=img.source))
            card.add_widget(grid)

        card.bind(width=self._control_card_width)
        self.ids.sv_list.add_widget(card)
        self.scroll_bottom()
        self.add_chat_loader(text)

    def farmi_chat(self, text):
        self.remove_chat_loader()
        text = text.strip()
        text = re.sub(r'\*\*(.*?)\*\*', r'[b]\1[/b]', text)
        dot_font = join(fonts_path, "materialdesignicons-webfont.ttf")
        dot = f"[color=406836ff][font={dot_font}][size={int(sp(20))}]\U000F09DE[/size][/font][/color]"
        text = text.replace("* ", f"{dot} ")
        card = MDCard(
            MDLabel(
                adaptive_height=True,
                text=text,
                markup=True,
                theme_line_height="Custom",
                line_height=1
            ),
            radius=["5dp", "16dp", "16dp", "16dp"],
            padding="15dp",
            adaptive_height=True,
            size_hint_x=None,
            width=self.width - dp(40) - dp(50),
            theme_bg_color="Custom",
            md_bg_color=self.theme_cls.surfaceContainerHighColor
        )

        card.bind(width=self._control_card_width)
        self.ids.sv_list.add_widget(card)
        self.scroll_bottom()

    @triggered(.2)
    def add_chat_loader(self, text):
        if not self.chat_loader:
            self.chat_loader = MDCard(
                DotSpinner(
                    dot_num=3,
                    speed=.2,
                    pos_hint={"center_y": .5}
                ),
                adaptive_width=True,
                size_hint_y=None,
                height="40dp",
                padding=["20dp", "10dp", "40dp", "10dp"],
                radius=["5dp", "16dp", "16dp", "16dp"]
            )

        self.ids.sv_list.add_widget(self.chat_loader)
        self.chat_loader.children[0].active = True
        self.scroll_bottom()
        self.ids.chat_box.disabled = True
        self.chat_gemini(text)

    def remove_chat_loader(self):
        self.chat_loader.children[0].active = False
        self.ids.sv_list.remove_widget(self.chat_loader)
        self.ids.chat_box.disabled = False

    @android_only
    def chat_gemini(self, text):
        from sjgeminifvai.jclass.contentbuilder import ContentBuilder
        from simplejnius.guava.jclass.futures import Futures
        from simplejnius.guava.jinterface.futurecallback import FutureCallback
        from jnius import autoclass

        # Provide a prompt that contains text
        content = ContentBuilder()
        content.setRole("user")
        for bitmap in self.bitmaps:
            content.addImage(bitmap)
        self.bitmaps = []
        self.ids.image_box.clear_widgets()
        content.addText(text)
        self.prompt = content.build()

        # To generate text output, call generateContent with the text input
        self.response = self.chat.sendMessage(self.prompt)

        self.future_callback = FutureCallback(
            dict(
                on_success=self.get_gemini_reply,
                on_failure=self.get_gemini_error
            )
        )
        executor = autoclass("java.util.concurrent.Executors").newSingleThreadExecutor()
        Futures.addCallback(self.response, self.future_callback, executor)

    @mainthread
    def get_gemini_reply(self, result):
        self.farmi_chat(result.getText())

    @mainthread
    def get_gemini_error(self, error):
        print(error.getLocalizedMessage())
        text = f"[color=ff0000]Something unexpected happened[/color]"
        self.farmi_chat(text)
