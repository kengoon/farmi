import contextlib

from View.base_screen import BaseScreenView


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
        )
    ]
    item_index = 0
    prev_item_index = 0

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """

    def on_enter(self):
        self.set_input(False)

    def set_input(self, check=True):
        if self.item_index < 0:
            self.item_index = 0
            return
        if self.item_index >= len(self.input_prediction):
            self.item_index = len(self.input_prediction) - 1
            return
        if not self.ids.text_field.text and self.prev_item_index == self.item_index and check:
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


