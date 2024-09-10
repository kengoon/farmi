# The screen's dictionary contains the objects of the models and controllers
# of the screens of the application.

from Model.onboard_screen import OnboardScreenModel
from Controller.onboard_screen import OnboardScreenController
from View.OnboardScreen.onboard_screen import OnboardScreenView
from Model.home_screen import HomeScreenModel
from Controller.home_screen import HomeScreenController
from View.HomeScreen.home_screen import HomeScreenView
from Model.yield_prediction_screen import YieldPredictionScreenModel
from Controller.yield_prediction_screen import YieldPredictionScreenController
from View.YieldPredictionScreen.yield_prediction_screen import YieldPredictionScreenView
from Model.crop_analysis_screen import CropAnalysisScreenModel
from Controller.crop_analysis_screen import CropAnalysisScreenController
from View.CropAnalysisScreen.crop_analysis_screen import CropAnalysisScreenView
from Model.inventory_screen import InventoryScreenModel
from Controller.inventory_screen import InventoryScreenController
from View.InventoryScreen.inventory_screen import InventoryScreenView
from Model.chat_screen import ChatScreenModel
from Controller.chat_screen import ChatScreenController
from View.ChatScreen.chat_screen import ChatScreenView
from Model.chart_screen import ChartScreenModel
from Controller.chart_screen import ChartScreenController
from View.ChartScreen.chart_screen import ChartScreenView

screens = {
    'crop analysis screen': {
        'model': CropAnalysisScreenModel,
        'controller': CropAnalysisScreenController,
        'view': CropAnalysisScreenView,
        'kv': "./View/CropAnalysisScreen/crop_analysis_screen.kv"
    },

    'inventory screen': {
        'model': InventoryScreenModel,
        'controller': InventoryScreenController,
        'view': InventoryScreenView,
        'kv': "./View/InventoryScreen/inventory_screen.kv"
    },

    'yield prediction screen': {
        'model': YieldPredictionScreenModel,
        'controller': YieldPredictionScreenController,
        'view': YieldPredictionScreenView,
        'kv': "./View/YieldPredictionScreen/yield_prediction_screen.kv"
    },

    'chart screen': {
        'model': ChartScreenModel,
        'controller': ChartScreenController,
        'view': ChartScreenView,
        'kv': "./View/ChartScreen/chart_screen.kv"
    },

    'onboard screen': {
        'model': OnboardScreenModel,
        'controller': OnboardScreenController,
        'view': OnboardScreenView,
        'kv': "./View/OnboardScreen/onboard_screen.kv"
    },

    'home screen': {
        'model': HomeScreenModel,
        'controller': HomeScreenController,
        'view': HomeScreenView,
        'kv': "./View/HomeScreen/home_screen.kv"
    },

    'chat screen': {
        'model': ChatScreenModel,
        'controller': ChatScreenController,
        'view': ChatScreenView,
        'kv': "./View/ChatScreen/chat_screen.kv"
    },

}
