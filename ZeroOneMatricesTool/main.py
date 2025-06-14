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
        """

        Updates the stack to only have the entered matrix

        """
        self.matrices_stack.clear() # remove any matrices already in the stack
        matrix_size = int(self.root.get_screen('HomeScreen').ids.matrix_size_text_input.text) # retrieve matrix size
        matrix = {} # matrix to be stacked
        for i in range(matrix_size): # iterate through the rows
            for j in range(matrix_size): # iterate through the columns
                entry_value = self.root.get_screen('EnterMatrixScreen').entered_matrix[f'{i},{j}'].text # retrieve the entered value
                if entry_value == '': # if there was none
                    entry_value = '0' # set the entered value to 0
                matrix[f'{i},{j}'] = entry_value # designate the element key with the entered value
        self.matrices_stack.append(matrix) # append matrix to the stack
        self.update_displayed_matrix() # update the displayed matrix

    def update_displayed_matrix(self):
        """

        Updates the displayed matrix to the most recent

        """
        matrix_display_box = self.root.get_screen('MatrixEditorScreen').ids.matrix_editor_display_box # retrieve box where matrix is displayed
        matrix_display_box.clear_widgets() # clear the current display
        displayed_matrix = self.matrices_stack[-1] # retrieve matrix currently displayed
        matrix_size = int(math.sqrt(len(displayed_matrix))) # determine the size of the matrix
        for i in range(matrix_size): # iterate through the rows
            row_box = BoxLayout(orientation='horizontal') # create a box for the row
            matrix_display_box.add_widget(row_box) # add box to the display area
            for j in range(matrix_size): # iterate through the columns
                matrix_display_label = SelfFormattingText(text=displayed_matrix[f'{i},{j}']) # create a label with corresponding value
                row_box.add_widget(matrix_display_label) # add the label

    def undo_operation(self):
        if len(self.matrices_stack) > 1: # given there are at least two matrices in the stack
            self.matrices_stack.pop(-1) # remove matrix on the top of the stack
            self.update_displayed_matrix() # display new matrix

    def make_irreflexive(self):
        current_matrix = self.matrices_stack[-1] # retrieve matrix currently displayed
        matrix_size = int(math.sqrt(len(current_matrix))) # determine the size of the matrix
        updated_matrix = {} # new matrix to be built
        for i in range(matrix_size): # iterate through the rows
            for j in range(matrix_size): # iterate through the columns
                if i == j: # if it is on the diagonal
                    updated_matrix[f'{i},{j}'] = '0' # set the value to 0
                else:
                    updated_matrix[f'{i},{j}'] = current_matrix[f'{i},{j}'] # copy the old value
        self.matrices_stack.append(updated_matrix) # add matrix to the stack
        self.update_displayed_matrix() # display new matrix

    def make_anti_symmetric(self):
        current_matrix = self.matrices_stack[-1]  # retrieve matrix currently displayed
        matrix_size = int(math.sqrt(len(current_matrix)))  # determine the size of the matrix
        updated_matrix = {}  # new matrix to be built
        for i in range(matrix_size): # iterate through the rows
            for j in range(i, matrix_size): # iterate through the columns
                if i != j: # if it is not on the diagonal
                    updated_matrix[f'{i},{j}'] = current_matrix[f'{i},{j}'] # copy the old value
                    if current_matrix[f'{i},{j}'] == '0': # make the corresponding element the opposite
                        updated_matrix[f'{j},{i}'] = '1'
                    elif current_matrix[f'{i},{j}'] == '1': # make the corresponding element the opposite
                        updated_matrix[f'{j},{i}'] = '0'
                else:
                    updated_matrix[f'{i},{j}'] = current_matrix[f'{i},{j}'] # copy the old value for elements on the diagonal
        self.matrices_stack.append(updated_matrix)  # add matrix to te stack
        self.update_displayed_matrix()  # display new matrix

    def make_asymmetric(self):
        current_matrix = self.matrices_stack[-1]  # retrieve matrix currently displayed
        matrix_size = int(math.sqrt(len(current_matrix)))  # determine the size of the matrix
        updated_matrix = {}  # new matrix to be built
        for i in range(matrix_size): # iterate through the rows
            for j in range(i, matrix_size): # iterate through the columns
                if i != j: # if it is not on the diagonal
                    updated_matrix[f'{i},{j}'] = current_matrix[f'{i},{j}'] # copy the old value
                    if current_matrix[f'{i},{j}'] == '0': # make the corresponding element the opposite
                        updated_matrix[f'{j},{i}'] = '1'
                    elif current_matrix[f'{i},{j}'] == '1': # make the corresponding element the opposite
                        updated_matrix[f'{j},{i}'] = '0'
                else:
                    updated_matrix[f'{i},{j}'] = '0' # set value to 0 for elements on the diagonal
        self.matrices_stack.append(updated_matrix)  # add matrix to te stack
        self.update_displayed_matrix()  # display new matrix


    def make_reflexive(self):
        current_matrix = self.matrices_stack[-1]  # retrieve matrix currently displayed
        matrix_size = int(math.sqrt(len(current_matrix)))  # determine the size of the matrix
        updated_matrix = {}  # new matrix to be built
        for i in range(matrix_size): # iterate through the rows
            for j in range(matrix_size): # iterate through the columns
                if i == j:
                    updated_matrix[f'{i},{j}'] = '1' # set all elements on the diagonal to 1
                else:
                    updated_matrix[f'{i},{j}'] = current_matrix[f'{i},{j}'] # copy old value for all elements outside the diagonal
        self.matrices_stack.append(updated_matrix)  # add matrix to te stack
        self.update_displayed_matrix()  # display new matrix

    def make_symmetric(self):
        current_matrix = self.matrices_stack[-1]  # retrieve matrix currently displayed
        matrix_size = int(math.sqrt(len(current_matrix)))  # determine the size of the matrix
        updated_matrix = {}  # new matrix to be built
        for i in range(matrix_size):
            for j in range(i, matrix_size):
                updated_matrix[f'{i},{j}'] = current_matrix[f'{i},{j}'] # copy the old value
                if i != j:
                    updated_matrix[f'{j},{i}'] = current_matrix[f'{i},{j}']  # match corresponding element for all elements outside the diagonal
        self.matrices_stack.append(updated_matrix)  # add matrix to te stack
        self.update_displayed_matrix()  # display new matrix

if __name__ == '__main__':
    app = zero_one_matrices_tool()
    app.run()