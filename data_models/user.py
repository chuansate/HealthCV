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



