#!/usr/bin/env python

import json
import sqlite3
from sqlite3 import Error


def insert_data(cur):
    with open('sample.json') as file:
        # an array of dictionairies 
        data = json.load(file)

    for entry in data:
        # insert user 
        cur.execute(''' INSERT INTO users(name,picture,company,email,phone)
              VALUES(?,?,?,?,?); ''', (entry["name"], entry["picture"], entry["company"], entry["email"], entry["phone"]))
        
        user_id = cur.lastrowid

        # insert location
        cur.execute('''
                    INSERT INTO location(user_id, latitude, longitude)
                    VALUES(?,?,?); ''', (user_id, entry["latitude"], entry["longitude"]))

        for event in entry["events"]:
            event_id = None

            cur.execute('''
            SELECT event_id 
            FROM events 
            WHERE event_name=?
                ''', [event["name"]])
            
            event_row = cur.fetchone()

            if event_row is None:
                # insert new event 
                cur.execute(''' INSERT INTO events(event_name) VALUES(?); ''', [event["name"]])
                event_id = cur.lastrowid
            else:
                event_id = event_row[0]

            # add user & event to the event user table
            if user_id is not None and event_id is not None: 
                cur.execute(''' INSERT INTO users_events(user_id, event_id)
                    VALUES(?,?); ''', (user_id, event_id))
              

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
                                    phone TEXT
                                );""")
        
        # create index for longitude - lattitude 

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

        # create location table
        cur.execute("""CREATE TABLE IF NOT EXISTS location (
                                    user_id INTEGER,
                                    latitude REAL NON NULL,
                                    longitude REAL NON NULL,
                                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                                );""")

        insert_data(cur)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    create_database(r"hackers.db")
