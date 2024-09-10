from os.path import splitext
import pickle, json
from time import time
from kivy.clock import mainthread
from View.base_screen import BaseScreenView
from libs.decorator import android_only
from libs.tools import get_bitmap
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarSupportingText
from kivy.metrics import dp
from kivy.clock import triggered


class CropAnalysisScreenView(BaseScreenView):
    def __init__(self, app, **kw):
        super().__init__(app, **kw)
        self.bitmap = None
        self.future_callback = None
        self.response = None
        self.prompt = None
        self.chat = None
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
        with open("system_instructions/analysis_instruction.prompt", "rb") as model:
            system_instruction = ContentBuilder().addText(
                pickle.loads(model.read())
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

    def open_photo_picker(self):
        from kvdroid.tools.photo_picker import action_pick_image
        action_pick_image(lambda path: self.add_image(path, get_bitmap(path)))

    def take_picture(self):
        from plyer import camera
        camera.take_picture(
            filename=f"images/img{str(time()).replace('.', '')}.png",
            on_complete=self.add_image
        )

    def add_image(self, filename, bitmap):
        img_ext = ["png", "jpg", "jpeg", "PNG", "JPG", "JPEG", "gif", "GIF"]
        ext = splitext(filename)[1].split(".")[1]
        if ext not in img_ext:
            return self.toast("Only images allowed")
        
        self.ids.cover_image.source = filename
        self.bitmap = bitmap

    @triggered(.5)
    def start_analysis(self, soil_ph):
        if not self.bitmap:
            return self.toast("Please add an image")
        self.open_dialog()
        from sjgeminifvai.jclass.contentbuilder import ContentBuilder
        from simplejnius.guava.jclass.futures import Futures
        from simplejnius.guava.jinterface.futurecallback import FutureCallback
        from kvdroid import activity  # noqa
        from jnius import autoclass

        # Provide a prompt that contains text
        content = ContentBuilder()
        content.setRole("user")
        content.addImage(self.bitmap)
        text = "Analyse"
        if soil_ph:
            text += f" with soil pH: {soil_ph}"
        content.addText(text)

        # To generate text output, call generateContent with the text input
        self.response = self.chat.sendMessage(content.build())

        self.future_callback = FutureCallback(
            dict(
                on_success=self.get_gemini_reply,
                on_failure=lambda _: self.get_gemini_error("Something went wrong. Try again"),
            )
        )
        executor = autoclass("java.util.concurrent.Executors").newSingleThreadExecutor()
        Futures.addCallback(self.response, self.future_callback, executor)

    @mainthread
    def get_gemini_reply(self, result):
        text = result.getText()
        try:
            data = json.loads(text)
            data["image"] = self.ids.cover_image.source
            self.put_extra("analysis", data)
            self.put_extra("analytical_type", "crop_analysis")
            self.switch_screen("chart screen")
        except json.JSONDecodeError:
            self.get_gemini_error(text.strip())

    @mainthread
    def get_gemini_error(self, error):
        MDSnackbar(
            MDSnackbarSupportingText(
                text=error,
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
        ).open()
        self.dismiss_dialog()
