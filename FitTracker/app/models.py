from . import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Exercise(db.Model):
    __tablename__ = 'exercise'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=False)
    num_sets = db.Column(db.Integer, index=True)
    num_reps = db.Column(db.Integer, index=True)
    weight = db.Column(db.Integer)
    notes = db.Column(db.String(64))
    associated_workout = db.Column(db.Integer, db.ForeignKey('workout.id'))

    def __repr__(self):
        return f'<Exercise {self.name} {self.num_sets} {self.num_reps} {self.weight} {self.associated_workout}>'

    def to_dict(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'num_sets' : self.num_sets,
            'num_reps' : self.num_reps,
            'weight' : self.weight,
            'notes' : self.notes,
            'associated_workout' : self.associated_workout
        }

class Workout(db.Model):
    __tablename__ = 'workout'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    description = db.Column(db.String(1024))
    user = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Workout {self.name} {self.id} {self.description} {self.user}>'

    def to_dict(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'description' : self.description,
            'user' : self.user,
        }

class FinishedWorkout(db.Model):
    __tablename__ = 'finishedworkout'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    description = db.Column(db.String(1024))
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'))
    duration = db.Column(db.Time)
    

class FinishedExercise(db.Model):
    __tablename__ = 'finishedexercise'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=False)
    completed_sets = db.Column(db.Text()) # a json array such that every entry is {weight: weight_done, num_reps: reps_done}
    notes = db.Column(db.String(64))
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'))
    finished_workout_id = db.Column(db.Integer, db.ForeignKey('finishedworkout.id'))

    


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


