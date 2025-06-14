import re
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

'''
Custom Kivy Screen Classes
'''

class HomeScreen(Screen):
    pass

class EnterMatrixScreen(Screen):
    zero_one_text_inputs = {}

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

class ZeroOneTextInput(TextInput):
    pat = re.compile('[^01]')

    def insert_text(self, substring, from_undo=False):
        # Filter out anything that's not 0 or 1
        s = re.sub(self.pat, '', substring)

        # Only insert if field is empty and s is not empty
        if not self.text and s:
            return super().insert_text(s[0], from_undo=from_undo)
        return

class MatrixSizeTextInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        # Preview what the new text would be
        new_text = self.text[:self.cursor_index()] + substring + self.text[self.cursor_index():]

        # Allow only digits
        if not new_text.isdigit():
            return

        # Allow only numbers from 1 to 20
        if not (1 <= int(new_text) <= 20):
            return

        return super().insert_text(substring, from_undo=from_undo)

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

    def build_matrix_entry_box(self):
        matrix_entry_box = self.root.get_screen('EnterMatrixScreen').ids.matrix_entry_box
        matrix_size = int(self.root.get_screen('HomeScreen').ids.matrix_size_text_input.text)
        matrix_entry_box.clear_widgets()
        self.root.get_screen('EnterMatrixScreen').zero_one_text_inputs.clear()
        for i in range(matrix_size):
            row_box = BoxLayout(orientation='horizontal')
            matrix_entry_box.add_widget(row_box)
            for j in range(matrix_size):
                zero_one_text_input = ZeroOneTextInput(hint_text='0/1', font_size='10sp', write_tab=False,  multiline=False)
                self.root.get_screen('EnterMatrixScreen').zero_one_text_inputs[f'{i},{j}'] = zero_one_text_input
                row_box.add_widget(zero_one_text_input)

if __name__ == '__main__':
    app = zero_one_matrices_tool()
    app.run()