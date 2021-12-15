from flask.app import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FormField, FieldList, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already exists. Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email Address already exists. Please use a different email address.')

class ExerciseForm(FlaskForm):
    exercise_name = StringField('Exercise Name', validators=[DataRequired()])
    num_sets = IntegerField('Number of Sets', validators=[DataRequired()])
    num_reps = IntegerField('Number of Reps', validators=[DataRequired()])
    intended_weight = IntegerField('Weight')
    notes = StringField('Notes')


class WorkoutForm(FlaskForm):
    workout_name = StringField('Workout Name', validators=[DataRequired()])
    description = StringField('Description')
    exercises = FieldList(FormField(ExerciseForm), min_entries = 0)
    submit = SubmitField('Save Workout')

    def set_num_entries(self, num):
        if len(self.exercises) < num:
            for i in range(num-len(self.exercises)):
                self.exercises.append_entry(FormField(ExerciseForm()))

    def add_exercise(self, exercise_form):
        self.exercises.append_entry(exercise_form)


class ForgotPasswordForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Email To Reset Password')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


