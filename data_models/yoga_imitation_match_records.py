from .database_constants import HOST, DATABASE_NAME, GAMES_COLLECTION_NAME, USERS_COLLECTION_NAME, \
    YogaImitation_COLLECTION_NAME
import pymongo


class YogaImitationMatchRecord:
    def __init__(self):
        pass

    def create_new_match_record(self, uname, score, datetime):
        print("Saving new match record in the backend for yoga imitation game...")
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        user_query = {"uname": uname}
        user_doc = users_col.find_one(user_query)
        yoga_match_recs_col = db[YogaImitation_COLLECTION_NAME]
        if user_doc is not None:
            yoga_match_recs_col.insert_one({
                "user_id": user_doc["_id"],
                "score": score,
                "datetime": datetime
            })
            if score > user_doc["best_records"][str(self.get_game_id())]:
                self.update_best_record(uname, score)
            print("Finished saving new match record for yoga imitation!")
        else:
            print("Username is not found when creating a new match record for yoga imitation!")
        client.close()

    def update_best_record(self, uname, best_score):
        print("Updating best records in backend for yoga imitation game, modifying collection `users`...")
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        best_records = users_col.find_one({"uname": uname})["best_records"]
        best_records[str(self.get_game_id())] = best_score
        users_col.update_one(
            {"uname": uname},
            {"$set": {"best_records": best_records}}
        )
        print("Finished updating best record!")
        client.close()

    def get_game_id(self):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        games_col = db[GAMES_COLLECTION_NAME]
        query = {"game_name": "Yoga Imitation"}
        game_id = games_col.find_one(query)["_id"]
        client.close()
        return game_id
