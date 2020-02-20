import sqlite3

from flask import Flask, request, jsonify
from sqlite3 import Error

conn = sqlite3.connect('database_init/hackers.db')
# conn.isolation_level = None
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
    users_data = query_db( '''
    WITH user_events_table AS (
        SELECT
            users.user_id AS user_id,
            group_concat(events.event_id || "+" || events.event_name) AS events
        FROM
            users
        JOIN
            users_events
        ON
            users.user_id = users_events.user_id
        JOIN 
            events ON users_events.event_id = events.event_id 
        GROUP BY
            users.user_id
    )
    SELECT
        name,
        picture,
        company,
        email,
        phone,
        latitude,
        longitude,
        user_events_table.events,
        users.user_id
    FROM
        users
    JOIN
        user_events_table
    ON users.user_id = user_events_table.user_id
    ''')

    users_list = []
    for user in users_data:
        user_dict = get_user_object(user, ["user_id", "name", "picture", "email", "phone", "latitude", "longitude"], True)
        users_list.append(user_dict)

    return jsonify(users_list)

@app.route('/users/<user_id>', methods=["GET"])
def get_user(user_id):
    user_data = query_db(
        '''
            WITH user_events_table AS (
            SELECT
                users.user_id AS user_id,
                group_concat(events.event_id || "+" || events.event_name) AS events
            FROM
                users
            JOIN
                users_events
            ON
                users.user_id = users_events.user_id
            JOIN 
                events ON users_events.event_id = events.event_id 
            WHERE
                users.user_id=?
            GROUP BY
                users.user_id
        )
        SELECT
            name,
            picture,
            company,
            email,
            phone,
            latitude,
            longitude,
            user_events_table.events
        FROM
            users
        JOIN
            user_events_table
        ON users.user_id = user_events_table.user_id
        '''
        , [user_id], True
    )

    user_dict = get_user_object(user_data, ["name", "picture", "email", "phone", "latitude", "longitude"], True)
    user_dict["user_id"] = user_id
    return jsonify(user_dict)

@app.route('/location', methods=["GET"])
def get_users_at_location():
    # type checking for min, max
    latitude = float(request.args.get('lat'))
    longitude = float(request.args.get('long'))
    range_val = float(request.args.get('range'))

    users_data = query_db(
        '''
        SELECT 
            user_id, name
        FROM 
            users
        WHERE 
            latitude BETWEEN ? AND ?
            AND longitude BETWEEN ? AND ?
        ''', 
        (latitude - range_val, latitude  + range_val, longitude - range_val, longitude + range_val)
    )

    users_list = []
    for user in users_data:
        user_dict = get_user_object(user, ["user_id", "name"])
        users_list.append(user_dict)
    
    return jsonify(users_list)

@app.route('/events/<event_id>', methods=["GET"])
def get_event(event_id):
    event_data = query_db(
        '''
        SELECT event_name
        FROM events
        WHERE event_id = ?
        '''
        ,
        [event_id],
        True
    )

    attendees_data = query_db(
        '''
        SELECT * 
        FROM users
        JOIN users_events
        ON users.user_id = users_events.user_id
        WHERE event_id = ?
        ''',
        [event_id]
    )

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

@app.route('/events/<event_id>/attendees/add', methods=["POST"])
def add_user_to_event(event_id):
    posted_data = request.get_json()
    user_id = posted_data["user_id"]

    response = ""

    try: 
        query_db(''' INSERT OR FAIL INTO users_events(user_id, event_id)
                    VALUES(?,?); ''', (user_id, event_id))
        conn.commit()
        response = "Insertion complete"
    except Error as e:
        response = "Oops! This user has already attended this event"

    return response

@app.route('/events/<event_id>/attendees/delete', methods=["POST"])
def delete_user_from_event(event_id):
    posted_data = request.get_json()
    user_id = posted_data["user_id"]

    response = ""

    deleted_rows = query_db(''' DELETE FROM users_events
                                WHERE user_id = ? AND event_id = ? ''', (user_id, event_id))
    print(deleted_rows)
    conn.commit()
    response = "Deletion complete"

    return response


# error handling

@app.teardown_appcontext
def close_connection(exception):
    conn.cursor()
