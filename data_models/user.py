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

    def save_profile_page(self, uname, new_fitness_goal, new_fitness_level):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        query = {"uname": uname}
        try:
            users_col.update_one(query, {"$set": {"fitness_goal": new_fitness_goal, "fitness_level": new_fitness_level}})
        except Exception as e:
            print(e)
            raise UserWarning("Failed to update profile!")
        client.close()

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
            "best_records": best_records,
            "XP": None,
            "fitness_goal": None,
            "fitness_level": None
        })
        client.close()

    def add_XP_to_user(self, uname, XP_increment):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        users_col.update_one(
            {"uname": uname},
            {"$inc": {"XP": XP_increment}}
        )
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

    def user_hasnt_filled_in_details(self, uname):
        """
        Check the collection `users` to see if the fitness goal and fitness level are still NULL
        :return:
        """
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        user_doc = users_col.find_one({"uname": uname})
        flag = False
        if user_doc is not None:
            if user_doc["XP"] is None and user_doc["fitness_goal"] is None and user_doc["fitness_level"] is None:
                flag = True
        else:
            raise Exception("The username couldn't been found!")
        client.close()
        return flag

    def filling_in_fitness_goal_and_level(self, uname, fitness_goal, fitness_level):
        """
        Check the collection `users` to see if the fitness goal and fitness level are still NULL
        :return:
        """
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        new_values = {"$set": {"XP": 0, "fitness_goal": fitness_goal, "fitness_level": fitness_level}}
        users_col.update_one({"uname": uname}, new_values)
        client.close()



