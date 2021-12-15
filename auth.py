from flask import Blueprint, render_template, url_for, flash, redirect
from flask_login import login_user, logout_user, current_user, login_required
import json
import random
import os
from ff3 import FF3Cipher
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app import db

from forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm
from models import User


auth = Blueprint('auth', __name__)
key = "EF4359D8D580AA4F7F036D6F04FC6A94"
tweak = "D8E7920AFA330A73"
c = FF3Cipher.withCustomAlphabet(key, tweak, "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+0123456789.@")
os.environ['EMAIL'] = 'fittracker.csc210@gmail.com'
os.environ['PASS'] = 'csc210finalproject'
## HELPER FUNCTIONS ###
def send_email(user_email, content):
    message = MIMEMultipart()
    message["From"] = os.environ['EMAIL']
    message["To"] = user_email
    message["Subject"] = "FitTracker Reset Password"
    message.attach(MIMEText(content, "plain"))

    text = message.as_string()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(os.environ['EMAIL'], os.environ['PASS'])
        server.sendmail(os.environ['EMAIL'], user_email, text)
    
############


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
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('signup.html', title='signup', form=form)

@auth.route('/forgot', methods=['GET', 'POST'])
def forgot_pass():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data, username=form.username.data).first()
        if user is None:
            flash("No such user exists. Create a new account.")
        else:
            hashed_email = c.encrypt(f"{user.email}") 
            hashed_username = c.encrypt(f"{user.username}")
            hashed_salt = c.encrypt(f"{random.randint(0,100) * random.randint(0,100)}")
            hashed_userinfo = f"{hashed_email}+{hashed_username}+{hashed_salt}"
            absolute_url = url_for('auth.reset_password', token=hashed_userinfo, _external=True)
            send_email(user.email, absolute_url)
            flash("Successfully sent email to reset your password.")
            
    return render_template('forgot_password.html', form=form)

  
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm()
    vals = token.split("+")
    print(c.decrypt(vals[0]))
    user = User.query.filter_by(email=c.decrypt(vals[0]), username=c.decrypt(vals[1])).first() 
    if user is not None and form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you successfuly changed your password!')
        return redirect(url_for('auth.login'))
    if user is not None:
        return render_template('reset_password.html', form=form)
    else:
        # show invalid page.
        return render_template('invalid.html')

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("main.index", logout="True"))