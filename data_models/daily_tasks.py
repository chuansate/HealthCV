from .database_constants import HOST, DATABASE_NAME, USERS_COLLECTION_NAME, DAILY_TASKS_COLLECTION_NAME
import pymongo
from tkinter import messagebox


class DailyTasks:
    def __init__(self):
        pass

    def daily_tasks_exist_on_date(self, uname, date):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        user_doc = users_col.find_one({"uname": uname})
        burned_calories = None
        found = False
        if user_doc is not None:
            user_id = user_doc["_id"]
            daily_tasks_col = db[DAILY_TASKS_COLLECTION_NAME]
            for doc in daily_tasks_col.find():
                if doc["user_id"] == user_doc["_id"] and doc["date"].year == date.year and doc["date"].month == date.month and doc["date"].day == date.day:
                    found = True
                    break
        else:
            msg = messagebox.showinfo("Warning", "Failed to find the username.")
        client.close()
        return found

    def create_daily_tasks(self, uname, date, progresses):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        daily_tasks_col = db[DAILY_TASKS_COLLECTION_NAME]
        user_doc = users_col.find_one({"uname": uname})
        if user_doc is not None:
            user_id = user_doc["_id"]
            daily_tasks_col.insert_one({
                "user_id": user_id,
                "date": date,
                "progresses": progresses
            })
        else:
            msg = messagebox.showinfo("Warning", "Failed to find the username.")
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