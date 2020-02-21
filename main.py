import sqlite3
from database_init.sql_queries import *
from flask import Flask, Response, request, jsonify
from sqlite3 import Error

conn = sqlite3.connect('database_init/hackers.db')
# get dictionairy from query responses
conn.row_factory = sqlite3.Row 

app = Flask(__name__)

# json returned fields
EVENT_FIELDS_FOR_USER = ["event_id", "event_name"]
USER_FIELDS = ["user_id", "name", "company", "picture", "email", "phone", "latitude", "longitude"]
USER_LOCATION_FIELDS = ["user_id", "name", "latitude", "longitude"]

# Helper Functions

'''
Make sql query to database
    query: String - sql query
    args: Tuple - values to pass into query
    one: Bool - if true, return one result
'''
def query_db(query, args=(), one=False):
    cur = conn.cursor()
    cur = cur.execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return (rows[0] if rows else None) if one else rows

'''
Parses a string of values using deliminators , and + and return list of dicts
    list_string: String - string to parse
    keys: [String] - keys to map to values from list_string
'''
def parse_string_to_dicts(list_string, keys):
    event_list = list_string.split(",")
    event_dicts = []
    for event in event_list:
        event_info = event.split("+")
        # map keys to event_info
        event_dict = dict(zip(keys, event_info))
        event_dicts.append(event_dict)
    return event_dicts

'''
Returns a user dict
    user_data: sqlite.Row - data from sql query
    keys: [String] - keys to create user dict
    addEvents: Bool - if true, add user attended events to user dict
'''
def get_user_object(user_data, keys, addEvents = False):
    user_data = dict(user_data) # get sqlite dict from query
    # maps values for user_data to keys 
    user_dict = {key: (user_data[key] if key in user_data else None) for key in keys}

    # add events attended by user
    if addEvents:
        user_dict["attended_events"] = []
        if "events" in user_data:
            # get attended events for a user from string created by group_concat
            attended_events_dict = parse_string_to_dicts(user_data["events"], EVENT_FIELDS_FOR_USER)            
            user_dict["attended_events"] = attended_events_dict
    
    return user_dict

'''
Returns an Api response
    status: String - indication of success or failure of request
    code: Int - Api response code
    message: String - message to explain response
'''
def get_response(status, code, message):
    return jsonify({"{}".format(status): "{}".format(code), "message": "{}".format(message)}), code

# Endpoints
@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/users', methods=["GET"])
def get_all_users():
    users_data = query_db(GET_ALL_USERS)

    users_list = []
    for user in users_data:
        user_dict = get_user_object(user, USER_FIELDS, True)
        users_list.append(user_dict)

    return jsonify(users_list)

@app.route('/users/<user_id>', methods=["GET"])
def get_user(user_id):
    user_data = query_db(GET_SINGLE_USER, [user_id], True)

    if user_data is None:
        return get_response("error", 404, "user with id {} does not exist".format(user_id))

    user_dict = get_user_object(user_data, USER_FIELDS, True)
    user_dict["user_id"] = user_id
    return jsonify(user_dict)

@app.route('/location', methods=["GET"])
def get_users_at_location():
    latitude = float(request.args.get('lat'))
    longitude = float(request.args.get('long'))
    range_val = float(request.args.get('range'))

    if range_val < 0:
        return get_response("error", 400, "range value must be greater than or equal to 0")

    users_data = query_db(
        GET_USERS_FROM_LOCATION, 
        (latitude - range_val, latitude  + range_val, longitude - range_val, longitude + range_val)
    )

    users_list = []
    for user in users_data:
        user_dict = get_user_object(user, USER_LOCATION_FIELDS)
        users_list.append(user_dict)
    
    return jsonify(users_list)

@app.route('/events/<event_id>', methods=["GET"])
def get_event(event_id):
    # get event name
    event_data = query_db(GET_EVENT_NAME, [event_id], True)
    # get users at the event
    attendees_data = query_db(GET_ATTENDEES_INFO, [event_id])

    if event_data is None:
        return get_response("error", 404, "event with id {} does not exist".format(event_id))

    event_data_dict = dict(event_data)

    event_dict = {}
    event_dict["event_id"] = event_id
    event_dict["event_name"] = event_data_dict["event_name"]
    
    attendees_list = []
    for attendee in attendees_data:
        attendees_dict = get_user_object(attendee, USER_FIELDS, False)
        attendees_list.append(attendees_dict)

    event_dict["attendees"] = attendees_list

    return jsonify(event_dict)

@app.route('/events/<event_id>/attendees', methods=["POST", "DELETE"])
def modify_event_attendees(event_id):
    posted_data = request.get_json()
    user_id = posted_data["user_id"]
    response = None

    if request.method == "POST":
        try: 
            query_db(INSERT_INTO_USERS_EVENTS_TABLE_IF_POSSIBLE, (user_id, event_id))
            conn.commit()
            response = Response("Successfully added user_id {} to event_id {} \n".format(user_id, event_id), status=201, mimetype='application/json')
            response.headers['location'] ='/events/{}/attendees'.format(event_id)

        except Error as e:
            # if user has already attended an event return error
            response = get_response("code", 200, "Oops! This user has already attended this event")            

    elif request.method == "DELETE":
        deleted_rows = query_db(DELETE_FROM_USERS_EVENTS_TABLE, (user_id, event_id))
        conn.commit()
        response = get_response("code", 200, "Successfully deleted user_id {} from event_id {} \n".format(user_id, event_id))

    return response

@app.teardown_appcontext
def close_connection(exception):
    conn.cursor()
