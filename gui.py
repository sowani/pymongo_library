from tkinter import *
from tkinter import ttk
import tkinter as tk
#import atexit
import pymongo
import config

debug = 0

def popUpWarning (ptext):
    pwin = tk.Toplevel()
    pwin.wm_title("Warning!")
    mwidth = len (ptext) + 2
    ttk.Label (pwin, text=ptext, width=mwidth, anchor="center").grid (column=0, row=0, sticky=(W, E))
    pbutton = ttk.Button (pwin, text="OK", width=4, command=pwin.destroy)
    pbutton.grid(column=0, row=1, pady=2)

def popUpWindow(booklist):
    pwin = tk.Toplevel()
    pwin.wm_title("Search result")
    # Add book names and author names here.
    rnum = 0
    for i in booklist:
        ttk.Label (pwin, text=rnum+1, width=3, anchor="center").grid (column=0, row=rnum, sticky=(W, E))
        ttk.Label (pwin, text=i['book_name'], width=40).grid (column=1, row=rnum, sticky=(W, E))
        rnum = rnum + 1
    pbutton = ttk.Button (pwin, text="OK", command=pwin.destroy)
    pbutton.grid(column=0, row=rnum, pady=2, columnspan=2, sticky=(W, E))

def checkSpecial (name):
    regex = re.compile ('[$^%*?]')
    if (regex.search (name) == None):
        return False
    else:
        return True

def add_book (db, book):
    if (debug):
        print ("adding book ", book)
    
    if (checkSpecial (book["book_name"]) == False):
        #try:
        x, _ = search_book(db, book)
        if (debug):
            print (x)
        
        if (x != None):
            if ( x == "nonexistent" ):
                # check for special characters and then add.
                _ = db.books.insert_one( book )
            else:
                popUpWarning("Book entry already exists.")
        else:
            if (debug):
                print ("Book entry already exists.")
            pass
        #except pymongo.errors.DuplicateKeyError:
        #    print ("Book already exists.")
    else:
        popUpWarning ("Error: Book name contains special character(s).")

def search_book (db, book, silent = 1):
    if (debug):
        print ("searching book ", book)
    
    keys = list (book.keys())
    vals = list (book.values())
    
    if (len(keys) > 0):
        if ( checkSpecial(vals[0]) == False ):
            # no special character, search for exact match.
            query_string = re.compile('^' + vals[0] + '$')
        else:
            # contains special character, use pattern match.
            query_string = re.compile(vals[0], re.IGNORECASE)

        x = db.books.find( { keys[0] : query_string } ).sort (keys[0], pymongo.ASCENDING)
    
        ret_list = []
        for i in x:
            ret_list.append (i)
            
        if (not silent):
            print ("total ", len(ret_list), " book entries found.")
        
        if ( len(ret_list) == 0 ):
            print ("Book entry does not exist.")
            return ( "nonexistent", "nonexistent")
        elif ( len(ret_list) == 1):
            # fetch details and update UI fields.
            if (not silent):
                print ("fetching book details.")
            
            keys2 = list (ret_list[0].keys())
            vals2 = list (ret_list[0].values())
            return (keys2, vals2)
        else:
            if (not silent):
                print ("Multiple book entries exist.")
            popUpWindow(ret_list)
            return (None, None)
        
def update_book (db, book):
    if (debug):
        print ("updating book ", book)
    
    if (checkSpecial (book["book_name"]) == False):
        old_entry_keys, old_entry_vals = search_book (db, book)
        if (debug):
            print (old_entry_keys)
        
        new_entry_keys = list(book.keys())
        new_entry_vals = list(book.values())
        
        if (old_entry_keys != None):
            if ( old_entry_keys[0] == "nonexistent" ):
                if (debug):
                    print ("Unable to update: book entry does not exist.")
                popUpWarning ("Unable to update: book entry does not exist.")
            elif ( old_entry_vals[1] == new_entry_vals[0] ):
                _ = db.books.update_one( { new_entry_keys[0] : new_entry_vals[0] }, { "$set": book } )
            else:
                print ("landed here.")
        else:
            popUpWarning ("Multiple books meet update criteria.")
    else:
        popUpWarning ("Error: Book name contains special character(s).")

def delete_book (db, book):
    if (debug):
        print ("deleting book ", book)
    
    if (checkSpecial (book["book_name"]) == False):
        x, _ = search_book(db, book)
        if (debug):
            print (x)
        if (x != None):
            if (x == "nonexistent"):
                popUpWarning ("Unable to delete: book entry does not exist.")
            else:
                _ = db.books.delete_one ( book )
    else:
        popUpWarning ("Error: Book name contains special character(s).")

class Gui(object):
    def __init__(self):
        self.window = tk.Tk()
        self.createUI(self.window)

    # When OK is pressed, set all entered fields in the record and
    # close window.
    def add(self, *args):
        empty_record = 1
        if (self.book_name.get() != ""):
            config.myBook["book_name"] = self.book_name.get()
            empty_record = 0
        
        if (self.book_subname.get() != ""):
            config.myBook["book_subname"] = self.book_subname.get()
            empty_record = 0
        
        if (self.author1.get() != ""):
            config.myBook["author1"] = self.author1.get()
            empty_record = 0
        
        if (self.publisher.get() != ""):
            config.myBook["publisher"] = self.publisher.get()
            empty_record = 0
        
        if (self.edn.get() != ""):
            config.myBook["edition"] = self.edn.get()
            empty_record = 0
        
        if (self.pubYear.get() != ""):
            config.myBook["pub_year"] = self.pubYear.get()
            empty_record = 0
        
        if (self.price.get() != ""):
            config.myBook["price"] = self.price.get()
            empty_record = 0
        
        if (self.format.get() != ""):
            config.myBook["format"] = self.format.get()
            empty_record = 0
        
        if (self.tags.get() != ""):
            config.myBook["tags"] = self.tags.get()
            empty_record = 0
        
        if ( not empty_record ):
            add_book (config.db, config.myBook)
        else:
            print ("Cannot add empty record.")
        config.myBook.pop("_id", "null")

    # Search a book with given parameters.
    def srch(self, *args):
        empty_record = 1
        if (self.book_name.get() != ""):
            config.myBook["book_name"] = self.book_name.get()
            empty_record = 0
        
        if (self.book_subname.get() != ""):
            config.myBook["book_subname"] = self.book_subname.get()
            empty_record = 0
        
        if (self.author1.get() != ""):
            config.myBook["author1"] = self.author1.get()
            empty_record = 0
        
        if (self.publisher.get() != ""):
            config.myBook["publisher"] = self.publisher.get()
            empty_record = 0
        
        if (self.edn.get() != ""):
            config.myBook["edition"] = self.edn.get()
            empty_record = 0
        
        if (self.pubYear.get() != ""):
            config.myBook["pub_year"] = self.pubYear.get()
            empty_record = 0
        
        if (self.price.get() != ""):
            config.myBook["price"] = self.price.get()
            empty_record = 0
        
        if (self.format.get() != ""):
            config.myBook["format"] = self.format.get()
            empty_record = 0
        
        if (self.tags.get() != ""):
            config.myBook["tags"] = self.tags.get()
            empty_record = 0
        
        if ( not empty_record ):
            keys, vals = search_book (config.db, config.myBook, 0)
            if (debug):
                print ("search returned ", keys)
            if (keys):
                self.populate_UI (keys, vals)
        else:
            print ("Search cannot work on empty fields.")
    
    def populate_UI (self, keys, values):
        if (debug):
            print ("populating UI")
        for i in range(len(keys)):
            if (debug):
                print (keys[i], values[i])
                
            if (keys[i] == "_id"):
                pass
            else:
                if (keys[i] == "book_name"):
                    book_name_entry.delete (0, 'end')
                    book_name_entry.insert (0, values[i])
                elif (keys[i] == "book_subname"):
                    book_subt_entry.delete(0, 'end')
                    book_subt_entry.insert (0, values[i])
                elif (keys[i] == "author1"):
                    book_auth_entry.delete(0, 'end')
                    book_auth_entry.insert (0, values[i])
                elif (keys[i] == "publisher"):
                    book_pub_entry.delete(0, 'end')
                    book_pub_entry.insert (0, values[i])
                elif (keys[i] == "edition"):
                    book_edn_cbox.set (values[i])
                elif (keys[i] == "pub_year"):
                    book_pub_cbox.set (values[i])
                elif (keys[i] == "price"):
                    book_price_entry.delete(0, 'end')
                    book_price_entry.insert (0, values[i])
                elif (keys[i] == "format"):
                    book_form_cbox.set (values[i])
                elif (keys[i] == "tags"):
                    book_tags_entry.delete(0, 'end')
                    book_tags_entry.insert (0, values[i])
                else:
                    pass

    # Update a book with given parameters.
    def upd(self, *args):
        empty_record = 1
        if (self.book_name.get() != ""):
            config.myBook["book_name"] = self.book_name.get()
            empty_record = 0
        
        if (self.book_subname.get() != ""):
            config.myBook["book_subname"] = self.book_subname.get()
            empty_record = 0
        
        if (self.author1.get() != ""):
            config.myBook["author1"] = self.author1.get()
            empty_record = 0
        
        if (self.publisher.get() != ""):
            config.myBook["publisher"] = self.publisher.get()
            empty_record = 0
        
        if (self.edn.get() != ""):
            config.myBook["edition"] = self.edn.get()
            empty_record = 0
        
        if (self.pubYear.get() != ""):
            config.myBook["pub_year"] = self.pubYear.get()
            empty_record = 0
        
        if (self.price.get() != ""):
            config.myBook["price"] = self.price.get()
            empty_record = 0
        
        if (self.format.get() != ""):
            config.myBook["format"] = self.format.get()
            empty_record = 0
        
        if (self.tags.get() != ""):
            config.myBook["tags"] = self.tags.get()
            empty_record = 0
        
        if (not empty_record):
            _ = update_book (config.db, config.myBook)
        else:
            print ("Cannot update blank entry.")

    # Delete a book with given parameters.
    def delete(self, *args):
        empty_record = 1
        if (self.book_name.get() != ""):
            config.myBook["book_name"] = self.book_name.get()
            empty_record = 0
        
        if (self.book_subname.get() != ""):
            config.myBook["book_subname"] = self.book_subname.get()
            empty_record = 0
        
        if (self.author1.get() != ""):
            config.myBook["author1"] = self.author1.get()
            empty_record = 0
        
        if (self.publisher.get() != ""):
            config.myBook["publisher"] = self.publisher.get()
            empty_record = 0
        
        if (self.edn.get() != ""):
            config.myBook["edition"] = self.edn.get()
            empty_record = 0
        
        if (self.pubYear.get() != ""):
            config.myBook["pub_year"] = self.pubYear.get()
            empty_record = 0
        
        if (self.price.get() != ""):
            config.myBook["price"] = self.price.get()
            empty_record = 0
        
        if (self.format.get() != ""):
            config.myBook["format"] = self.format.get()
            empty_record = 0
        
        if (self.tags.get() != ""):
            config.myBook["tags"] = self.tags.get()
            empty_record = 0
        
        if ( not empty_record ):
            delete_book (config.db, config.myBook)
            self.clear()
        else:
            print ("Cannot delete empty book.")
    
    def clear(self, *args):
        if (debug):
            print ("Clearing all fields")
        
        config.myBook = {}
        book_name_entry.delete (0, 'end')
        book_subt_entry.delete (0, 'end')
        book_auth_entry.delete (0, 'end')
        book_pub_entry.delete (0, 'end')
        book_edn_cbox.set ("")
        book_pub_cbox.set ("")
        book_price_entry.delete (0, 'end')
        book_form_cbox.set ("")
        book_tags_entry.delete (0, 'end')
        config.myBook.pop("_id", "null")
    
    def ex(self, *args):
        print ("Preparing to exit.")
        config.myBook = {}
        self.window.quit()

    # Remove blank fields from record.
    def check_val(self, *args):
        if (self.book_name.get() == ""):
            config.myBook.pop("book_name", "null")
        elif (self.book_subname.get() == ""):
            config.myBook.pop("book_subname", "null")
        elif (self.author1.get() == ""):
            config.myBook.pop("author1", "null")
        elif (self.publisher.get() == ""):
            config.myBook.pop("publisher", "null")
        elif (self.edn.get() == ""):
            config.myBook.pop("edition", "null")
        elif (self.pubYear.get() == ""):
            config.myBook.pop("pub_year", "null")
        elif (self.price.get() == ""):
            config.myBook.pop("price", "null")
        elif (self.format.get() == ""):
            config.myBook.pop("format", "null")
        elif (self.tags.get() == ""):
            config.myBook.pop("tags", "null")
        else:
            pass
        return True
    
    def cnt (self, *args):
        self.lbl_txt.set ( len(list (config.books_coll.find())) )  # @UndefinedVariable
    
    def createUI(self, window):
        self.book_name = StringVar()
        self.book_subname = StringVar()
        self.author1 = StringVar()
        self.publisher = StringVar()
        self.edn = StringVar()
        self.pubYear = StringVar()
        self.price = StringVar()
        self.format = StringVar()
        self.count_var = StringVar()
        self.lbl_txt = StringVar()
        self.tags = StringVar()
        
        # Make following Entry widgets global.
        global book_name_entry, book_subt_entry, book_auth_entry
        global book_pub_entry, book_price_entry, book_tags_entry
        global book_edn_cbox, book_pub_cbox, book_form_cbox
        
#        atexit.register (self.exit_handler)
        window.title ("Book Library")
        
        mainframe = ttk.Frame (window, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, columnspan=8, sticky=(N, W, E, S))
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)

        rnum = 0
        
        # book title
        ttk.Label (mainframe, text="Book Title").grid (column=0, row=rnum, sticky=W)
        book_name_entry = ttk.Entry (mainframe, width=80, textvariable=self.book_name)
        book_name_entry.grid(column=1, row=rnum, sticky=(W, E))
        rnum = rnum + 1
        
        # book sub-title
        ttk.Label (mainframe, text="Sub-title").grid (column=0, row=rnum, sticky=W)
        book_subt_entry = ttk.Entry (mainframe, width=80, textvariable=self.book_subname)
        book_subt_entry.grid (column=1, row=rnum, sticky=(W, E))
        rnum = rnum + 1
        
        # authors
        ttk.Label (mainframe, text="Author(s)").grid (column=0, row=rnum, sticky=(W, E))
        book_auth_entry = ttk.Entry (mainframe, width=80, textvariable=self.author1)
        book_auth_entry.grid(column=1, row=rnum, sticky=W)
        #ttk.Button (mainframe, text="+", width=2, command=self.addAuth).grid(column=2, row=rnum, sticky=W)
        rnum = rnum + 1
        
        # publisher
        ttk.Label (mainframe, text="Publisher").grid (column=0, row=rnum, sticky=(W, E))
        book_pub_entry = ttk.Entry (mainframe, width=80, textvariable=self.publisher)
        book_pub_entry.grid (column=1, row=rnum, sticky=W)
        rnum = rnum + 1
        
        # edition, publication sub-frame
        subframe1 = ttk.Frame (mainframe, width=80, padding='0 3 3 3')
        subframe1.grid(column=0, row=rnum, columnspan=8, sticky=(N, W, E, S))
        rnum = rnum + 1
        col = 0

        # edition
        ttk.Label (subframe1, text="Edition").grid (column=col, row=0, sticky=W)
        col = col + 1
        book_edn_cbox = ttk.Combobox (subframe1, width=4, textvariable=self.edn)
        book_edn_cbox['values'] = list(range(1,16))
        book_edn_cbox.state(["readonly"])
        book_edn_cbox.grid (column=col, row=0, padx=5, sticky=W)
        col = col + 1
        
        # year of publication
        ttk.Label (subframe1, text="").grid (column=col, row=0, padx=10)
        col = col + 1
        ttk.Label (subframe1, text="Publication Year").grid (column=col, row=0, padx=5)
        col = col + 1
        book_pub_cbox = ttk.Combobox (subframe1, width=5, textvariable=self.pubYear)
        book_pub_cbox['values'] = list(range (1930, 2051))
        book_pub_cbox.state(["readonly"])
        book_pub_cbox.grid (column=col, row=0, padx=5, sticky=W)
        col = col + 1
        
        # price
        ttk.Label (subframe1, text="").grid (column=col, row=0, padx=10, sticky=W)
        col = col + 1
        ttk.Label (subframe1, text="Price").grid (column=col, row=0, padx=5, sticky=W)
        col = col + 1
        book_price_entry = ttk.Entry (subframe1, width=5, textvariable=self.price)
        book_price_entry.grid (column=col, row=0, padx=5, sticky=W)
        
        subframe2 = ttk.Frame (mainframe, width=80, padding='0 3 3 3')
        subframe2.grid(column=0, row=rnum, columnspan=8, sticky=(N, W, E, S))
        rnum = rnum + 1
        col = 0

        # format: Physical, PDF, DJVU, PS, HTML
        ttk.Label (subframe2, text="Format").grid (column=col, row=1, sticky=W)
        col = col + 1
        book_form_cbox = ttk.Combobox (subframe2, width=8, textvariable=self.format)
        book_form_cbox['values'] = ('Physical', 'PDF', 'DJVU', 'PS', 'HTML')
        book_form_cbox.state(['readonly'])
        book_form_cbox.grid (column=col, row=1, padx=5, sticky=W)
        col = col + 1
        
        # tags
        ttk.Label (subframe2, text="").grid (column=col, row=1, padx=10)
        col = col + 1
        ttk.Label (subframe2, text="Tags").grid (column=col, row=1, padx=5)
        col = col + 1
        book_tags_entry = ttk.Entry (subframe2, width=40, textvariable=self.tags)
        book_tags_entry.grid(column=col, row=1, padx=5, sticky=(W, E))

        # OK, Cancel, Clear sub-frame.
        subframe3 = ttk.Frame (mainframe, padding="3 3 3 9")
        subframe3.grid (column=0, row=rnum, columnspan=2, sticky=(N, W, E, S))
        rnum = rnum + 1
        
        col = 0
        ttk.Button (subframe3, text="Add", command=self.add).grid(column=col, row=0, sticky=W)
        col = col + 1
        ttk.Button (subframe3, text="Search", command=self.srch).grid(column=col, row=0, padx=10, sticky=W)
        col = col + 1
        ttk.Button (subframe3, text="Update", command=self.upd).grid(column=col, row=0, padx=10, sticky=W)
        col = col + 1
        ttk.Button (subframe3, text="Delete", command=self.delete).grid(column=col, row=0, padx=10, sticky=W)
        col = col + 1
        ttk.Button (subframe3, text="Clear", command=self.clear).grid(column=col, row=0, padx=10, sticky=W)
        col = col + 1
        ttk.Button (subframe3, text="Exit", command=self.ex).grid(column=col, row=0, padx=10, sticky=W)
        col = col + 1
        ttk.Button (subframe3, text="Count", command=self.cnt).grid(column=col, row=0, padx=10, sticky=W)
        
        # total count label and number display area.
        ttk.Label (mainframe, text="Total books").grid (column=0, row=rnum, sticky=(W, E))
        ttk.Label (mainframe, textvariable=self.lbl_txt).grid (column=1, row=rnum, sticky=(W, E))
        self.cnt()
        rnum = rnum + 1
        
        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)
        
        book_name_entry.focus()
        window.bind("<Return>", self.add)
        
        # monitor each input for activity. When value changes, callback function
        # sets the value in the record.
        self.book_name.trace_add("write", self.check_val)
        self.book_subname.trace_add("write", self.check_val)
        self.author1.trace_add("write", self.check_val)
        self.publisher.trace_add("write", self.check_val)
        self.edn.trace_add("write", self.check_val)
        self.pubYear.trace_add("write", self.check_val)
        self.price.trace_add("write", self.check_val)
        self.format.trace_add("write", self.check_val)
        self.tags.trace_add("write", self.check_val)
        
        window.mainloop()

    def __del__(self):
        pass
    
#    def exit_handler(self):
#        print (config.myBook)
#        print ("exiting gui")
