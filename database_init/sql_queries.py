INSERT_INTO_USERS_TABLE = '''
    INSERT INTO users(name,picture,company,email,phone, latitude, longitude)
    VALUES(?,?,?,?,?,?,?)
    '''

INSERT_INTO_EVENTS_TABLE = '''
    INSERT INTO events(event_name) 
    VALUES(?); 
    '''

INSERT_INTO_USERS_EVENTS_TABLE = ''' 
    INSERT INTO users_events(user_id, event_id)
    VALUES(?,?); 
    '''

GET_EVENT_ID_FOR_EVENT_NAME = '''
    SELECT event_id 
    FROM events 
    WHERE event_name=?
    '''

GET_ALL_USERS = '''
    WITH user_events_table AS (
        SELECT 
            users.user_id AS user_id,
            group_concat(events.event_id || "+" || events.event_name) AS events
        FROM users
        JOIN users_events
        ON users.user_id = users_events.user_id
        JOIN events ON users_events.event_id = events.event_id 
        GROUP BY users.user_id
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
    FROM users
    JOIN user_events_table
    ON users.user_id = user_events_table.user_id
    '''

GET_SINGLE_USER = '''
    WITH user_events_table AS (
        SELECT
            users.user_id AS user_id,
            group_concat(events.event_id || "+" || events.event_name) AS events
        FROM users
        JOIN users_events
        ON users.user_id = users_events.user_id
        JOIN events ON users_events.event_id = events.event_id 
        WHERE users.user_id=?
        GROUP BY users.user_id
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
    FROM users
    JOIN user_events_table
    ON users.user_id = user_events_table.user_id
    '''

GET_USERS_FROM_LOCATION = '''
    SELECT 
        user_id, name, latitude, longitude 
    FROM users
    WHERE latitude BETWEEN ? AND ?
        AND longitude BETWEEN ? AND ?
    '''

GET_EVENT_NAME = '''
    SELECT event_name
    FROM events
    WHERE event_id = ?
    '''

GET_ATTENDEES_INFO = '''
    SELECT * 
    FROM users
    JOIN users_events
    ON users.user_id = users_events.user_id
    WHERE event_id = ?
    '''

INSERT_INTO_USERS_EVENTS_TABLE_IF_POSSIBLE = ''' 
    INSERT OR FAIL INTO users_events(user_id, event_id)
    VALUES(?,?); 
    '''

DELETE_FROM_USERS_EVENTS_TABLE = ''' 
    DELETE FROM users_events
    WHERE user_id = ? AND event_id = ? 
    '''