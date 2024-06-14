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
                if doc["user_id"] == user_doc["_id"] and doc["date"].year == date.year and doc[
                    "date"].month == date.month and doc["date"].day == date.day:
                    found = True
                    break
        else:
            msg = messagebox.showinfo("Warning", "Failed to find the username when checking if daily tasks existed!")
        client.close()
        return found

    def update_personalized_daily_tasks(self, uname, date, progresses):
        """
        The record may exist before (the user clicked into the daily tasks page), then delete it and insert a new one
        The record may not exist (the user hasn't clicked), then insert a new one
        :return:
        """
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        user_doc = users_col.find_one({"uname": uname})
        tasks_id = None
        if user_doc is not None:
            user_id = user_doc["_id"]
            daily_tasks_col = db[DAILY_TASKS_COLLECTION_NAME]
            for doc in daily_tasks_col.find():
                if doc["user_id"] == user_doc["_id"] and doc["date"].year == date.year and doc["date"].month == date.month and doc["date"].day == date.day:
                    tasks_id = doc["_id"]
                    break
            if tasks_id is not None:
                try:
                    print("Found old daily tasks!")
                    daily_tasks_col.delete_one({"_id": tasks_id})
                    print("Deleted the old daily tasks due to change of fitness goal and fitness level!")
                    daily_tasks_col.insert_one({
                        "user_id": user_id,
                        "date": date,
                        "progresses": progresses
                    })
                    print("Inserted new daily tasks due to change of fitness goal and fitness level!")
                except Exception as e:
                    print("Failed to update daily tasks!")
                    print(e)
            else:
                try:
                    print("Found no old daily tasks!")
                    daily_tasks_col.insert_one({
                        "user_id": user_id,
                        "date": date,
                        "progresses": progresses
                    })
                    print("Inserted new daily tasks due to change of fitness goal and fitness level!")
                except Exception as e:
                    print("Failed to update daily tasks!")
                    print(e)
        else:
            msg = messagebox.showinfo("Warning", "Failed to find the username while updating personalized daily tasks.")
        client.close()

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
