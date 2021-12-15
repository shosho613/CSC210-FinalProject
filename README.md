# CSC210-FinalProject
A Fitness/Workout planner and tracker developed as a final project for CSC210.


profile should have:
- list of saved workouts
- basic statistics like number of times completed each workout, total weight lifted.

- create a workout:
- workout has the list of Exercises, title of workout, description.
dynamic form to add exercise entries
each exercise entry is:
* name of exercise
* number of sets
* number of reps
* target weight
* notes
* rest in between sets

save to db assoc with user logged in. 

view workout
loads a single workout in read only mode

edit workout "presses edit button" -> sends to create a workout screen with the workout loaded.