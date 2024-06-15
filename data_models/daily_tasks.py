from .database_constants import HOST, DATABASE_NAME, USERS_COLLECTION_NAME, DAILY_TASKS_COLLECTION_NAME
import pymongo
from tkinter import messagebox


class DailyTasks:
    def __init__(self):
        pass

    def get_daily_tasks_progresses(self, uname, date):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        user_doc = users_col.find_one({"uname": uname})
        daily_tasks_doc = None
        if user_doc is not None:
            user_id = user_doc["_id"]
            daily_tasks_col = db[DAILY_TASKS_COLLECTION_NAME]
            for doc in daily_tasks_col.find():
                if doc["user_id"] == user_doc["_id"] and doc["date"].year == date.year and doc[
                    "date"].month == date.month and doc["date"].day == date.day:
                    daily_tasks_doc = doc
                    break
        else:
            msg = messagebox.showinfo("Warning", "Failed to find the username!")
        client.close()
        return daily_tasks_doc

    def daily_tasks_exist_on_date(self, uname, date):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        user_doc = users_col.find_one({"uname": uname})
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

    def update_biceps_curl_progress(self, uname, date, set_count, rep_count):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        user_doc = users_col.find_one({"uname": uname})
        tasks_id = None
        task_doc = None
        if user_doc is not None:
            user_id = user_doc["_id"]
            daily_tasks_col = db[DAILY_TASKS_COLLECTION_NAME]
            for doc in daily_tasks_col.find():
                if doc["user_id"] == user_doc["_id"] and doc["date"].year == date.year and doc["date"].month == date.month and doc["date"].day == date.day:
                    tasks_id = doc["_id"]
                    task_doc = doc
                    break
            if task_doc is not None:
                progresses = task_doc["progresses"]
                if set_count > progresses["Biceps curl"]["current_set"]:
                    progresses["Biceps curl"]["current_set"] = set_count
                if rep_count > progresses["Biceps curl"]["current_rep"]:
                    progresses["Biceps curl"]["current_rep"] = rep_count
                if progresses["Biceps curl"]["current_set"] >= progresses["Biceps curl"]["target_set"] and progresses["Biceps curl"]["current_rep"] >= progresses["Biceps curl"]["target_rep"]:
                    progresses["Biceps curl"]["done"] = True
                try:
                    daily_tasks_col.update_one({"_id": tasks_id}, {"$set": {"progresses": progresses}})
                except Exception as e:
                    msg = messagebox.showinfo("Warning",
                                              "Failed to update the progress of biceps curl in daily tasks!")
                    print(e)
            else:
                msg = messagebox.showinfo("Warning",
                                          "Failed to find the daily tasks when updating the progress of biceps curl in daily tasks!")
        else:
            msg = messagebox.showinfo("Warning", "Failed to find the username while updating personalized progress of kick-and-catch in daily tasks.")

        client.close()

    def update_kick_and_catch_progress(self, uname, date, fitness_goal, score, num_punch, num_kick):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        user_doc = users_col.find_one({"uname": uname})
        tasks_id = None
        task_doc = None
        if user_doc is not None:
            user_id = user_doc["_id"]
            daily_tasks_col = db[DAILY_TASKS_COLLECTION_NAME]
            for doc in daily_tasks_col.find():
                if doc["user_id"] == user_doc["_id"] and doc["date"].year == date.year and doc["date"].month == date.month and doc["date"].day == date.day:
                    tasks_id = doc["_id"]
                    task_doc = doc
                    break
            if tasks_id is not None:
                if fitness_goal == "Weight Loss":
                    progresses = task_doc["progresses"]
                    progresses["Kick-And-Catch"]["current_score"] += score
                    if progresses["Kick-And-Catch"]["current_score"] >= progresses["Kick-And-Catch"]["target_score"]:
                        progresses["Kick-And-Catch"]["done"] = True
                    daily_tasks_col.update_one({"_id": tasks_id}, {"$set": {"progresses": progresses}})
                elif fitness_goal == "Endurance":
                    progresses = task_doc["progresses"]
                    if score >= progresses["Kick-And-Catch"]["each_game_target_score"]:
                        progresses["Kick-And-Catch"]["num_match_done"] += 1
                    if progresses["Kick-And-Catch"]["num_match_done"] >= progresses["Kick-And-Catch"]["num_match"]:
                        progresses["Kick-And-Catch"]["done"] = True
                    daily_tasks_col.update_one({"_id": tasks_id}, {"$set": {"progresses": progresses}})
                elif fitness_goal == "Flexibility":
                    progresses = task_doc["progresses"]
                    progresses["Kick-And-Catch"]["current_punch"] += num_punch
                    progresses["Kick-And-Catch"]["current_kick"] += num_kick
                    if progresses["Kick-And-Catch"]["current_punch"] >= progresses["Kick-And-Catch"]["target_punch"] and progresses["Kick-And-Catch"]["current_kick"] >= progresses["Kick-And-Catch"]["target_kick"]:
                        progresses["Kick-And-Catch"]["done"] = True
                    daily_tasks_col.update_one({"_id": tasks_id}, {"$set": {"progresses": progresses}})
        else:
            msg = messagebox.showinfo("Warning", "Failed to find the username while updating personalized progress of kick-and-catch in daily tasks.")

        client.close()

    def update_yoga_imitation_progress(self, uname, date, score):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        user_doc = users_col.find_one({"uname": uname})
        tasks_id = None
        task_doc = None
        if user_doc is not None:
            user_id = user_doc["_id"]
            daily_tasks_col = db[DAILY_TASKS_COLLECTION_NAME]
            for doc in daily_tasks_col.find():
                if doc["user_id"] == user_doc["_id"] and doc["date"].year == date.year and doc["date"].month == date.month and doc["date"].day == date.day:
                    tasks_id = doc["_id"]
                    task_doc = doc
                    break
            if task_doc is not None:
                progresses = task_doc["progresses"]
                progresses["Yoga Imitation"]["current_score"] += score
                if progresses["Yoga Imitation"]["current_score"] >= progresses["Yoga Imitation"]["target_score"]:
                    progresses["Yoga Imitation"]["done"] = True
                daily_tasks_col.update_one({"_id": tasks_id}, {"$set": {"progresses": progresses}})
        else:
            msg = messagebox.showinfo("Warning", "Failed to find the username while updating personalized progress of kick-and-catch in daily tasks.")

        client.close()


    def update_feedback_by_task(self, uname, date, task_name, feedback):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        user_doc = users_col.find_one({"uname": uname})
        tasks_id = None
        task_doc = None
        if user_doc is not None:
            user_id = user_doc["_id"]
            daily_tasks_col = db[DAILY_TASKS_COLLECTION_NAME]
            for doc in daily_tasks_col.find():
                if doc["user_id"] == user_doc["_id"] and doc["date"].year == date.year and doc["date"].month == date.month and doc["date"].day == date.day:
                    tasks_id = doc["_id"]
                    task_doc = doc
                    break
            if task_doc is not None:
                new_progresses = task_doc["progresses"]
                new_progresses[task_name]["feedback"] = feedback
                try:
                    daily_tasks_col.update_one({"_id": tasks_id}, {"$set": {"progresses": new_progresses}})
                    msg = messagebox.showinfo("Information", "Updated the feedback!")
                except Exception as e:
                    msg = messagebox.showinfo("Warning",
                                              "Failed to update the feedback, try again!")
                    print(e)
        else:
            msg = messagebox.showinfo("Warning", "Failed to find the username while updating personalized progress of kick-and-catch in daily tasks.")

        client.close()

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
