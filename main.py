import json
import datetime
import pandas as pd
from flask import Blueprint, render_template, url_for, redirect, flash, request
from flask.wrappers import Response
from flask_login import login_required, current_user
from app import db
from forms import ExerciseForm, WorkoutForm
from models import User, Exercise, Workout, FinishedWorkout, FinishedExercise

main = Blueprint('main', __name__)

#### HELPER FUNCTIONS #####

def add_workout_exercise(workout_id):
    exercise = Exercise(name="", associated_workout=workout_id)
    db.session.add(exercise)
    db.session.flush()
    db.session.commit()
    



def delete_workout(workout_id):
    Workout.query.filter_by(id=workout_id).delete()
    Exercise.query.filter_by(associated_workout=workout_id).delete()
    db.session.commit()

def delete_finished_workout(id):
    FinishedWorkout.query.filter_by(id=id).delete()
    FinishedExercise.query.filter_by(finished_workout_id=id).delete()
    db.session.commit()



def add_workout(form, id=None):
    user_id = current_user.id
    db_workout = Workout(name=form.workout_name.data, description=form.description.data, user=user_id)
    if id:
        db_workout.id = id
    db.session.add(db_workout)
    db.session.flush()
    db.session.refresh(db_workout)

    for exercise in form.exercises:
        notes = exercise.notes.data if exercise.notes.data else ""
        db_exercise = Exercise(name=exercise.exercise_name.data, num_sets=exercise.num_sets.data, num_reps=exercise.num_reps.data, 
                                weight=exercise.intended_weight.data, associated_workout=db_workout.id, notes=notes) 
        db.session.add(db_exercise)
    db.session.commit()

def increment_form(form):
    form.set_num_entries(len(form.exercises) + 1)
    print(len(form.exercises))
    return render_template('workout_creator.html', form=form)

def populate_form(form, workout, exercises):
    print(f"In populate form: {workout}")
    form = WorkoutForm(workout_name=workout.name, description=workout.description)
    for exercise in exercises:
        ex_form = ExerciseForm()
        ex_form.exercise_name = exercise.name
        ex_form.num_sets = exercise.num_sets
        ex_form.num_reps = exercise.num_reps
        ex_form.intended_weight = exercise.weight
        ex_form.notes = exercise.notes
        form.add_exercise(ex_form)
    return form

def time_avg(times):
    total_mins = 0
    total_seconds = 0
    for t in times:
        total_mins += t.minute
        total_seconds += t.second
    total = total_mins * 60 + total_seconds
    return total/len(times)


def produce_analysis(finished_workouts):
    avg_workout_time = None
    avg_pounds_lifted = 0

    durations = []
    lbs_lifted = []
    completed_workout_names = []
    completed_workouts = dict()
    for workout in finished_workouts:
        completed_workout_names.append(workout.name)
        durations.append(workout.duration)

    for i in completed_workout_names:
        if i in completed_workouts:
            completed_workouts[i] += 1
        else:
            completed_workouts[i] = 1
    print(completed_workouts)
        # exercises:
    finished_exercises = FinishedExercise.query.filter_by(finished_workout_id=workout.id).all()
    total_weight = 0
    for exercise in finished_exercises:
        if str(exercise.completed_sets) != '':
            comp_sets = json.loads(str(exercise.completed_sets))
            for s in comp_sets:
                total_weight += int(s['weight']) * int(s['num_reps'])
            if total_weight != 0:
                lbs_lifted.append(total_weight)
    
    # number of times each workout was completed
    avg_pounds_lifted = sum(lbs_lifted)/len(lbs_lifted)
    avg_workout_time = time_avg(durations)
    avg_workout_time = pd.Timedelta(datetime.timedelta(seconds=avg_workout_time)).round('1s')

    
    return round(avg_pounds_lifted,2), str(avg_workout_time)[7:], completed_workouts

###############
@main.route('/')
def index():
    logout = bool(request.args.get('logout', False))
    print(logout)
    return render_template('index.html', logout=logout)
    

@main.route('/profile')
def profile():
    if current_user.is_authenticated:
        # get workouts associated with user.
        workouts = Workout.query.filter_by(user=current_user.id).all()
        
        finished_workouts = FinishedWorkout.query.filter(db.or_(FinishedWorkout.workout_id == w.id for w in workouts)).all()
        avg_pounds_lifted, avg_workout_time, completed_workouts = produce_analysis(finished_workouts)
        return render_template('profile.html', name=current_user.username, workouts=workouts, 
        finished_workouts=reversed(finished_workouts), avg_pounds_lifted=avg_pounds_lifted, 
        avg_workout_time=avg_workout_time, completed_workouts=completed_workouts)
    else:
        messages = json.dumps({"next" : url_for('main.profile')})

        return redirect(url_for('auth.login', messages=messages))


# must be get for href to work
@main.route('/workout/delete', methods=['GET'])
def deleteworkout():
    workout_id = request.args['workout_id']
    delete_workout(workout_id)
    return redirect(url_for('main.profile'))

@main.route('/workout/finished/delete', methods=['GET'])
def deletefinishedworkout():
    finished_workout_id = request.args['finished_workout_id']
    delete_finished_workout(finished_workout_id)
    return redirect(url_for('main.profile'))

@main.route('/workout/edit', methods=['GET', 'POST'])
def editworkout():
    workout_id = request.args['workout_id']
    form = WorkoutForm()
    if form.validate_on_submit():
        delete_workout(workout_id)
        add_workout(form, workout_id)
        return redirect(url_for('main.profile'))
    workout = Workout.query.filter_by(id=workout_id).first()
    exercises = Exercise.query.filter_by(associated_workout=workout_id).all()
    print(f"In editworkout: {workout}")
    form = populate_form(form, workout, exercises)
    return render_template('workout_creator.html', form=form)

@main.route('/workout/create', methods=['GET', 'POST'])
def createworkout():
    form = WorkoutForm()
    form.set_num_entries(5) 
    if form.validate_on_submit():
        existing_workout = Workout.query.filter_by(name=form.workout_name.data).first()
        if existing_workout is not None:
            flash("Cannot create workout with identical name")
            return render_template('workout_creator.html', form=form)
        add_workout(form)
        return redirect(url_for('main.profile'))
    return render_template('workout_creator.html', form=form)


# @main.route('/addExercise', methods=['GET', 'POST'])
# def add_exercise():
#     workout_id = request.args['workout_id']

#     add_workout_exercise(workout_id)
#     return redirect(url_for('main.editworkout', workout_id=workout_id))


@main.route('/workout/start', methods=['GET', 'POST'])
def startworkout():
    workout_id = request.args['workout_id']
    workout = Workout.query.filter_by(id=workout_id).first()
    exercises = Exercise.query.filter_by(associated_workout=workout_id).all()
    exercises_dictlist = []
    for exercise in exercises:
        exercises_dictlist.append(exercise.to_dict())
    return render_template('workout_checklist.html', workout=workout, exercises=exercises, workout_dict=workout.to_dict(), exercises_dict=exercises_dictlist)


@main.route('/workout/finish', methods=['GET', 'POST'])
def finishworkout():
    data = json.loads(request.data)
    # create FinishedWorkout entry
    name = data['name']
    description = data['description']
    workout_id = data['id']
    duration = datetime.time(minute=int(data['time_taken']['minutes']), 
    second=int(data['time_taken']['seconds']))

    finished_workout = FinishedWorkout(name=name, description=description, 
    workout_id=workout_id, duration=duration)
    db.session.add(finished_workout)
    db.session.flush()
    db.session.refresh(finished_workout)

    fin_workout_id = finished_workout.id
    # create finished exercise
    for exercise in data['exercises']:
        name = exercise['name']
        notes = exercise['notes']
        exercise_id = exercise['id']
        completed_sets = exercise['completed_sets']
        if len(completed_sets) == 0:
            finished_exercise = FinishedExercise(name=name, completed_sets="", notes=notes,
             exercise_id=exercise_id, finished_workout_id=fin_workout_id)
            db.session.add(finished_exercise)
        else:
            finished_exercise = FinishedExercise(name=name, completed_sets=json.dumps(completed_sets), notes=notes,
             exercise_id=exercise_id, finished_workout_id=fin_workout_id)
            db.session.add(finished_exercise)
    
    db.session.commit()
    
    return Response(status=200)


