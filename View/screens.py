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

screens = {
    'yield prediction screen': {
        'model': YieldPredictionScreenModel,
        'controller': YieldPredictionScreenController,
        'view': YieldPredictionScreenView,
        'kv': "./View/YieldPredictionScreen/yield_prediction_screen.kv"
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

}
