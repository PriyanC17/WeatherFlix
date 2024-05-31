from datetime import datetime
from project import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# def add_column(engine, table_name, column):
#     column_name = column.compile(dialect=engine.dialect)
#     column_type = column.type.compile(engine.dialect)
#     engine.execute('ALTER TABLE %s ADD COLUMN %s %s ' %(table_name, column_name, column_type))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    # column = db.Column('city',db.String(100),nullable=False)
    # add_column(engine,user,column)
    # image_file = db.Column(db.String(20), nullable=False ,default='default.jpeg')

    password = db.Column(db.String(60), nullable=False)

    # posts = db.relationship('Post', backref='author', lazy=True)
    def __repr__(self):
        return f"User('{self.username}','{self.email}',{self.city})"
