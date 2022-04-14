import pymongo
from pymongo.errors import ConnectionFailure
import config

class Database(object):
    def __init__(self):
        self.mydb = self.openDB()
        self.books = self.openCollection(self.mydb)
    
    def openDB(self):
        global myclient
        myclient = pymongo.MongoClient ("mongodb://localhost:27017")
        try:
            myclient.admin.command ('ping')
        except ConnectionFailure:
            print ("Could not connect to MongoDB.")
            quit()
        else:
            # check if database already exists. If not, create new.
            try:
                dblist = myclient.list_database_names();
            except:
                print ("Could not open database.")
                quit()
            else:
                if "bookDatabase" in dblist:
                    print('The database already exists.')
                    mydb = myclient.get_database("bookDatabase")
                else:
                    print('Creating new database.')
                    mydb = myclient["bookDatabase"]
                return mydb

    def openCollection (self, mydb):
        # create books collection. (table)
        collist = mydb.list_collection_names()
        if "books" in collist:
            print("Books collection already exists.")
            books = mydb.get_collection("books")
        else:
            print('Creating books collection.')
            books = mydb["books"]
        config.books_coll = books
        return books
    
    def closeDB(self):
        myclient.close()
        print ("Database closed.")
