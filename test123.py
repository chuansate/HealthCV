# Import the required module for text
# to speech conversion
# from gtts import gTTS
#
# # This module is imported so that we can
# # play the converted audio
# #
# # The text that you want to convert to audio
# mytext = 'Body not straight'
# path = "./audio/body_not_straight.mp3"
# # Language in which you want to convert
# language = 'en'
#
# # Passing the text and language to the engine,
# # here we have marked slow=False. Which tells
# # the module that the converted audio should
# # have a high speed
# myobj = gTTS(text=mytext, lang=language, slow=False)
#
# # Saving the converted audio in a mp3 file named
# # welcome
#
# myobj.save(path)
# import playsound
# playsound.playsound(path)
#
import numpy as np
from scipy.stats import pearsonr

a=[1, 2, 3]

# input array 2
b=[1, 2, 3]

corr, _ = pearsonr(a, b)
print('Pearsons correlation: %.6f' % corr)
print(abs(int(corr)))

print(10.1 % 3)
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
