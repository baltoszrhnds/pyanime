#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlite3
import sys
import argparse

class Database():
    """provides all database I/O functions for anime database"""
    def __init__(self,dbname):
        """Prepares an anime database for I/O"""
        #Creates database with name specified by 'dbname' if it doesn't exist
        #and connects to it if/when it exists. If sqlite can't connect to the
        #database the program exits with an error.
        try:
            self.db = sqlite3.connect(dbname)
        except sqlite3.Error, e:
            print "Error %s:" % e.args[0] #prints error message
            sys.exit(1)
        #Creates a cursor to interface with the databasw
        self.cur = self.db.cursor()
        #If the database doesn't have an "anime" table, it creates one.
        self.cur.execute("CREATE TABLE IF NOT EXISTS anime"
                         "(Name TEXT PRIMARY KEY, Type TEXT, status TEXT, "
                         "score INT, current_ep INT, total_ep INT, "
                         "startDate TEXT, endDate TEXT, fansub TEXT, mal TEXT, "
                         "wiki TEXT, season TEXT, rwCount INT, "
                         "rwStartDate TEXT, rwEndDate TEXT, rwValue INT, "
                         "priority TEXT)")

    def add_anime(self, data):
        """Adds anime to the anime database. Accepts a tuple of tuples."""
        #The 'data' variable puts all the data to be entered into the database
        #into a tuple of tuples to be substituded into the INSERT command.
        #This is done for security.
        #All the data in 'data' is substituded in place of the '?' whenever
        #they appear. SQL then adds the information to the database to be
        #committed. Once it's committed, the changes are saved to the database.
        try:
            self.cur.execute("INSERT INTO anime VALUES(?, ?, ?, ?, ?, ?, ?, ?, "
                             "?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
            self.db.commit()
            print("anime added successfully")
        #If the database can't add the data into the table, the changes are
        #rolled back, the database is closed, and the error message is printed.
        except sqlite3.Error, e:
            self.db.rollback()
            self.db.close()
            print "Error %s:" % e.args[0]

    def update_anime(self,name,field,value):
        if field == "name":
            self.cur.execute("UPDATE anime SET Name=? WHERE Name=?",
                             (value, name))
            self.db.commit()
        else:
            print "not implemented"

    def remove_anime(self):
        pass

    def list_anime(self):
        self.cur.execute("SELECT * FROM anime")
        return self.cur.fetchall()

def ask_for_anime():
    name = raw_input("anime name: ")
    type_ = raw_input("(tv/movie/ova/ona): ") #The release medium
    score = raw_input("score (1-10): ") #can be empty for no rating
    #Status can be: watching, re-watching, on hold, complete, dropped, or
    #planned.
    status = raw_input("(watching/re-watching/on hold/complete/dropped/"
                       "planned): ")
    if status == "watching" or status == "on hold":
        currentEp = raw_input("last episode watched: ")
        totalEp = raw_input("total number of episodes: ")
        startDate = raw_input("start date: ")
        endDate = ""
        rwCount = 0
        rwStartDate = ""
        rwEndDate = ""
        rwValue = raw_input("rewatch value(1-5): ")
        priority = raw_input("watch priority(1-3): ")
    elif status == "re-watching":
        currentEp = raw_input("last episode watched: ")
        totalEp = raw_input("total number of episodes: ")
        startDate = raw_input("original start date: ")
        endDate = raw_input("original end date: ")
        rwCount = raw_input("times completed: ")
        rwStartDate = raw_input("rewatch start date: ")
        if rwCount > 0:
            rwEndDate = raw_input("last rewatch end date: ")
        else:
            rwEndDate = ""
        rwValue = raw_input("rewatch value(1-5): ")
        priority = raw_input("watch priority(1-3): ")
    elif status == "dropped":
        currentEp = raw_input("last episode watched: ")
        totalEp = raw_input("total number of episodes: ")
        startDate = raw_input("start date: ")
        endDate = raw_input("end date: ")
        rwCount = 0
        rwStartDate = ""
        rwEndDate = ""
        rwValue = 0
        priority = 0
    elif status == "complete":
        totalEp = raw_input("total number of episodes: ")
        currentEp = totalEp
        startDate = raw_input("start date: ")
        endDate = raw_input("end date: ")
        rwCount = raw_input("times completed: ")
        if rwCount > 1:
            rwStartDate = raw_input("rewatch started: ")
            rwEndDate = raw_input("rewatch completed: ")
        rwValue = raw_input("rewatch value(1-5): ")
        priority = raw_input("watch priority(1-3): ")
    elif status == "planned":
        currentEp = 0
        totalEp = raw_input("total number of episodes: ")
        startDate = ""
        endDate = ""
        rwCount = 0
        rwStartDate = ""
        rwEndDate = ""
        rwValue = ""
        priority = raw_input("watch priority(1-3): ")
    else:
        print("something broke :/")
    season = raw_input("anime season: ")
    fansub = raw_input("fansub group: ")
    MAL = raw_input("MyAnimeList URL: ")
    wikipedia = raw_input("Wikipedia URL: ")
      
    data = ((name, type_, score, status, currentEp, totalEp, startDate, endDate,
             rwCount, rwStartDate, rwEndDate, rwValue, priority, season, fansub,
             MAL, wikipedia))
    return data

class InteractiveMode():
    def main_loop(self,database):
        mode = ""
        while mode != "exit":
            print("please choose a mode:")
            mode = raw_input("(add/update/remove/list/exit)")
            if mode == "add":
                while True:
                    self.add(database)
                    if raw_input("continue?: ") == "no":
                        break
            elif mode == "update":
                while True:
                    self.update(database)
                    if raw_input("continue?: ") == "no":
                        break
            elif mode == "remove":
                while True:
                    self.remove(database)
                    if raw_input("continue?: ") == "no":
                        break
            elif mode == "list":
                while True:
                    self.list(database)
                    if raw_input("continue?: ") == "no":
                        break
            elif mode == "exit":
                database.db.close()
                break
            else:
                print("incorrect input")
    def add(self,database):
        database.add_anime(ask_for_anime())
    def update(self,database):
        database.update_anime()
    def remove(self,database):
        database.remove_anime()
    def list(self,database):
        rows = database.list_anime()
        if len(rows) > 0:
            columns = len(rows[0])
            for row in rows:
                cellCount = 0
                for cell in row:
                    cellCount += 1
                    if cellCount < columns:
                        print str(cell),
                    else:
                        print str(cell)
        else:
            print("Database is empty")

class Command(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        database = Database("anime.db")
        if self.dest == "interactive":
            InteractiveMode().main_loop(database)
        elif self.dest == "add":
            pass
        elif self.dest == "update":
            #This will be heavily modified when the appropriate flags
            #are added. The variables are test code.
            field = raw_input("Field: ")
            newVal = raw_input("New value: ")
            database.update_anime(values,field,newVal)
        elif self.dest == "remove":
            pass
        elif self.dest == "list":
            InteractiveMode().list(database)
        else:
            print "something went wrong"

#There is currently a bug with parsing the command-line arguments. Adding more
#than one of the same flag runs the function twice instead of causing argparse
#complain about it.

#The CLI options will be expanded upon later to make them more powerful and
#fully-featured.

parser = argparse.ArgumentParser(description="Run PyAnime, an anime database "
                                 "management program.")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-i", "--interactive", help="use interactive mode",
                   action=Command, nargs=0)
group.add_argument('-a', '--add', help="Add an anime to the database.",
                   action=Command)
group.add_argument('-u', '--update', help="Update an anime in the database.",
                   action=Command)
group.add_argument('-r', '--remove', help="Delete an anime from the database.",
                   action=Command)
group.add_argument('-l', '--list', help="List database entries.",
                   action=Command, nargs=0)

args = parser.parse_args()
