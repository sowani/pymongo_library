from opendb import Database
from gui import Gui
import config

# Open database and search for "book" collection
config.db = Database()
if ( config.db ):
    print ("Open database successful.")
else:
    print ("Failed to open database.")

Gui()
