from kivy.app import App
from kivy.core.window import Window
from kivy.modules import inspector
from kivy.uix.screenmanager import ScreenManager


class ZeroOneMatricesTool(App):
    def build(self):
        inspector.create_inspector(Window, self)
        self.sm = ScreenManager()
        return self.sm

if __name__ == '__main__':
    app = ZeroOneMatricesTool()
    app.run()