import math
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
    entered_matrix = {}

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
    matrices_stack = []

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
        self.root.get_screen('EnterMatrixScreen').entered_matrix.clear()
        for i in range(matrix_size):
            row_box = BoxLayout(orientation='horizontal')
            matrix_entry_box.add_widget(row_box)
            for j in range(matrix_size):
                zero_one_text_input = ZeroOneTextInput(hint_text='0/1', font_size='10sp', write_tab=False,  multiline=False)
                self.root.get_screen('EnterMatrixScreen').entered_matrix[f'{i},{j}'] = zero_one_text_input
                row_box.add_widget(zero_one_text_input)

    def stack_entered_matrix(self):
        self.matrices_stack.clear()
        matrix_size = int(self.root.get_screen('HomeScreen').ids.matrix_size_text_input.text)
        matrix = {}
        for i in range(matrix_size):
            for j in range(matrix_size):
                entry_value = self.root.get_screen('EnterMatrixScreen').entered_matrix[f'{i},{j}'].text
                if entry_value == '':
                    entry_value = '0'
                matrix[f'{i},{j}'] = entry_value
        self.matrices_stack.append(matrix)
        self.update_displayed_matrix()

    def update_displayed_matrix(self):
        matrix_display_box = self.root.get_screen('MatrixEditorScreen').ids.matrix_editor_display_box
        matrix_display_box.clear_widgets()
        displayed_matrix = self.matrices_stack[-1]
        matrix_size = int(math.sqrt(len(displayed_matrix)))
        for i in range(matrix_size):
            row_box = BoxLayout(orientation='horizontal')
            matrix_display_box.add_widget(row_box)
            for j in range(matrix_size):
                matrix_display_label = SelfFormattingText(text=displayed_matrix[f'{i},{j}'])
                row_box.add_widget(matrix_display_label)

    def undo_operation(self):
        if len(self.matrices_stack) > 1:
            self.matrices_stack.pop(-1)
            self.update_displayed_matrix()

    def make_irreflexive(self):
        current_matrix = self.matrices_stack[-1]
        matrix_size = int(math.sqrt(len(current_matrix)))
        updated_matrix = {}
        for i in range(matrix_size):
            for j in range(matrix_size):
                if i == j:
                    updated_matrix[f'{i},{j}'] = '0'
                else:
                    updated_matrix[f'{i},{j}'] = current_matrix[f'{i},{j}']
        self.matrices_stack.append(updated_matrix)
        self.update_displayed_matrix()

    def make_reflexive(self):
        current_matrix = self.matrices_stack[-1]
        matrix_size = int(math.sqrt(len(current_matrix)))
        updated_matrix = {}
        for i in range(matrix_size):
            for j in range(matrix_size):
                if i == j:
                    updated_matrix[f'{i},{j}'] = '1'
                else:
                    updated_matrix[f'{i},{j}'] = current_matrix[f'{i},{j}']
        self.matrices_stack.append(updated_matrix)
        self.update_displayed_matrix()

if __name__ == '__main__':
    app = zero_one_matrices_tool()
    app.run()