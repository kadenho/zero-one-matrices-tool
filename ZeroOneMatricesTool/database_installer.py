from sys import stderr
from sqlalchemy.exc import SQLAlchemyError
from ZeroOneMatricesTool.database import MatrixDatabase


def main():
    try:
        url = MatrixDatabase.construct_mysql_url('localhost', 3306, 'matrices', 'root', 'sqlpassword')
        matrix_database = MatrixDatabase(url)
        matrix_database.ensure_tables_exist()
        print('Tables created.')
    except SQLAlchemyError as exception:
        print('Database setup failed!', file=stderr)
        print(f'Cause: {exception}', file=stderr)
        exit(1)


if __name__ == '__main__':
    main()
