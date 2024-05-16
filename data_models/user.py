from .database_constants import HOST, DATABASE_NAME, USERS_COLLECTION_NAME
import pymongo


class User:
    def __init__(self, uname, pwd):
        self.__uname = uname
        self.__pwd = pwd

    def search_by_uname(self):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        query = {"uname": self.__uname}
        found_doc = users_col.find_one(query)
        client.close()
        return found_doc

    def create_new_user(self):
        client = pymongo.MongoClient(HOST)
        db = client[DATABASE_NAME]
        users_col = db[USERS_COLLECTION_NAME]
        users_col.insert_one({
            "uname": self.__uname,
            "pwd": self.__pwd
        })
        client.close()

    def get_uname(self):
        return self.__uname

    def set_uname(self, uname):
        if type(uname) != str:
            raise TypeError("The username must be of string type!")
        self.__uname = uname

    def get_pwd(self):
        return self.__pwd

    def set_pwd(self, pwd):
        if type(pwd) != str:
            raise TypeError("The password must be of string type!")
        self.__pwd = pwd

