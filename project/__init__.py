from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
db = SQLAlchemy()
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Your API Key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'ite.db'
    db.init_app(app)
    # bcrypt = Bcrypt(app)

    with app.app_context():
        db.create_all()

    return app


app = create_app()
login_manager = LoginManager(app)
# if user is not logged in and tries to access the account page
# then it redirects to login page using this login_view
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

import project.routes
