from kivy.app import App
from kivy.properties import NumericProperty
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

'''
Custom Kivy Screen Classes
'''

class HomeScreen(Screen):
    pass

class EnterMatrixScreen(Screen):
    matrix_size = NumericProperty(0)

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

class zero_one_matrices_tool(App):
    def build(self):
        screen_manager = ScreenManager(transition=NoTransition())
        screen_manager.add_widget(HomeScreen(name='HomeScreen'))
        screen_manager.add_widget(EnterMatrixScreen(name='EnterMatrixScreen'))
        screen_manager.add_widget(LoadMatrixScreen(name='LoadMatrixScreen'))
        screen_manager.add_widget(MatrixEditorScreen(name='MatrixEditorScreen'))
        return screen_manager

if __name__ == '__main__':
    app = zero_one_matrices_tool()
    app.run()