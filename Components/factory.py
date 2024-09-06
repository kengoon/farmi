from kivy.factory import Factory

register = Factory.register


def register_factory():
    register("CoverImage", module="Components.frame")
    register("RealRecycleView", module="Components.scrollview")
    register("TextField", module="Components.textfield")
    register("TagTextField", module="Components.textfield")
    register("Dot", module="Components.dot")
    register("DotSpinner", module="Components.spinner")
