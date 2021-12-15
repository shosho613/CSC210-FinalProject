from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

import os
# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
app = Flask(__name__)
login = LoginManager(app)

app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

db.init_app(app)
# init db
if not os.path.isfile("db.sqlite"):
    from models import *
    db.create_all(app=app)
# blueprint for auth routes in our app
from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

# blueprint for non-auth parts of app
from main import main as main_blueprint
app.register_blueprint(main_blueprint)
migrate = Migrate(app, db)
login.login_view = 'login'

if __name__ == '__main__':
    app.run(threaded=True, port=5000)