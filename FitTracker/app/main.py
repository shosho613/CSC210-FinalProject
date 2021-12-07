import json
from flask import Blueprint, render_template, url_for, redirect
from flask_login import login_required, current_user
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html', logout=False)
    

@main.route('/profile')
def profile():
    if current_user.is_authenticated:
        return render_template('profile.html', name=current_user.username)
    else:
        messages = json.dumps({"next" : url_for('main.profile')})

        return redirect(url_for('auth.login', messages=messages))