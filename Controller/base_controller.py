class BaseScreenController:
    def __init__(self, app, model):
        self.app = app
        self.model = model
        self.view = None
        
    def set_view(self, view):
        self.view = view
        
    def get_view(self):
        return self.view
