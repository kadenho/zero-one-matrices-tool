from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

'''
Custom Kivy Screen Classes
'''

class HomeScreen(Screen):
    pass

class EnterMatrixScreen(Screen):
    pass

class LoadMatrixScreen(Screen):
    pass

class MatrixEditorScreen(Screen):
    pass


'''
Custom Kivy Widgets Classes
'''
class ScreenBoxLayout(BoxLayout):
    pass

class SelfFormattingText(Label):
    pass

'''
Define kivy app class
'''

class ZeroOneMatricesTool(App):
    def build(self):
        self.sm = ScreenManager(transition=NoTransition())
        self.sm.add_widget(HomeScreen(name='HomeScreen'))
        self.sm.add_widget(EnterMatrixScreen(name='EnterMatrixScreen'))
        self.sm.add_widget(LoadMatrixScreen(name='LoadMatrixScreen'))
        self.sm.add_widget(MatrixEditorScreen(name='MatrixEditorScreen'))
        return self.sm

if __name__ == '__main__':
    app = ZeroOneMatricesTool()
    app.run()