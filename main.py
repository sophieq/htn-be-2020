import sqlite3
from database_init.sql_queries import *
from flask import Flask, request, jsonify
from sqlite3 import Error

conn = sqlite3.connect('database_init/hackers.db')
conn.row_factory = sqlite3.Row

app = Flask(__name__)

# Helper functions

def query_db(query, args=(), one=False):
    cur = conn.cursor()
    cur = cur.execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return (rows[0] if rows else None) if one else rows

def parse_string_to_list(list_string, keys):
    event_list = list_string.split(",")
    event_dicts = []
    for event in event_list:
        event_info = event.split("+")
        event_dict = dict(zip(keys, event_info))
        event_dicts.append(event_dict)
    return event_dicts

def get_user_object(user_data, keys, addEvents = False):
    user_data = dict(user_data) # get sqlite dict from query
    user_dict = {key: user_data[key] for key in keys}

    # add events attended to user
    if addEvents:
        user_dict["attended_events"] = []
        if "events" in user_data:
            attended_events_dict = parse_string_to_list(user_data["events"], ["event_id", "event_name"])            
            user_dict["attended_events"] = attended_events_dict
    
    return user_dict

# Endpoints

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/users', methods=["GET"])
def get_all_users():
    users_data = query_db(GET_ALL_USERS)

    users_list = []
    for user in users_data:
        user_dict = get_user_object(user, ["user_id", "name", "picture", "email", "phone", "latitude", "longitude"], True)
        users_list.append(user_dict)

    return jsonify(users_list)

@app.route('/users/<user_id>', methods=["GET"])
def get_user(user_id):
    user_data = query_db(GET_SINGLE_USER, [user_id], True)

    user_dict = get_user_object(user_data, ["name", "picture", "email", "phone", "latitude", "longitude"], True)
    user_dict["user_id"] = user_id
    return jsonify(user_dict)

@app.route('/location', methods=["GET"])
def get_users_at_location():
    # type checking for min, max
    latitude = float(request.args.get('lat'))
    longitude = float(request.args.get('long'))
    range_val = float(request.args.get('range'))

    if range_val < 0:
        return "ERROR: range only takes positive values"

    users_data = query_db(GET_USERS_FROM_LOCATION, 
        (latitude - range_val, latitude  + range_val, longitude - range_val, longitude + range_val)
    )

    users_list = []
    for user in users_data:
        user_dict = get_user_object(user, ["user_id", "name", "latitude", "longitude"])
        users_list.append(user_dict)
    
    return jsonify(users_list)

@app.route('/events/<event_id>', methods=["GET"])
def get_event(event_id):
    event_data = query_db(GET_EVENT_NAME, [event_id], True)

    attendees_data = query_db(GET_ATTENDEES_INFO, [event_id])

    event_data_dict = dict(event_data)

    event_dict = {}
    event_dict["event_id"] = event_id
    event_dict["event_name"] = event_data_dict["event_name"]
    
    attendees_list = []
    for attendee in attendees_data:
        attendees_dict = get_user_object(attendee, ["name", "picture", "email", "phone", "latitude", "longitude"], False)
        attendees_list.append(attendees_dict)

    event_dict["attendees"] = attendees_list

    return jsonify(event_dict)

@app.route('/events/<event_id>/attendees', methods=["POST", "DELETE"])
def modify_event_attendees(event_id):
    posted_data = request.get_json()
    user_id = posted_data["user_id"]
    response = ""

    if request.method == "POST":
        try: 
            query_db(INSERT_INTO_USERS_EVENTS_TABLE_IF_POSSIBLE, (user_id, event_id))
            conn.commit()
            response = "Insertion complete"
        except Error as e:
            response = "Oops! This user has already attended this event"

    elif request.method == "DELETE":
        deleted_rows = query_db(DELETE_FROM_USERS_EVENTS_TABLE, (user_id, event_id))
        conn.commit()
        response = "Deletion complete"

    return response

# error handling

@app.teardown_appcontext
def close_connection(exception):
    conn.cursor()
