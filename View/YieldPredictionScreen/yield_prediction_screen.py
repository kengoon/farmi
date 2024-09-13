import contextlib
import re
from os.path import join
from pickle import loads
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
from kivy.metrics import dp, sp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd import fonts_path
from View.base_screen import BaseScreenView
from libs.decorator import android_only
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarSupportingText


class YieldPredictionScreenView(BaseScreenView):
    input_prediction = [
        (
            "Crop type",
            "The specific type of crop being planted (e.g., maize, rice, cassava). "
            "Different crops have unique growth requirements and yield patterns, so this "
            "is fundamental to making accurate predictions."
        ),

        (
            "Planting date",
            "The date when the crops were planted. "
            "This helps in assessing the growth stage of the crop and "
            "aligning it with historical data to predict yield."
        ),

        (
            "Soil type",
            "Information about the soil type (e.g., loamy, sandy, clay). "
            "Soil characteristics greatly affect crop growth and yield, so "
            "this input helps refine the prediction."
        ),

        (
            "Soil pH",
            "Specific soil conditions (e.g., pH level, a number between 0 - 14). "
            "Soil characteristics greatly affect crop growth and yield, so "
            "this input helps refine the prediction."
        ),

        (
            "Irrigation Method",
            "How the crops are watered (e.g., rain-fed, drip irrigation, sprinkler). "
            "Water availability and irrigation method influence crop growth, so this "
            "helps in predicting yield under varying water conditions."
        ),

        (
            "Fertilizer Usage",
            "Types and amounts of fertilizers applied, along with the application schedule. "
            "Fertilizer usage impacts plant nutrition and yield, so it's "
            "crucial for accurate predictions."
        ),

        (
            "Pest and Disease Management",
            "Information on any pests or diseases that have affected the crops and how they were managed. "
            "Crop health is a key determinant of yield, so this helps in adjusting the prediction based "
            "on any damage or stress the plants have experienced."
        ),

        (
            "Farm size",
            "The amount of plots of farm land being planted. "
            "While this doesn't directly influence the yield per unit area, "
            "it's necessary to estimate total production."
        ),

        (
            "State",
            "The state in Nigeria your farm land located. "
            "Different parts of our country have different weather and soil conditions."
        )
    ]
    item_index = None
    prev_item_index = 0

    def __init__(self, app, **kw):
        super().__init__(app, **kw)
        self.set_radius = False
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

    def on_enter(self):
        if self.item_index is not None:
            return
        if not self.set_radius:
            self.ids.text_field.radius = self.ids.text_field.height / 2
            self.set_radius = True
        self.item_index = 0
        self.farmi_chat()

    def farmi_chat(self):
        if self.item_index >= len(self.input_prediction):
            self.start_prediction()
            return
        question = self.input_prediction[self.item_index][0] + "?"
        description = self.input_prediction[self.item_index][1]
        self.ids.sv_list.add_widget(
            MDCard(
                MDLabel(
                    adaptive_height=True,
                    text=f"[b]{question}[/b]\n\n{description}",
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
        )
        self.scroll_bottom()

    def user_chat(self, text):
        if not text:
            return
        text = text.strip()
        question = self.input_prediction[self.item_index][0]
        self.put_extra(question, self.ids.text_field.text)
        card = MDCard(
            MDLabel(
                adaptive_height=True,
                adaptive_width=True,
                text=text,
                theme_line_height="Custom",
                line_height=1
            ),
            radius=["16dp", "5dp", "16dp", "16dp"],
            padding="15dp",
            adaptive_height=True,
            adaptive_width=True,
            theme_bg_color="Custom",
            pos_hint={"right": 1},
            md_bg_color=self.theme_cls.surfaceContainerHighColor
        )

        def control_card_width(_, width):
            if width > self.width - dp(40) - dp(50):
                card.width = self.width - dp(40) - dp(50)
                card.children[0].adaptive_width = False
                card.children[0].text_size = self.width - dp(40) - dp(50) - dp(30), None

        card.bind(width=control_card_width)
        self.ids.sv_list.add_widget(card)
        self.scroll_bottom()

        if self.item_index == len(self.input_prediction):
            self.start_prediction()
            return 

        Clock.schedule_once(lambda _: self.farmi_chat(), 1)
        self.item_index += 1

    def scroll_bottom(self):
        sv = self.ids.sv
        sv_list = self.ids.sv_list
        if sv.height < sv_list.height:
            Animation.cancel_all(sv, 'scroll_y')
            Animation(scroll_y=0, t='out_quad', d=.5).start(sv)

    def set_input(self, check=True):
        if self.item_index < 0:
            self.item_index = 0
            return
        if self.item_index >= len(self.input_prediction):
            self.item_index = len(self.input_prediction) - 1
            return
        if not self.ids.text_field.text and self.prev_item_index == self.item_index and check:
            self.ids.text_field.focus = True
            return self.toast(f"Fill {self.input_prediction[self.item_index][0]}")
        if check:
            self.put_extra(self.ids.text_field.hint_text, self.ids.text_field.text)
        with contextlib.suppress(IndexError):
            if self.item_index == 0:
                self.ids.prev_btn.disabled = True
            elif self.item_index == len(self.input_prediction) - 1:
                self.ids.prev_btn.disabled = False
                self.ids.next_btn_text.text = "Predict"
                self.ids.next_btn.theme_bg_color = "Custom"
                self.ids.next_btn.md_bg_color = self.theme_cls.primaryColor
                self.ids.next_btn_text.theme_text_color = "Custom"
                self.ids.next_btn_text.text_color = "white"
            else:
                self.ids.prev_btn.disabled = False
                self.ids.next_btn_text.text = "Next"
                self.ids.next_btn.theme_bg_color = "Primary"
                self.ids.next_btn_text.theme_text_color = "Primary"

            item = self.input_prediction[self.item_index]
            self.ids.text_field.hint_text = item[0]
            self.ids.description.text = item[1]

            text = self.get_extra(item[0], "")
            self.ids.text_field.text = text
            self.prev_item_index = self.item_index

    @android_only
    def start_prediction(self):
        self.open_dialog()
        from sjgeminifvai.jclass.contentbuilder import ContentBuilder
        from simplejnius.guava.jclass.futures import Futures
        from simplejnius.guava.jinterface.futurecallback import FutureCallback
        from jnius import autoclass

        text = ""
        for question, _ in self.input_prediction:
            text += f"{question}: {self.get_extra(question)}\n"
        text = text.strip()

        # Provide a prompt that contains text
        content = ContentBuilder()
        content.setRole("user")
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
        text = result.getText()
        text = text.strip()
        text = re.sub(r'\*\*(.*?)\*\*', r'[b]\1[/b]', text)
        text = re.sub(r'(?<!\*)\*(?!\*)(.*?)\*(?<!\*)', r'[i]\1[/i]', text)
        dot_font = join(fonts_path, "materialdesignicons-webfont.ttf")
        dot = f"[color=406836ff][font={dot_font}][size={int(sp(20))}]\U000F09DE[/size][/font][/color]"
        text = text.replace("* ", f"{dot} ")
        self.put_extra("analytical_type", "crop_prediction")
        self.put_extra("prediction", text)
        self.switch_screen("chart screen")
        self.ids.sv_list.clear_widgets()
        self.item_index = None

    @mainthread
    def get_gemini_error(self, error):
        print(error.getLocalizedMessage())
        text = f"Something unexpected happened"
        MDSnackbar(
            MDSnackbarSupportingText(
                text=text,
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
        ).open()
        self.dismiss_dialog()
