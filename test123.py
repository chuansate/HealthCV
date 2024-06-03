# Import the required module for text
# to speech conversion
def text_to_speech():
    from gtts import gTTS

    # This module is imported so that we can
    # play the converted audio
    #
    # The text that you want to convert to audio
    mytext = 'Congratulation, you have learned how to do push-up!'
    path = "./audio/congrats_pushup.mp3"
    # Language in which you want to convert
    language = 'en'

    # Passing the text and language to the engine,
    # here we have marked slow=False. Which tells
    # the module that the converted audio should
    # have a high speed
    myobj = gTTS(text=mytext, lang=language, slow=False)

    # Saving the converted audio in a mp3 file named
    # welcome

    myobj.save(path)
    import playsound
    playsound.playsound(path)
#
##############
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["HealthCV"]

dblist = myclient.list_database_names()
print("Existing databases = ", dblist)
print("Existing collections in HealthCV database = ", mydb.list_collection_names())
if "HealthCV" in dblist:
    print("The database exists.")


def print_users_collection():
    print("Printing collection `users`:")
    collection = mydb["users"]
    for x in collection.find():
        print(x)

def print_games_collection():
    print("Printing collection `games`:")
    collection = mydb["games"]
    for x in collection.find():
        print(x)

def print_workout_exercise_collection():
    print("Printing collection `workout_exercise`:")
    collection = mydb["workout_exercise"]
    for x in collection.find():
        print(x)

def print_pushup_recs_collection():
    print("Printing collection `push_up_records`:")
    collection = mydb["push_up_records"]
    for x in collection.find():
        print(x)

def print_bicepscurl_recs_collection():
    print("Printing collection `biceps_curl_records`:")
    collection = mydb["biceps_curl_records"]
    for x in collection.find():
        print(x)


def print_kick_and_catch_match_recs_collection():
    print("Printing collection `kick_and_catch_match_records`:")
    collection = mydb["kick_and_catch_match_records"]
    for x in collection.find():
        print(x)

def print_yoga_estimation_match_recs_collection():
    print("Printing collection `yoga_imitation_match_records`:")
    collection = mydb["yoga_imitation_match_records"]
    for x in collection.find():
        print(x)

def print_StackOverflow_collection():
    print("Printing collection `StackOverflow`:")
    collection = mydb.StackOverflow
    for x in collection.find():
        print(x)


def delete_StackOverflow_collection():
    collection = mydb.StackOverflow
    collection.delete_many({})


# THIS IS WORKING!!
def update_nested_docs_simple_criteria():
    collection = mydb.StackOverflow   #collection name= StackOverflow
    record = {
        "uname" : "value1",
        "pwd" : "value2",
        "created_time": "value3",
        "best_records": {
            "game_id1": 0,
            "game_id2": 100
        }
    }
    collection.insert_one(record)
    for data in collection.find():
        print("Inserted Data=", data)
    best_records = collection.find_one({"uname": "value1"})["best_records"]
    best_records["game_id1"] = -99
    collection.update_one(
        {"uname": "value1"},
        {"$set":{"best_records" : best_records}}
    )

print_users_collection()
# print_games_collection()
# print_yoga_estimation_match_recs_collection()
print_workout_exercise_collection()
print_pushup_recs_collection()
print_bicepscurl_recs_collection()

