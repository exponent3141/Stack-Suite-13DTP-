from flask import Flask
from base import base
from auth import auth
from ctf import ctf
from tools import tools
from about import about
from info import info
from inventory import inventory
import dotenv
import os
from models.extensions import db, User
from flask_bootstrap import Bootstrap
import flask_login
from flask_login import current_user
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from base.base import error_404
dotenv.load_dotenv("../src/.env")

if "SECRET" not in os.environ:
    raise Exception("SECRET enviroment variable not found.")


class HomeView(AdminIndexView):
    """Admin view"""

    def is_accessible(self):
        """Checks that the user has administrator permissions"""
        try:
            # Returns true if user perms are 2, else false
            res = current_user.perms == 2
        except:
            # No perms, user is logged out
            res = False
        return res

    def inaccessible_callback(self, name, **kwargs):
        """
            Handle the response to inaccessible views.

            By default, it throw HTTP 403 error. 
            Now overidden to throw a HTTP 404 not found error.
            This is so that the website doesnt leak the admin route
        """
        return error_404("404")


app = Flask(__name__, static_folder="../static")
admin = Admin(app, base_template='layout.html',
              index_view=HomeView(name=' '), template_mode='bootstrap4')
login_manager = flask_login.LoginManager()

app.config["SECRET_KEY"] = os.environ["SECRET"]
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
bootstrap = Bootstrap(app)
db.init_app(app)

app.register_blueprint(base.blueprint)
app.register_blueprint(ctf.blueprint)
app.register_blueprint(auth.blueprint)
app.register_blueprint(tools.blueprint)
app.register_blueprint(info.blueprint)
app.register_blueprint(about.blueprint)
app.register_blueprint(inventory.blueprint)


class NEWModelView(ModelView):
    """Other admin pages"""

    def is_accessible(self):
        try:
            res = current_user.perms == 2
        except:
            res = False
        return res

    edit_template = 'editt.html'
    list_template = 'listt.html'
    create_template = 'creatt.html'


admin.add_view(NEWModelView(User, db.session))

login_manager.init_app(app)

login_manager.login_view = 'auth.authenticate'


@login_manager.user_loader
def load_user(user_id):
    """Returns user given a userid"""
    return User.query.get(int(user_id))


if __name__ == "__main__":

    app.run(debug=True)

    pass
