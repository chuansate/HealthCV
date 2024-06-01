from .database_constants import HOST, DATABASE_NAME, USERS_COLLECTION_NAME, GAMES_COLLECTION_NAME
import pymongo


class User:
    def __init__(self):
        pass

    def search_by_uname(self, uname):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        query = {"uname": uname}
        found_doc = users_col.find_one(query)
        client.close()
        return found_doc

    def create_new_user(self, uname, pwd, acc_created_time):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        games_col = db[GAMES_COLLECTION_NAME]
        best_records = {}
        for game in games_col.find():
            best_records[str(game["_id"])] = 0
        users_col.insert_one({
            "uname": uname,
            "pwd": pwd,
            "created_time": acc_created_time,
            "best_records": best_records
        })
        client.close()

    def get_best_record(self, uname, game_name):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        user_query = {"uname": uname}
        game_query = {"game_name": game_name}
        users_col = db[USERS_COLLECTION_NAME]
        games_col = db[GAMES_COLLECTION_NAME]
        game_doc = games_col.find_one(game_query)
        user_doc = users_col.find_one(user_query)
        best_record = None
        if game_doc is not None and user_doc is not None:
            game_id = game_doc["_id"]
            best_record = user_doc["best_records"][str(game_id)]

        client.close()
        return best_record



