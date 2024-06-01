from .database_constants import HOST, DATABASE_NAME, GAMES_COLLECTION_NAME
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





