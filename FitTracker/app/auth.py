from flask import Blueprint, render_template, url_for
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
import json

from . import db
from app.forms import LoginForm, RegistrationForm
from app.models import User


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login(messages=None):
    if current_user.is_authenticated:
        return redirect(url_for('main.profile'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.profile'))
    return render_template('login.html', title='Log In', form=form)


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('signup.html', title='signup', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return render_template('index.html', logout=True)