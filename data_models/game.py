from .database_constants import HOST, DATABASE_NAME, GAMES_COLLECTION_NAME, USERS_COLLECTION_NAME
import pymongo


class Game:
    def __init__(self):
        pass

    def create_new_game(self, game_name, description):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        games_col = db[GAMES_COLLECTION_NAME]
        games_col.insert_one({
            "game_name": game_name,
            "description": description
        })
        client.close()

    def get_all_games_ids_names(self):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        games_col = db[GAMES_COLLECTION_NAME]
        rows = []
        for rec in games_col.find({}, {"game_name": 1}):
            rows.append(rec)
        client.close()
        return rows

    def get_best_records_by_each_user(self):
        """

        :return: best_records_by_each_user: keys are game IDs in string, values are lists of tuples (player_name, score)
        """
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        games_col = db[GAMES_COLLECTION_NAME]
        best_records_by_each_user = {}
        games_ids_strs = []
        for rec in games_col.find({}, {"_id": 1, "game_name": 0, "description": 0}):
            best_records_by_each_user[str(rec["_id"])] = []
            games_ids_strs.append(str(rec["_id"]))
        for row in users_col.find():
            for id_str in games_ids_strs:
                score = row["best_records"][id_str]
                best_records_by_each_user[id_str].append((row["uname"], score))
        client.close()
        return best_records_by_each_user




