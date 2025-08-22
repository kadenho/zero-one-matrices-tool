# zero-one-matrices-tool
A tool developed to enforce relational properties on 0-1 matrices featuring a GUI.\
Developed on Python 3.13 \
Authored by Kaden Ho
### Status:
✅ Complete and functional, no known bugs at this time

### Packages:
#### Default python packages:
math \
re \
sys \
datetime
#### Other packages:
kivy version 2.3.1 \
sqlalchemy version 2.0.40



### Setup:

### In terminal:
#### Download required packages:
mysql-connector-python (or the python connector for your dialect of choice)\
sqlalchemy \
kivy
### In one of the following SQL dialects:
###### (PostgreSQL, MySQL and MariaDB, SQLite, Oracle, Microsoft SQL Server)
Create an empty database
### In config.py
Edit DB_HOST, DB_PORT, DB_NAME, DB_USER, and DB_PASSWORD to match your database information. \
\
DB_HOST = The server where your database is located (typically localhost) \
\
DB_PORT = Your database port\
Common default port numbers:
PostgreSQL: 5432 \
MySQL and MariaDB: 3306 \
Oracle: 1521 \
Microsoft SQL Server: 1433 \
\
DB_NAME = The name you gave to your database\
\
DB_USER = The username used in your database dialect (commonly root)\
\
DB_PASSWORD = The password set on your database
### In database_installer.py
Run the installer file.
### In main.py
Run the main file.



## Creating a user
To create a user, click on the 'Create User' button on the select user screen. \
From there, enter your name in the provided text box and click 'Create User'.

## Logging in
To log in, click 'Select User' to open a dropdown. \
Click your username and then click the 'Login' button.

## Creating a new matrix
To create a new matrix, first enter the size of your matrix in the provided text box and click next. \
Enter either the number 1 or 0 in the text boxes below, and click next. Any unpopulated textboxes will be filled in as a 0 when the user clicks next.

## Using the matrix editor
After creating or loading a matrix, use the provided buttons on the third and fourth rows of the matrix editor to apply properties to the matrix. \
Use the undo button to revert the matrix to the state it was in before applying the most recent property.

## Saving a matrix
From the matrix editor, click save matrix on the second row. \
Enter the name of the matrix in the provided text box and click save matrix.

## Loading a matrix
From the home screen, select the 'Load Matrix' button. \
A list of saved matrices will appear, to select a matrix click the on the name of the matrix. \
If the user has more than 5 matrices saved, they can use the 'Next' and 'Previous' buttons to navigate through the list of matrices. \
The user can also enter a search query into the text box next to the search button. Upon clicking the search button, the list will be filtered to only show results that contain the search query.