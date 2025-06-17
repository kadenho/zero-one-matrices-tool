from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Persisted = declarative_base()

class User(Persisted):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(256), nullable=False)
    matrices = relationship('Matrix', back_populates='user')

class Matrix(Persisted):
    __tablename__ = 'matrices'
    matrix_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    name = Column(String(256), nullable=False)
    user = relationship('User', back_populates='matrices')
    matrix_elements = relationship('MatrixElement', back_populates='matrix')

class MatrixElement(Persisted):
    __tablename__ = 'matrix_elements'
    matrix_id = Column(Integer, ForeignKey('matrices.matrix_id', ondelete='CASCADE'), primary_key=True)
    row = Column(Integer, primary_key=True)
    col = Column(Integer, primary_key=True)
    value = Column(Integer, nullable=False)
    matrix = relationship('Matrix', back_populates='matrix_elements')

class MatrixDatabase(object):
    @staticmethod
    def construct_mysql_url(authority, port, database, username, password):
        return f'mysql+mysqlconnector://{username}:{password}@{authority}:{port}/{database}'

    @staticmethod
    def construct_in_memory_url():
        return 'sqlite:///'

    def __init__(self, url):
        self.engine = create_engine(url)
        self.Session = sessionmaker()
        self.Session.configure(bind=self.engine)

    def ensure_tables_exist(self):
        Persisted.metadata.create_all(self.engine)

    def create_session(self):
        return self.Session()
