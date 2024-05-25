# Import the required module for text
# to speech conversion
from gtts import gTTS

# This module is imported so that we can
# play the converted audio
#
# The text that you want to convert to audio
mytext = 'Step 3, go up while maintaining a straight body.'
path = "./audio/push_up_step3.mp3"
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

##############
# import pymongo
#
# myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#
# mydb = myclient["HealthCV"]
#
# dblist = myclient.list_database_names()
# print("Existing databases = ", dblist)
# print("Existing collections in HealthCV database = ", mydb.list_collection_names())
# if "HealthCV" in dblist:
#     print("The database exists.")
#
# users_collection = mydb["users"]
#
# for rec in users_collection.find():
#     print(rec)

# record = { "uname": "Lim", "pwd": "Lim123" }
#
# x = users_collection.insert_one(record)
# print("The record with id " + str(x.inserted_id) + " just got inserted!")
