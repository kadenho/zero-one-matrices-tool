import math
import re
from datetime import datetime

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
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

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


class SelectUserScreen(Screen):
    def on_pre_enter(self):  # Runs on enter the screen
        self.populate_select_user_spinner()

    def populate_select_user_spinner(self):
        """
        Populates the select user spinner with each username in the database
        """
        url = MatrixDatabase.construct_mysql_url(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)
        matrix_database = MatrixDatabase(url)
        screen_database_session = matrix_database.create_session()
        users = screen_database_session.query(User).all()  # Query all the users
        screen_database_session.close()
        self.ids.user_select_spinner.values = [user.username for user in
                                               users]  # Display each user's usernames in the select user spinner


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
        # Filter out anything that's not 0 or 1
        s = re.sub(self.pat, '', substring)

        # Only insert if field is empty and s is not empty
        if not self.text and s:
            return super().insert_text(s[0], from_undo=from_undo)
        return


class MatrixSizeTextInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        new_text = self.text[:self.cursor_index()] + substring + self.text[
                                                                 self.cursor_index():]  # Preview what the new text would be
        if not new_text.isdigit():  # Allow only digits
            return
        if not (1 <= int(new_text) <= 20):  # Allow only numbers from 1 to 20
            return

        return super().insert_text(substring, from_undo=from_undo)


class NameTextInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        s = "".join([c for c in substring if c != ' ' and c != '\t'])  # Filter out spaces and tabs
        super().insert_text(s, from_undo=from_undo)


class LimitedDropdown(DropDown):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_height = 400  # Set the height of the spinner to be 400 pixels, allowing it to be scrollable


class UserSelectSpinner(Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dropdown_cls = LimitedDropdown  # Use the limited dropdown for the spinner


class LoadMatrixSelectBox(BoxLayout):
    matrix_id = StringProperty()  # Store the ID of the matrix shown
    matrix_name = StringProperty()  # Store the matrix's name
    save_timestamp = StringProperty()  # Store the matrix's created timestamp


"""
Define kivy app class
"""


class ZeroOneMatricesTool(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        url = MatrixDatabase.construct_mysql_url(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)
        self.matrix_database = MatrixDatabase(url)
        self.database_session = self.matrix_database.create_session()  # Session that makes queries the database
        self.screen_manager = ScreenManager(transition=NoTransition())  # Manages changes between scenes
        self.matrices_stack = []  # Stack that tracks history in the matrix editor
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
            'SelectUserScreen').ids.user_select_spinner.text  # Gets the username of the selected user
        if selected_user == 'Select User':  # If no user has been selected
            Popup(title='User not selected', content=Label(text='Must select user!'),
                  size_hint=(0.5, 0.5)).open()  # Throw an error
        else:
            self.user_id = self.database_session.query(User).filter(
                User.username == selected_user).one().user_id  # Find the user id of the selected user
            self.root.current = 'HomeScreen'  # Change the screen to the home screen

    def create_user(self):
        """
        Adds a new user to the database.
        """
        entered_username = self.root.get_screen(
            'CreateUserScreen').ids.create_user_text_input.text  # Retrieve the username the user entered
        if entered_username == '':  # If no username has been entered
            Popup(title='Invalid username', content=Label(text='Username cannot be blank!'),
                  size_hint=(0.5, 0.5)).open()  # Throw an error
        elif self.database_session.query(User).filter(
                User.username == entered_username).count() > 0:  # If the username is already taken
            self.root.get_screen(
                'CreateUserScreen').ids.create_user_text_input.text = ''  # Clear the username enter box
            Popup(title='Invalid username', content=Label(text='Username taken!'),
                  size_hint=(0.5, 0.5)).open()  # Throw an error
        else:
            self.database_session.add(User(username=entered_username))  # Create the new user
            self.database_session.commit()  # Commit the change to the database
            self.root.get_screen(
                'CreateUserScreen').ids.create_user_text_input.text = ''  # Clear the username enter box
            self.screen_manager.current = 'SelectUserScreen'  # Change the screen back to the log in screen

    def build_matrix_entry_box(self):
        """
        Constructs a BoxLayout with text inputs allowing the user to enter their matrix.
        """
        matrix_entry_box = self.root.get_screen(
            'EnterMatrixScreen').ids.matrix_entry_box  # Get the box where text boxes will be put into
        try:
            matrix_size = int(self.root.get_screen(
                'HomeScreen').ids.matrix_size_text_input.text)  # Retrieve the entered size of the matrix
            matrix_entry_box.clear_widgets()  # Clear any old widgets
            self.root.get_screen('EnterMatrixScreen').entered_matrix.clear()  # Clear any old matrices stored
            for i in range(matrix_size):  # Iterating through the rows
                row_box = BoxLayout(orientation='horizontal')  # Create a box to put text inputs into
                matrix_entry_box.add_widget(row_box)  # Add the box onto the screen
                for j in range(matrix_size):  # Iterating through each spot of the row
                    zero_one_text_input = ZeroOneTextInput(hint_text='0/1', font_size='10sp', write_tab=False,
                                                           multiline=False)  # Create a text entry box
                    self.root.get_screen('EnterMatrixScreen').entered_matrix[
                        f'{i},{j}'] = zero_one_text_input  # Link the box to a key for later reference
                    row_box.add_widget(zero_one_text_input)  # Add text input box into the row box
            self.screen_manager.current = 'EnterMatrixScreen'  # Change the screen to the matrix editor screen
        except ValueError:
            if self.root.get_screen('HomeScreen').ids.matrix_size_text_input.text == '':  # If no size has been entered
                Popup(title='Value Error', content=Label(text='Size cannot be blank!'),
                      size_hint=(0.5, 0.5)).open()  # Throw error
            else:
                Popup(title='Value Error', content=Label(text='Value Error has occurred!'),
                      size_hint=(0.5, 0.5)).open()  # Throw error

    def stack_entered_matrix(self):
        """

        Updates the stack to only have the entered matrix

        """
        self.matrices_stack.clear()  # remove any matrices already in the stack
        matrix_size = int(self.root.get_screen('HomeScreen').ids.matrix_size_text_input.text)  # retrieve matrix size
        matrix = {}  # matrix to be stacked
        for i in range(matrix_size):  # iterate through the rows
            for j in range(matrix_size):  # iterate through the columns
                entry_value = self.root.get_screen('EnterMatrixScreen').entered_matrix[
                    f'{i},{j}'].text  # retrieve the entered value
                if entry_value == '':  # if there was none
                    entry_value = '0'  # set the entered value to 0
                matrix[f'{i},{j}'] = entry_value  # designate the element key with the entered value
        self.matrices_stack.append(matrix)  # append matrix to the stack
        self.update_displayed_matrix()  # update the displayed matrix
        app.root.current = 'MatrixEditorScreen'

    def populate_load_matrix_list(self, search_query):
        """
        Populates the list of matrices the user has saved, adhering to the search query
        :param search_query:
        :return:
        """
        load_screen = self.screen_manager.get_screen('LoadMatrixScreen')  # Retrieve the load matrix screen
        load_screen.ids.load_matrix_select_box.clear_widgets()  # Clear any old widgets
        load_screen.saved_matrices.clear()  # Clear any old saved matrices
        if search_query == '':  # If the user searches nothing
            load_screen.saved_matrices = self.database_session.query(Matrix).filter(
                Matrix.user_id == self.user_id).all()  # Pull all matrices the user has saved
        else:  # If the user has searched something
            iterated_saved_matrices = self.database_session.query(Matrix).filter(
                Matrix.user_id == self.user_id).all()  # Pull all matrices the user has saved
            for matrix in iterated_saved_matrices:  # Iterate through all the saved matrices
                if search_query.lower().strip() in matrix.name.lower().strip():  # If the search query appears in the matrix's name
                    load_screen.saved_matrices.append(matrix)  # Save the matrix to the list of matrices to be displayed
        load_screen.display_index = 0  # Begin the list at the 0th element
        self.display_load_matrix_list(load_screen.display_index)  # Display the list of saved matrices
        app.root.current = 'LoadMatrixScreen'  # Change the screen to the load matrix screen

    def display_load_matrix_list(self, begin_index):
        """
        Constructs a BoxLayout with a list of save matrices, showing five at a time, allowing the user to load previously saved matrices
        :param begin_index:
        :return:
        """
        load_screen = self.screen_manager.get_screen('LoadMatrixScreen')  # Retrieve the load matrix screen
        load_screen.ids.load_matrix_select_box.clear_widgets()  # Clear any old widgets in the list display box
        if not load_screen.saved_matrices:  # If there are no saved matrices
            load_screen.ids.load_matrix_select_box.add_widget(
                SelfFormattingText(text='No matrices found!',
                                   font_size='30sp'))  # Display text notifying the user there are no saved matrices
            app.root.current = 'LoadMatrixScreen'  # Change the screen to the load matrix screen
        else:
            if begin_index + 5 < len(
                    load_screen.saved_matrices):  # If there are enough matrices left to fill the entire box
                end_index = begin_index + 5  # Set the end index to be five past the beginning index
                empty_spaces = 0  # Add zero empty spaces
            else:  # If there are not enough matrices left to fill the entire box
                end_index = len(load_screen.saved_matrices)  # Set the end index to the last matrix in the list
                empty_spaces = begin_index + 5 - len(
                    load_screen.saved_matrices)  # Determine the number of empty spaces required to fill the entire box
            for i in range(begin_index, end_index):
                load_screen.ids.load_matrix_select_box.add_widget(
                    LoadMatrixSelectBox(matrix_id=str(load_screen.saved_matrices[i].matrix_id),
                                        matrix_name=load_screen.saved_matrices[i].name,
                                        save_timestamp=load_screen.saved_matrices[i].timestamp.strftime(
                                            "%Y-%m-%d %H:%M:%S")))  # Add the matrix select box widget
            for i in range(empty_spaces):  # Add the empty spaces required to fill the entire box
                load_screen.ids.load_matrix_select_box.add_widget(Widget())

    def move_load_matrix_list_previous(self):
        """
        Moves the displayed matrices list 5 elements towards the beginning of the list
        :return:
        """
        load_screen = self.screen_manager.get_screen('LoadMatrixScreen')  # Retrieve the load matrix screen
        if load_screen.display_index - 5 >= 0:  # If there is room to move the list towards the beginning
            load_screen.display_index -= 5  # Move the matrix towards the beginning
            self.display_load_matrix_list(load_screen.display_index)  # Display the new list range

    def move_load_matrix_list_next(self):
        """
        Moves the displayed matrices list 5 elements towards the end of the list
        :return:
        """
        load_screen = self.screen_manager.get_screen('LoadMatrixScreen')  # Retrieve the load matrix screen
        if load_screen.display_index + 5 < len(load_screen.saved_matrices):  # If there is room to move the list towards the end
            load_screen.display_index += 5  # Move the list towards the end
            self.display_load_matrix_list(load_screen.display_index)  # Display the new list range

    def stack_saved_matrix(self, matrix_id):
        """
        Puts the saved matrix into the matrix editor stack
        :param matrix_id:
        :return:
        """
        self.matrices_stack.clear()  # remove any matrices already in the stack
        constructed_matrix = {}
        elements = self.database_session.query(MatrixElement).filter(MatrixElement.matrix_id == int(matrix_id)).all()  # Pull all the elements for the matrix
        for element in elements:  # For each element
            constructed_matrix[f'{element.row},{element.col}'] = str(element.value)  # Add a key value pair to the dictionary
        self.matrices_stack.append(constructed_matrix)  # Add the new dictionary defined matrix to the stack
        self.update_displayed_matrix()  # update the displayed matrix
        app.root.current = 'MatrixEditorScreen'  # Change screen to the matrix editor

    def update_displayed_matrix(self):
        """

        Updates the displayed matrix to the most recent

        """
        matrix_display_box = self.root.get_screen(
            'MatrixEditorScreen').ids.matrix_editor_display_box  # retrieve box where matrix is displayed
        matrix_display_box.clear_widgets()  # clear the current display
        displayed_matrix = self.matrices_stack[-1]  # retrieve matrix currently displayed
        matrix_size = int(math.sqrt(len(displayed_matrix)))  # determine the size of the matrix
        for i in range(matrix_size):  # iterate through the rows
            row_box = BoxLayout(orientation='horizontal')  # create a box for the row
            matrix_display_box.add_widget(row_box)  # add box to the display area
            for j in range(matrix_size):  # iterate through the columns
                matrix_display_label = SelfFormattingText(
                    text=displayed_matrix[f'{i},{j}'])  # create a label with corresponding value
                row_box.add_widget(matrix_display_label)  # add the label

    def undo_operation(self):
        """
        Removes one matrix from the stack and displays the new top matrix
        :return:
        """
        if len(self.matrices_stack) > 1:  # given there are at least two matrices in the stack
            self.matrices_stack.pop(-1)  # remove matrix on the top of the stack
            self.update_displayed_matrix()  # display new matrix

    def make_irreflexive(self):
        """
        Applies the irreflexive property to the matrix in the matrix editor
        :return:
        """
        current_matrix = self.matrices_stack[-1]  # retrieve matrix currently displayed
        matrix_size = int(math.sqrt(len(current_matrix)))  # determine the size of the matrix
        updated_matrix = {}  # new matrix to be built
        for i in range(matrix_size):  # iterate through the rows
            for j in range(matrix_size):  # iterate through the columns
                if i == j:  # if it is on the diagonal
                    updated_matrix[f'{i},{j}'] = '0'  # set the value to 0
                else:
                    updated_matrix[f'{i},{j}'] = current_matrix[f'{i},{j}']  # copy the old value
        self.matrices_stack.append(updated_matrix)  # add matrix to the stack
        self.update_displayed_matrix()  # display new matrix

    def make_anti_symmetric(self):
        """
        Applies the antisymmetric property to the matrix in the matrix editor
        :return:
        """
        current_matrix = self.matrices_stack[-1]  # retrieve matrix currently displayed
        matrix_size = int(math.sqrt(len(current_matrix)))  # determine the size of the matrix
        updated_matrix = {}  # new matrix to be built
        for i in range(matrix_size):  # iterate through the rows
            for j in range(i, matrix_size):  # iterate through the columns
                if i != j:  # if it is not on the diagonal
                    updated_matrix[f'{i},{j}'] = current_matrix[f'{i},{j}']  # copy the old value
                    if current_matrix[f'{i},{j}'] == '1':  # if element is a 1
                        updated_matrix[f'{j},{i}'] = '0'  # corresponding element must be 0
                    else:  # else (element is a 0)
                        updated_matrix[f'{j},{i}'] = current_matrix[
                            f'{j},{i}']  # corresponding element can be copied safely
                else:
                    updated_matrix[f'{i},{j}'] = current_matrix[
                        f'{i},{j}']  # copy the old value for elements on the diagonal
        self.matrices_stack.append(updated_matrix)  # add matrix to te stack
        self.update_displayed_matrix()  # display new matrix

    def make_asymmetric(self):
        """
        Applies the asymmetric property to the matrix in the matrix editor
        :return:
        """
        current_matrix = self.matrices_stack[-1]  # retrieve matrix currently displayed
        matrix_size = int(math.sqrt(len(current_matrix)))  # determine the size of the matrix
        updated_matrix = {}  # new matrix to be built
        for i in range(matrix_size):  # iterate through the rows
            for j in range(i, matrix_size):  # iterate through the columns
                if i != j:  # if it is not on the diagonal
                    updated_matrix[f'{i},{j}'] = current_matrix[f'{i},{j}']  # copy the old value
                    if current_matrix[f'{i},{j}'] == '1':  # if element is a 1
                        updated_matrix[f'{j},{i}'] = '0'  # corresponding element must be 0
                    else:  # else (element is a 0)
                        updated_matrix[f'{j},{i}'] = current_matrix[
                            f'{j},{i}']  # corresponding element can be copied safely
                else:
                    updated_matrix[f'{i},{j}'] = '0'
        self.matrices_stack.append(updated_matrix)  # add matrix to te stack
        self.update_displayed_matrix()  # display new matrix

    def make_reflexive(self):
        """
        Applies the reflexive property to the matrix in the matrix editor
        :return:
        """
        current_matrix = self.matrices_stack[-1]  # retrieve matrix currently displayed
        matrix_size = int(math.sqrt(len(current_matrix)))  # determine the size of the matrix
        updated_matrix = {}  # new matrix to be built
        for i in range(matrix_size):  # iterate through the rows
            for j in range(matrix_size):  # iterate through the columns
                if i == j:
                    updated_matrix[f'{i},{j}'] = '1'  # set all elements on the diagonal to 1
                else:
                    updated_matrix[f'{i},{j}'] = current_matrix[
                        f'{i},{j}']  # copy old value for all elements outside the diagonal
        self.matrices_stack.append(updated_matrix)  # add matrix to te stack
        self.update_displayed_matrix()  # display new matrix

    def make_symmetric(self):
        """
        Applies the symmetric property to the matrix in the matrix editor
        :return:
        """
        current_matrix = self.matrices_stack[-1]  # retrieve matrix currently displayed
        matrix_size = int(math.sqrt(len(current_matrix)))  # determine the size of the matrix
        updated_matrix = {}  # new matrix to be built
        for i in range(matrix_size):  # iterate through the rows
            for j in range(i, matrix_size):  # iterate through the columns
                if current_matrix[f'{i},{j}'] == '1' or current_matrix[
                    f'{j},{i}'] == '1':  # if a one is found in elements under check
                    updated_matrix[f'{i},{j}'] = updated_matrix[f'{j},{i}'] = '1'  # set both elements to 1
                else:  # if neither are a 1
                    updated_matrix[f'{i},{j}'] = updated_matrix[f'{j},{i}'] = '0'  # set both elements to 0
        self.matrices_stack.append(updated_matrix)  # add matrix to te stack
        self.update_displayed_matrix()  # display new matrix

    def make_transitive(self):
        """
        Applies the transitive property to the matrix in the matrix editor
        :return:
        """
        current_matrix = self.matrices_stack[-1]  # retrieve matrix currently displayed
        matrix_size = int(math.sqrt(len(current_matrix)))  # determine the size of the matrix
        updated_matrix = current_matrix.copy()  # new matrix to be built
        for k in range(matrix_size):
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
        current_matrix = self.matrices_stack[-1]  # retrieve matrix currently displayed
        matrix_size = int(math.sqrt(len(current_matrix)))  # determine the size of the matrix
        updated_matrix = {}  # new matrix to be built
        for i in range(matrix_size):  # iterate through the rows
            for j in range(matrix_size):  # iterate through the columns
                if i == j:
                    updated_matrix[f'{i},{j}'] = '1'  # set all elements on the diagonal to 1
                elif current_matrix[f'{i},{j}'] == '1' or current_matrix[f'{j},{i}'] == '1':  # If a one is found in elements under test
                    updated_matrix[f'{i},{j}'] = updated_matrix[f'{j},{i}'] = '1'  # Set both elements to 1
                else:  # If neither are 1
                    updated_matrix[f'{i},{j}'] = updated_matrix[f'{j},{i}'] = '0'  # Set both elements to 0
        for k in range(matrix_size):  # Warshall's algorithm
            for i in range(matrix_size):
                for j in range(matrix_size):
                    ik = updated_matrix[f'{i},{k}']
                    kj = updated_matrix[f'{k},{j}']
                    if ik == '1' and kj == '1':
                        updated_matrix[f'{i},{j}'] = '1'
        self.matrices_stack.append(updated_matrix)  # Stack the new matrix
        self.update_displayed_matrix()  # Update the displayed matrix

    def save_matrix(self):
        """
        Saves the matrix in the matrix editor to the database
        :return:
        """
        matrix_name = self.root.get_screen('SaveMatrixScreen').ids.save_matrix_name_text_input.text  # Retrieve the entered matrix name
        if matrix_name == '':  # If the name is empty
            Popup(title='Empty Name', content=Label(text='Name cannot be blank!'), size_hint=(0.5, 0.5)).open()  # Throw an error
        elif self.database_session.query(Matrix).filter(Matrix.name == matrix_name,
                                                        Matrix.user_id == self.user_id).count() == 0:  # If the name is not a duplicate
            current_timestamp = datetime.now()  # Retrieve the current timestamp
            new_matrix = Matrix(user_id=self.user_id, timestamp=current_timestamp, name=matrix_name)  # Create a matrix database object
            self.database_session.add(new_matrix)  # Add the matrix database object to the database
            self.database_session.flush()  # Update database without committing
            current_matrix = self.matrices_stack[-1]  # Retrieve the current matrix
            for key in current_matrix:  # For each element in the dictionary defined matrix
                row, col = map(int, key.split(','))  # Map the key into row and col variables
                self.database_session.add(
                    MatrixElement(matrix_id=new_matrix.matrix_id, row=row, col=col, value=current_matrix[key]))  # Add a matrix element database object
            self.database_session.commit()  # Commit the new database information
            Popup(title='Success', content=Label(text='Matrix Saved'), size_hint=(0.5, 0.5)).open()  # Notify the user the matrix was saved
            self.root.current = 'MatrixEditorScreen'  # Change the screen back to the matrix editor
            self.root.get_screen('SaveMatrixScreen').ids.save_matrix_name_text_input.text = ''  # Clear the name text input
        else:  # If the name is a duplicate
            Popup(title='Name taken', content=Label(text='Name already used!'), size_hint=(0.5, 0.5)).open()  # Throw an error
            self.root.get_screen('SaveMatrixScreen').ids.save_matrix_name_text_input.text = ''  # Clear the name text input


if __name__ == '__main__':
    app = ZeroOneMatricesTool()
    app.run()
