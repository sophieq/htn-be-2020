#!/usr/bin/env python

import json
import sqlite3
from sqlite3 import Error
from sql_queries import *

def insert_data(cur):
    with open('data.json') as file:
        # an array of dictionairies 
        data = json.load(file)

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
                event_id = event_row[0]

            # add user & event to the event user table
            if user_id is not None and event_id is not None: 
                cur.execute(INSERT_INTO_USERS_EVENTS_TABLE, (user_id, event_id))
              

# Creates a database named db_file with user and events tables
def create_database(db_file):
    conn = None 
    try:
        conn = sqlite3.connect(db_file)
        conn.isolation_level = None
        conn.execute('''PRAGMA foreign_keys = ON;''')

        cur = conn.cursor()

        # create tables
        # create user table
        cur.execute("""CREATE TABLE IF NOT EXISTS users (
                                    user_id INTEGER PRIMARY KEY,
                                    name TEXT NOT NULL,
                                    picture TEXT,
                                    company TEXT,
                                    email TEXT,
                                    phone TEXT,
                                    latitude REAL NON NULL,
                                    longitude REAL NON NULL
                                );""")

        # index to search for location
        cur.execute("""
            CREATE INDEX idx_user_location 
                ON users (latitude, longitude);
        """)
        
        # create event table
        cur.execute("""CREATE TABLE IF NOT EXISTS events (
                                    event_id INTEGER PRIMARY KEY,
                                    event_name TEXT NOT NULL
                                );""")
        
        # create user events table
        cur.execute("""CREATE TABLE IF NOT EXISTS users_events (
                                    user_id INTEGER,
                                    event_id INTEGER,
                                    FOREIGN KEY(user_id) REFERENCES users(user_id),
                                    FOREIGN KEY(event_id) REFERENCES events(event_id)
                                );""")

        cur.execute("""
            CREATE UNIQUE INDEX idx_user_event
                ON users_events (user_id, event_id);
        """)

        insert_data(cur)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    create_database(r"hackers.db")
