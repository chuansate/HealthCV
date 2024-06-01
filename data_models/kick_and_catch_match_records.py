from .database_constants import HOST, DATABASE_NAME, GAMES_COLLECTION_NAME, USERS_COLLECTION_NAME, \
    KickAndCatchMatchRecord_COLLECTION_NAME
import pymongo


class KickAndCatchMatchRecord:
    def __init__(self):
        pass

    def create_new_match_record(self, uname, score, datetime):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        user_query = {"uname": uname}
        user_doc = users_col.find_one(user_query)
        kcamr_col = db[KickAndCatchMatchRecord_COLLECTION_NAME]
        if user_doc is not None:
            kcamr_col.insert_one({
                "user_id": user_doc["_id"],
                "score": score,
                "datetime": datetime
            })
            if score > user_doc["best_records"][str(self.get_game_id())]:
                self.update_best_record(uname, score)
        else:
            print("Username is not found when creating a new match record for kick-and-catch!")
        client.close()

    def update_best_record(self, uname, score):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        myquery = {"uname": uname}
        newvalues = {"$set": {"best_records": "Canyon 123"}}

        # Pymongo updating nested dictionaries
        # Go to test123.py, that one is the modified version!
        # https://stackoverflow.com/questions/30782373/updating-nested-document-in-mongodb-using-pymongo
        if user_doc is not None:

        else:
            print("Username is not found when creating a new match record for kick-and-catch!")
        client.close()

    def get_game_id(self):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        games_col = db[GAMES_COLLECTION_NAME]
        query = {"game_name": "Kick-And-Catch"}
        game_id = games_col.find_one(query)["_id"]
        client.close()
        return game_id
