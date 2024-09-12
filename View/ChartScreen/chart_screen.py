from View.base_screen import BaseScreenView
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.relativelayout import MDRelativeLayout
from Components.frame import CoverImage
from kivy.metrics import sp
from Components.charts import BarChart, PieChart
from kivy.metrics import dp
from kivymd.uix.divider import MDDivider


class ChartScreenView(BaseScreenView):

    def model_is_changed(self) -> None:
        """
        Called whenever any change has occurred in the data model.
        The view in this method tracks these changes and updates the UI
        according to these changes.
        """

    def on_enter(self, *args):
        match self.get_extra("analytical_type"):
            case "crop_analysis":
                self.crop_analysis()
            case "crop_prediction":
                self.crop_prediction()

    def crop_prediction(self):
        self.ids.sv_list.add_widget(
            MDLabel(
                text=self.get_extra("prediction"),
                adaptive_height=True,
                markup=True,
            )
        )

    def crop_analysis(self):
        data: dict = self.get_extra("analysis")

        plant_health_score = data.get("plant_health_score")
        self.ids.sv_list.add_widget(
            MDBoxLayout(
                MDBoxLayout(
                    MDLabel(
                        text="Plant Health",
                        adaptive_height=True,
                        theme_line_height="Custom",
                        line_height=1,
                        bold=True,
                    ),
                    MDCard(  # bar
                        MDRelativeLayout(
                            MDBoxLayout(  # bar color
                                size_hint_y=plant_health_score/100,
                                md_bg_color=self.theme_cls.primaryColor
                            ),
                            MDLabel(  # bar percentage
                                text=str(plant_health_score) + "%",
                                halign='center',
                                font_style='Title',
                            )
                        ),
                        pos_hint={"center_x": .5},
                        size_hint_x=None,
                        width="60dp"
                    ),
                    orientation="vertical",
                    spacing="10dp",
                    radius=0
                ),
                CoverImage(
                    source=data["image"],
                    size_hint_y=None,
                    height=(self.width - dp(40) - dp(20)) / 2,
                    radius=((self.width - dp(40) - dp(20)) / 2) / 2,
                    pos_hint={"center_y": .5},
                ),
                size_hint_y=None,
                height="250dp",
                md_bg_color=self.theme_cls.surfaceContainerColor,
                radius="16dp",
                padding="10dp"
            )
        )

        if detected_issues := data.get("detected_issues"):
            x_values = [0]
            y_values = [0]
            x_labels = [" "]
            y_labels = [" "]
            # with contextlib.suppress(TypeError):
            #     detected_issues = json.loads(detected_issues)
            for value in detected_issues:
                # with contextlib.suppress(TypeError):
                #     print(value, type(value))
                #     value = json.loads(value)
                x_values.append(x_values[-1] + 1)
                y_values.append(value["percentage_affected"])
                x_labels.append(value["issue_name"].replace("_", "\n"))
                y_labels.append(str(value["percentage_affected"]))

            x_values.append(x_values[-1] + 1)
            y_values.append(0)
            x_labels.append(" ")
            y_labels.append(" ")

            self.ids.sv_list.add_widget(
                MDCard(
                    MDLabel(
                        text="Detected Issues",
                        adaptive_height=True,
                        theme_line_height="Custom",
                        line_height=1,
                        bold=True,
                    ),
                    BarChart(
                        labels=True,
                        anim=True,
                        lines=True,
                        x_values=x_values,
                        y_values=y_values,
                        x_labels=x_labels,
                        y_labels=y_labels,
                        bg_color=self.theme_cls.transparentColor,
                        lines_color=self.theme_cls.primaryColor,
                        bars_color=self.theme_cls.primaryColor,
                        labels_color=self.theme_cls.primaryColor,
                        label_size=sp(12)
                    ),
                    orientation="vertical",
                    size_hint_y=None,
                    height="270dp",
                    padding=("10dp", "10dp"),
                )
            )

        severity_of_issues = data.get("severity_of_issues")
        growth_stage = data.get("growth_stage")
        self.ids.sv_list.add_widget(
            MDCard(
                MDBoxLayout(
                    MDLabel(
                        text="Issues Severity",
                        adaptive_height=True,
                        bold=True,
                        padding="10dp",
                        md_bg_color=self.theme_cls.primaryColor,
                        radius=["16dp", 0, 0, 0],
                        theme_text_color="Custom",
                        text_color="white"
                    ),
                    MDDivider(orientation="vertical"),
                    MDLabel(
                        text="Growth Stage",
                        adaptive_height=True,
                        bold=True,
                        padding="10dp",
                        md_bg_color=self.theme_cls.primaryColor,
                        radius=[0, "16dp", 0, 0],
                        theme_text_color="Custom",
                        text_color="white"
                    ),
                    adaptive_height=True,
                ),
                MDBoxLayout(
                    MDLabel(
                        text=severity_of_issues,
                        adaptive_height=True,
                        padding="20dp",
                        radius=[0, "16dp", 0, 0],
                    ),
                    MDDivider(orientation="vertical"),
                    MDLabel(
                        text=growth_stage,
                        adaptive_height=True,
                        padding="20dp",
                        radius=[0, "16dp", 0, 0],
                    ),
                    adaptive_height=True,
                ),
                adaptive_height=True,
                orientation="vertical",
                spacing="10dp"
            )
        )

        analysis_breakdown = data.get("analysis_breakdown")
        self.ids.sv_list.add_widget(
            MDCard(
                MDLabel(
                    text="Analysis Breakdown",
                    bold=True,
                    adaptive_height=True,
                    theme_line_height="Custom",
                    line_height=1,
                ),
                PieChart(
                    items=[
                        {
                            "Healthy Area": analysis_breakdown["healthy_area"],
                            "Affected Area": analysis_breakdown["affected_area"]
                        }
                    ],
                    pos_hint={"center_x": 0.5},
                    size_hint=[None, None],
                    size=("200dp", "200dp"),
                ),
                padding="10dp",
                spacing="10dp",
                size_hint_y=None,
                height="250dp",
                orientation="vertical"
            )
        )

        confidence_level = data.get("confidence_level")
        self.ids.sv_list.add_widget(
            MDCard(
                MDLabel(
                    text="AI Confidence Level",
                    adaptive_height=True,
                    bold=True,
                ),
                MDBoxLayout(
                    MDLabel(
                        text=str(confidence_level) + "%",
                        adaptive_height=True,
                        font_style='Headline',
                        theme_line_height="Custom",
                        line_height=1,
                    ),
                    MDIcon(
                        icon="signal",
                        theme_font_size="Custom",
                        font_size="32sp",
                        theme_icon_color="Custom",
                        icon_color=self.theme_cls.primaryColor,
                    ),
                    adaptive_height=True,
                ),
                padding="20dp",
                spacing="15dp",
                orientation="vertical",
                adaptive_height=True,
            )
        )

        actionable_suggestions = data.get("actionable_suggestions")
        card = MDCard(
            MDLabel(
                text="Actionable Suggestions",
                adaptive_height=True,
                bold=True,
            ),
            orientation="vertical",
            padding="20dp",
            spacing="15dp",
            adaptive_height=True

        )
        for value in actionable_suggestions:
            card.add_widget(
                MDBoxLayout(
                    MDIcon(
                        icon="circle-medium",
                        pos_hint={"top": .9},
                        theme_icon_color="Custom",
                        icon_color=self.theme_cls.primaryColor,
                    ),
                    MDBoxLayout(
                        MDLabel(
                            text=value["recommendation"],
                            adaptive_height=True,
                        ),
                        MDLabel(
                            text="[b]priority:[/b] " + value["priority"],
                            adaptive_height=True,
                            markup=True,
                        ),
                        orientation="vertical",
                        spacing="5dp",
                        adaptive_height=True
                    ),
                    spacing="10dp",
                    adaptive_height=True,
                )
            )
        self.ids.sv_list.add_widget(card)

        text_explanation = data.get("text_explanation")
        self.ids.sv_list.add_widget(
            MDCard(
                MDLabel(
                    text="Detailed Explanation",
                    adaptive_height=True,
                    bold=True,
                ),
                MDLabel(
                    text=text_explanation,
                    adaptive_height=True,
                ),
                padding="20dp",
                orientation="vertical",
                adaptive_height=True,
                spacing="10dp",
            )
        )

    def on_leave(self, *args):
        self.ids.sv_list.clear_widgets()
        self.ids.sv_list.scroll_y = 1
