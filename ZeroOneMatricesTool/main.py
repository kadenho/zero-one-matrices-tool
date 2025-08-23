import math
import re
import sys
from datetime import datetime
import json

from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from ZeroOneMatricesTool.database import MatrixDatabase, User, Matrix, MatrixElement

'''
Custom Kivy Screen Classes
'''


class HomeScreen(Screen):
    pass


class EnterMatrixScreen(Screen):
    entered_matrix = {}  # Stores the matrix the user enters


class LoadMatrixScreen(Screen):
    saved_matrices = []  # Saves a list of saved matrices
    display_index = 0  # Stores the index of the first element currently shown in the load matrix list


class MatrixEditorScreen(Screen):
    pass


class SaveMatrixScreen(Screen):
    pass


def build_matrix_database():
    file_path = 'config.json'
    try:
        with open(file_path) as json_file:
            data = json.load(json_file)
            database_host = data["database"]["host"]
            database_port = data["database"]["port"]
            database_name = data["database"]["name"]
            database_user = data["database"]["user"]
            database_password = data["database"]["password"]
    except FileNotFoundError:
        print('config.json not found.')
        sys.exit(1)
    url = MatrixDatabase.construct_mysql_url(database_host, int(database_port), database_name, database_user,
                                             database_password)
    matrix_database = MatrixDatabase(url)
    return matrix_database


class SelectUserScreen(Screen):
    def on_pre_enter(self):  # Runs on enter the screen
        self.populate_select_user_spinner()

    def populate_select_user_spinner(self):
        """
        Populates the select user spinner with each username in the database
        """
        matrix_database = build_matrix_database()
        screen_database_session = matrix_database.create_session()
        users = screen_database_session.query(User).all()
        screen_database_session.close()
        self.ids.user_select_spinner.values = [user.username for user in
                                               users]


class CreateUserScreen(Screen):
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
        s = re.sub(self.pat, '', substring)

        if not self.text and s:
            return super().insert_text(s[0], from_undo=from_undo)
        return


class MatrixSizeTextInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        new_text = self.text[:self.cursor_index()] + substring + self.text[
                                                                 self.cursor_index():]
        if not new_text.isdigit():
            return
        if not (1 <= int(new_text) <= 20):
            return

        return super().insert_text(substring, from_undo=from_undo)


class NameTextInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        s = "".join([c for c in substring if c != ' ' and c != '\t'])
        super().insert_text(s, from_undo=from_undo)


class LimitedDropdown(DropDown):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_height = 400


class UserSelectSpinner(Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dropdown_cls = LimitedDropdown


class LoadMatrixSelectBox(BoxLayout):
    matrix_id = StringProperty()
    matrix_name = StringProperty()
    save_timestamp = StringProperty()


"""
Define kivy app class
"""


class ZeroOneMatricesTool(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.matrix_database = build_matrix_database()
        self.database_session = self.matrix_database.create_session()
        self.screen_manager = ScreenManager(transition=NoTransition())
        self.matrices_stack = []
        self.user_id = None

    def build(self):
        self.screen_manager.add_widget(SelectUserScreen(name='SelectUserScreen'))
        self.screen_manager.add_widget(CreateUserScreen(name='CreateUserScreen'))
        self.screen_manager.add_widget(HomeScreen(name='HomeScreen'))
        self.screen_manager.add_widget(EnterMatrixScreen(name='EnterMatrixScreen'))
        self.screen_manager.add_widget(LoadMatrixScreen(name='LoadMatrixScreen'))
        self.screen_manager.add_widget(MatrixEditorScreen(name='MatrixEditorScreen'))
        self.screen_manager.add_widget(SaveMatrixScreen(name='SaveMatrixScreen'))
        return self.screen_manager

    def log_in(self):
        """
        Logs the user in.
        """
        selected_user = self.root.get_screen(
            'SelectUserScreen').ids.user_select_spinner.text
        if selected_user == 'Select User':
            Popup(title='User not selected', content=Label(text='Must select user!'),
                  size_hint=(0.5, 0.5)).open()
        else:
            self.user_id = self.database_session.query(User).filter(
                User.username == selected_user).one().user_id
            self.root.current = 'HomeScreen'

    def create_user(self):
        """
        Adds a new user to the database.
        """
        entered_username = self.root.get_screen(
            'CreateUserScreen').ids.create_user_text_input.text
        if entered_username == '':
            Popup(title='Invalid username', content=Label(text='Username cannot be blank!'),
                  size_hint=(0.5, 0.5)).open()
        elif self.database_session.query(User).filter(
                User.username == entered_username).count() > 0:
            self.root.get_screen(
                'CreateUserScreen').ids.create_user_text_input.text = ''
            Popup(title='Invalid username', content=Label(text='Username taken!'),
                  size_hint=(0.5, 0.5)).open()
        else:
            self.database_session.add(User(username=entered_username))
            self.database_session.commit()
            self.root.get_screen(
                'CreateUserScreen').ids.create_user_text_input.text = ''
            self.screen_manager.current = 'SelectUserScreen'

    def build_matrix_entry_box(self):
        """
        Constructs a BoxLayout with text inputs allowing the user to enter their matrix.
        """
        matrix_entry_box = self.root.get_screen(
            'EnterMatrixScreen').ids.matrix_entry_box
        try:
            matrix_size = int(self.root.get_screen(
                'HomeScreen').ids.matrix_size_text_input.text)
            matrix_entry_box.clear_widgets()
            self.root.get_screen('EnterMatrixScreen').entered_matrix.clear()
            for i in range(matrix_size):
                row_box = BoxLayout(orientation='horizontal')
                matrix_entry_box.add_widget(row_box)
                for j in range(matrix_size):
                    zero_one_text_input = ZeroOneTextInput(hint_text='0/1', font_size='10sp', write_tab=False,
                                                           multiline=False)
                    self.root.get_screen('EnterMatrixScreen').entered_matrix[
                        f'{i},{j}'] = zero_one_text_input
                    row_box.add_widget(zero_one_text_input)
            self.screen_manager.current = 'EnterMatrixScreen'
        except ValueError:
            if self.root.get_screen('HomeScreen').ids.matrix_size_text_input.text == '':
                Popup(title='Value Error', content=Label(text='Size cannot be blank!'),
                      size_hint=(0.5, 0.5)).open()
            else:
                Popup(title='Value Error', content=Label(text='Value Error has occurred!'),
                      size_hint=(0.5, 0.5)).open()

    def stack_entered_matrix(self):
        """

        Updates the stack to only have the entered matrix

        """
        self.matrices_stack.clear()
        matrix_size = int(self.root.get_screen('HomeScreen').ids.matrix_size_text_input.text)
        matrix = {}
        for i in range(matrix_size):
            for j in range(matrix_size):
                entry_value = self.root.get_screen('EnterMatrixScreen').entered_matrix[
                    f'{i},{j}'].text
                if entry_value == '':
                    entry_value = '0'
                matrix[f'{i},{j}'] = entry_value
        self.matrices_stack.append(matrix)
        self.update_displayed_matrix()
        app.root.current = 'MatrixEditorScreen'

    def populate_load_matrix_list(self, search_query):
        """
        Populates the list of matrices the user has saved, adhering to the search query
        :param search_query:
        :return:
        """
        load_screen = self.screen_manager.get_screen('LoadMatrixScreen')
        load_screen.ids.load_matrix_select_box.clear_widgets()
        load_screen.saved_matrices.clear()
        if search_query == '':
            load_screen.saved_matrices = self.database_session.query(Matrix).filter(
                Matrix.user_id == self.user_id).all()
        else:
            iterated_saved_matrices = self.database_session.query(Matrix).filter(
                Matrix.user_id == self.user_id).all()
            for matrix in iterated_saved_matrices:
                if search_query.lower().strip() in matrix.name.lower().strip():
                    load_screen.saved_matrices.append(matrix)
        load_screen.saved_matrices.reverse()
        load_screen.display_index = 0
        self.display_load_matrix_list(load_screen.display_index)
        app.root.current = 'LoadMatrixScreen'

    def display_load_matrix_list(self, begin_index):
        """
        Constructs a BoxLayout with a list of save matrices, showing five at a time, allowing the user to load previously saved matrices
        :param begin_index:
        :return:
        """
        load_screen = self.screen_manager.get_screen('LoadMatrixScreen')
        load_screen.ids.load_matrix_select_box.clear_widgets()
        if not load_screen.saved_matrices:
            load_screen.ids.load_matrix_select_box.add_widget(
                SelfFormattingText(text='No matrices found!',
                                   font_size='30sp'))
            app.root.current = 'LoadMatrixScreen'
        else:
            if begin_index + 5 < len(
                    load_screen.saved_matrices):
                end_index = begin_index + 5
                empty_spaces = 0
            else:
                end_index = len(load_screen.saved_matrices)
                empty_spaces = begin_index + 5 - len(
                    load_screen.saved_matrices)
            for i in range(begin_index, end_index):
                load_screen.ids.load_matrix_select_box.add_widget(
                    LoadMatrixSelectBox(matrix_id=str(load_screen.saved_matrices[i].matrix_id),
                                        matrix_name=load_screen.saved_matrices[i].name,
                                        save_timestamp=load_screen.saved_matrices[i].timestamp.strftime(
                                            "%Y-%m-%d %H:%M:%S")))
            for i in range(empty_spaces):
                load_screen.ids.load_matrix_select_box.add_widget(Widget())

    def move_load_matrix_list_previous(self):
        """
        Moves the displayed matrices list 5 elements towards the beginning of the list
        :return:
        """
        load_screen = self.screen_manager.get_screen('LoadMatrixScreen')
        if load_screen.display_index - 5 >= 0:
            load_screen.display_index -= 5
            self.display_load_matrix_list(load_screen.display_index)

    def move_load_matrix_list_next(self):
        """
        Moves the displayed matrices list 5 elements towards the end of the list
        :return:
        """
        load_screen = self.screen_manager.get_screen('LoadMatrixScreen')
        if load_screen.display_index + 5 < len(load_screen.saved_matrices):
            load_screen.display_index += 5
            self.display_load_matrix_list(load_screen.display_index)

    def stack_saved_matrix(self, matrix_id):
        """
        Puts the saved matrix into the matrix editor stack
        :param matrix_id:
        :return:
        """
        self.matrices_stack.clear()
        constructed_matrix = {}
        elements = self.database_session.query(MatrixElement).filter(MatrixElement.matrix_id == int(matrix_id)).all()
        for element in elements:
            constructed_matrix[f'{element.row},{element.col}'] = str(element.value)
        self.matrices_stack.append(constructed_matrix)
        self.update_displayed_matrix()
        app.root.current = 'MatrixEditorScreen'

    def update_displayed_matrix(self):
        """

        Updates the displayed matrix to the most recent

        """
        matrix_display_box = self.root.get_screen(
            'MatrixEditorScreen').ids.matrix_editor_display_box
        matrix_display_box.clear_widgets()
        displayed_matrix = self.matrices_stack[-1]
        matrix_size = int(math.sqrt(len(displayed_matrix)))
        for i in range(matrix_size):
            row_box = BoxLayout(orientation='horizontal')
            matrix_display_box.add_widget(row_box)
            for j in range(matrix_size):
                matrix_display_label = SelfFormattingText(
                    text=displayed_matrix[f'{i},{j}'])
                row_box.add_widget(matrix_display_label)

    def undo_operation(self):
        """
        Removes one matrix from the stack and displays the new top matrix
        :return:
        """
        if len(self.matrices_stack) > 1:
            self.matrices_stack.pop(-1)
            self.update_displayed_matrix()

    def make_irreflexive(self):
        """
        Applies the irreflexive property to the matrix in the matrix editor
        :return:
        """
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

    def make_anti_symmetric(self):
        """
        Applies the antisymmetric property to the matrix in the matrix editor
        :return:
        """
        current_matrix = self.matrices_stack[-1]
        matrix_size = int(math.sqrt(len(current_matrix)))
        updated_matrix = {}
        for i in range(matrix_size):
            for j in range(i, matrix_size):
                if i != j:
                    updated_matrix[f'{i},{j}'] = current_matrix[f'{i},{j}']
                    if current_matrix[f'{i},{j}'] == '1':
                        updated_matrix[f'{j},{i}'] = '0'
                    else:
                        updated_matrix[f'{j},{i}'] = current_matrix[
                            f'{j},{i}']
                else:
                    updated_matrix[f'{i},{j}'] = current_matrix[
                        f'{i},{j}']
        self.matrices_stack.append(updated_matrix)
        self.update_displayed_matrix()

    def make_asymmetric(self):
        """
        Applies the asymmetric property to the matrix in the matrix editor
        :return:
        """
        current_matrix = self.matrices_stack[-1]
        matrix_size = int(math.sqrt(len(current_matrix)))
        updated_matrix = {}
        for i in range(matrix_size):
            for j in range(i, matrix_size):
                if i != j:
                    updated_matrix[f'{i},{j}'] = current_matrix[f'{i},{j}']
                    if current_matrix[f'{i},{j}'] == '1':
                        updated_matrix[f'{j},{i}'] = '0'
                    else:
                        updated_matrix[f'{j},{i}'] = current_matrix[
                            f'{j},{i}']
                else:
                    updated_matrix[f'{i},{j}'] = '0'
        self.matrices_stack.append(updated_matrix)
        self.update_displayed_matrix()

    def make_reflexive(self):
        """
        Applies the reflexive property to the matrix in the matrix editor
        :return:
        """
        current_matrix = self.matrices_stack[-1]
        matrix_size = int(math.sqrt(len(current_matrix)))
        updated_matrix = {}
        for i in range(matrix_size):
            for j in range(matrix_size):
                if i == j:
                    updated_matrix[f'{i},{j}'] = '1'
                else:
                    updated_matrix[f'{i},{j}'] = current_matrix[
                        f'{i},{j}']
        self.matrices_stack.append(updated_matrix)
        self.update_displayed_matrix()

    def make_symmetric(self):
        """
        Applies the symmetric property to the matrix in the matrix editor
        :return:
        """
        current_matrix = self.matrices_stack[-1]
        matrix_size = int(math.sqrt(len(current_matrix)))
        updated_matrix = {}
        for i in range(matrix_size):
            for j in range(i, matrix_size):
                if current_matrix[f'{i},{j}'] == '1' or current_matrix[
                    f'{j},{i}'] == '1':
                    updated_matrix[f'{i},{j}'] = updated_matrix[f'{j},{i}'] = '1'
                else:
                    updated_matrix[f'{i},{j}'] = updated_matrix[f'{j},{i}'] = '0'
        self.matrices_stack.append(updated_matrix)
        self.update_displayed_matrix()

    def make_transitive(self):
        """
        Applies the transitive property to the matrix in the matrix editor
        :return:
        """
        current_matrix = self.matrices_stack[-1]
        matrix_size = int(math.sqrt(len(current_matrix)))
        updated_matrix = current_matrix.copy()
        for k in range(matrix_size):  # Warshall's algorithm
            for i in range(matrix_size):
                for j in range(matrix_size):
                    ik = updated_matrix[f'{i},{k}']
                    kj = updated_matrix[f'{k},{j}']
                    if ik == '1' and kj == '1':
                        updated_matrix[f'{i},{j}'] = '1'
        self.matrices_stack.append(updated_matrix)
        self.update_displayed_matrix()

    def make_equivalent(self):
        """
        Makes the matrix an equivalence relation in the matrix editor
        :return:
        """
        current_matrix = self.matrices_stack[-1]
        matrix_size = int(math.sqrt(len(current_matrix)))
        updated_matrix = {}
        for i in range(matrix_size):
            for j in range(matrix_size):
                if i == j:
                    updated_matrix[f'{i},{j}'] = '1'
                elif current_matrix[f'{i},{j}'] == '1' or current_matrix[f'{j},{i}'] == '1':
                    updated_matrix[f'{i},{j}'] = updated_matrix[f'{j},{i}'] = '1'
                else:
                    updated_matrix[f'{i},{j}'] = updated_matrix[f'{j},{i}'] = '0'
        for k in range(matrix_size):  # Warshall's algorithm
            for i in range(matrix_size):
                for j in range(matrix_size):
                    ik = updated_matrix[f'{i},{k}']
                    kj = updated_matrix[f'{k},{j}']
                    if ik == '1' and kj == '1':
                        updated_matrix[f'{i},{j}'] = '1'
        self.matrices_stack.append(updated_matrix)
        self.update_displayed_matrix()

    def save_matrix(self):
        """
        Saves the matrix in the matrix editor to the database
        :return:
        """
        matrix_name = self.root.get_screen('SaveMatrixScreen').ids.save_matrix_name_text_input.text
        if matrix_name == '':
            Popup(title='Empty Name', content=Label(text='Name cannot be blank!'), size_hint=(0.5, 0.5)).open()
        elif self.database_session.query(Matrix).filter(Matrix.name == matrix_name,
                                                        Matrix.user_id == self.user_id).count() == 0:
            current_timestamp = datetime.now()
            new_matrix = Matrix(user_id=self.user_id, timestamp=current_timestamp, name=matrix_name)
            self.database_session.add(new_matrix)
            self.database_session.flush()
            current_matrix = self.matrices_stack[-1]
            for key in current_matrix:
                row, col = map(int, key.split(','))
                self.database_session.add(
                    MatrixElement(matrix_id=new_matrix.matrix_id, row=row, col=col, value=current_matrix[key]))
            self.database_session.commit()
            Popup(title='Success', content=Label(text='Matrix Saved'), size_hint=(0.5, 0.5)).open()
            self.root.current = 'MatrixEditorScreen'
            self.root.get_screen('SaveMatrixScreen').ids.save_matrix_name_text_input.text = ''
        else:
            Popup(title='Name taken', content=Label(text='Name already used!'), size_hint=(0.5, 0.5)).open()
            self.root.get_screen('SaveMatrixScreen').ids.save_matrix_name_text_input.text = ''


if __name__ == '__main__':
    app = ZeroOneMatricesTool()
    app.run()
