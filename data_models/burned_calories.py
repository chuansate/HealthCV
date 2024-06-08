from tkinter import messagebox

from .database_constants import HOST, DATABASE_NAME, USERS_COLLECTION_NAME, BURNED_CALORIES_COLLECTION_NAME
import pymongo


class BurnedCalories:
    def __init__(self):
        pass

    def get_burned_calories_by_date(self, uname, date):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        user_doc = users_col.find_one({"uname": uname})
        burned_calories = None
        if user_doc is not None:
            bc_col = db[BURNED_CALORIES_COLLECTION_NAME]
            found = False
            for doc in bc_col.find():
                if doc["user_id"] == user_doc["_id"] and doc["date"].year == date.year and doc["date"].month == date.month and doc["date"].day == date.day:
                    found = True
                    burned_calories = doc["amount"]
                    break
            if not found:
                burned_calories = 0
        else:
            msg = messagebox.showinfo("Warning", "Failed to find the username.")

        client.close()
        return burned_calories

    def update_burned_calories_by_date(self, uname, amount, date):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        user_doc = users_col.find_one({"uname": uname})
        if user_doc is not None:
            bc_col = db[BURNED_CALORIES_COLLECTION_NAME]
            found = False  # to see if the same user has recorded burned calories on the same day
            current_burned_calories = None
            bc_doc_id = None
            for doc in bc_col.find():
                if doc["user_id"] == user_doc["_id"] and doc["date"].year == date.year and doc["date"].month == date.month and doc["date"].day == date.day:
                    found = True
                    current_burned_calories = doc["amount"]
                    bc_doc_id = doc["_id"]
                    break

            if found:
                current_burned_calories += amount
                try:
                    bc_col.update_one({"_id": bc_doc_id}, {"$set": {"amount": current_burned_calories}})
                except Exception as e:
                    msg = messagebox.showinfo("Warning", "Failed to update.")
                    print(e)
            else:
                try:
                    bc_col.insert_one({"user_id": user_doc["_id"], "amount": amount, "date": date})
                except Exception as e:
                    msg = messagebox.showinfo("Warning", "Failed to insert.")
                    print(e)

        else:
            msg = messagebox.showinfo("Warning", "Failed to find the username.")

        client.close()
