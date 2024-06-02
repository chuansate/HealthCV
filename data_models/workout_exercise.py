from .database_constants import HOST, DATABASE_NAME, WORKOUT_EXERCISE_COLLECTION_NAME
import pymongo


class WorkoutExercise:
    def __init__(self):
        pass

    def create_new_exercise(self, exercise_name, description):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        workout_exercise_col = db[WORKOUT_EXERCISE_COLLECTION_NAME]
        workout_exercise_col.insert_one({
            "exercise_name": exercise_name,
            "description": description
        })
        client.close()
