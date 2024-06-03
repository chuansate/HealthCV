from .database_constants import HOST, DATABASE_NAME, USERS_COLLECTION_NAME, \
     WORKOUT_EXERCISE_COLLECTION_NAME, BicepsCurlRecord_COLLECTION_NAME
import pymongo


class BicepsCurlRecord:
    def __init__(self):
        pass

    def create_new_workout_record(self, uname, set_count, rep_count, complete_duration, datetime):
        print("Saving new match record in the backend for biceps curl record...")
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        user_query = {"uname": uname}
        user_doc = users_col.find_one(user_query)
        bicepscurl_recs_col = db[BicepsCurlRecord_COLLECTION_NAME]
        if user_doc is not None:
            bicepscurl_recs_col.insert_one({
                "user_id": user_doc["_id"],
                "set_count": set_count,
                "rep_count": rep_count,
                "complete_duration": complete_duration,
                "datetime": datetime
            })
            print("Finished saving new biceps curl record!")
        else:
            print("Username is not found when creating a biceps curl record!")
        client.close()

    def get_workout_exercise_id(self):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        workout_exercise_col = db[WORKOUT_EXERCISE_COLLECTION_NAME]
        query = {"exercise_name": "Biceps curl"}
        exercise_id = workout_exercise_col.find_one(query)["_id"]
        client.close()
        return exercise_id