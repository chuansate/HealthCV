import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["HealthCV"]

dblist = myclient.list_database_names()
print("Existing databases = ", dblist)
print("Existing collections in HealthCV database = ", mydb.list_collection_names())
if "HealthCV" in dblist:
    print("The database exists.")

users_collection = mydb["users"]


record = { "uname": "Lim", "pwd": "Lim123" }

x = users_collection.insert_one(record)
print("The record with id " + str(x.inserted_id) + " just got inserted!")
