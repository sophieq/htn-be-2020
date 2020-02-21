#!/usr/bin/env python

import json
import sqlite3
from sqlite3 import Error
from sql_queries import *

'''
Populate tables with data.json
    cur: cursor that is connected to database for data insertion
'''
def insert_data(cur):
    with open('data.json') as file:
        data = json.load(file)
        # parse information from data and insert into appropriate table
        for entry in data:
            # insert user 
            cur.execute(INSERT_INTO_USERS_TABLE, (entry["name"], entry["picture"], entry["company"], entry["email"], entry["phone"], entry["latitude"], entry["longitude"]))
            user_id = cur.lastrowid

            for event in entry["events"]:
                event_id = None
                cur.execute(GET_EVENT_ID_FOR_EVENT_NAME, [event["name"]])
                event_row = cur.fetchone()

                if event_row is None:
                    # insert new event 
                    cur.execute(INSERT_INTO_EVENTS_TABLE, [event["name"]])
                    event_id = cur.lastrowid
                else:
                    # event already exists, and id gets returned 
                    event_id = event_row[0]

                # add user & event to the user attended event table
                if user_id is not None and event_id is not None: 
                    cur.execute(INSERT_INTO_USERS_EVENTS_TABLE, (user_id, event_id))
              
'''
Creates tables for database
    db_file: the name of the database that will be created
'''
def create_database(db_file):
    conn = None 
    try:
        conn = sqlite3.connect(db_file)
        conn.isolation_level = None
        conn.execute('''PRAGMA foreign_keys = ON;''')

        cur = conn.cursor()

        # create tables
        cur.execute(CREATE_USER_TABLE)
        cur.execute(CREATE_EVENTS_TABLE)
        cur.execute(CREATE_USERS_EVENTS_RELATIONSHIP_TABLE)

        # index to search for location
        cur.execute(CREATE_LOCATION_IDX)
        # index to guarantee that a user can only attend one event
        cur.execute(CREATE_USER_EVENT_IDX)

        insert_data(cur)

    except Error as e:
        print(e)

    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    create_database(r"hackers.db")
