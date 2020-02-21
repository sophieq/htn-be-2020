# Hack the North 2020 Backend Challenge
> My submission for the the Hack the North 2020 be challenge using SQLite, Flask 

## Usage
**Populate Database** 
To populate the `hackers.db` database
```
$ cd database_init
$ ./database.py
```
Note: 
1. `hackers.db` has already been prepopulated. If you would like to populate the database again, please delete the `hackers.db` file.

**Run Server**
```
$ env FLASK_APP=main.py flask run
```
Note: 
1. Make sure you are in the root directory of the repository 

## Endpoints
**Get All Users**
```
GET http://localhost:5000/users
```
Response: a list of user objects 
``` json
[
  {
    "user_id":<string>,
    "name": <string>,
    "picture": <string>,
    "company": <string>,
    "email": <string>,
    "phone": <string>,
    "latitude": <float>,
    "longitude": <float>,
    "attended_events": [
      {
        "event_id": <string>,
        "event_name": <string>
      }
    ]
  },
  ...
]
```
**Get a User**
```
GET http://localhost:5000/users/<user_id>
```
Response: a user object
``` json
{
  "user_id":<string>,
  "name": <string>,
  "picture": <string>,
  "company": <string>,
  "email": <string>,
  "phone": <string>,
  "latitude": <float>,
  "longitude": <float>,
  "attended_events": [
    {
      "event_id": <string>,
      "event_name": <string>
    }
  ]
}
```
**User Location Query**
```
GET http://localhost:5000/users?lat=<float>&long=<float>&range=<float>
```
Response: a list of users {id, name} within the location range
``` json
[
  {
    "name": <string>,
    "user_id":<string>,
    "latitude: <float>,
    "longitude": <float>
  },
  ...
]
```
Note:
1. if range < 0, an error response will be returned

**Get an Event**
```
GET http://localhost:5000/events/<event_id>
```
Response: an event object with attendees
``` json
{
  "event_name": <string>,
  "event_id": <number>,
  "attendees”: [
    {
      "user_id":<string>,
      "name": <string>,
      "picture": <string>,
      "company": <string>,
      "email": <string>,
      "phone": <string>,
      "latitude": <float>,
      "longitude": <float>,
    },
    ...
  ]
}
```
Note:
1. if event id is invalid, an error response will be returned
**Add a User to an Event**
```
POST http://localhost:5000/events/<event_id>/attendees
```
with payload:
``` json
{
    "user_id": <string>}
}

```
Response: 
```
Successfully added user_id <user_id> to event_id <event_id> 
OR
{
  "code": "200", 
  "message": "Oops! This user has already attended this event"
}
```

**Remove a User from an Event**
```
DELETE http://localhost:5000/events/<event_id>/attendees
```
with payload:
``` json
{
    "user_id": <string>}
}
```
Response:
```
{
  "code": "200", 
  "message": "Successfully deleted user_id <user_id> from event_id <event_id>"
}

```


### Tests 
I tested my API endpoints using Postman and Google Chrome using a `sample.json`, a subset of the `data.json`. Unfortunately curl was not working on my mac :/ . 

## Future Improvements
Some things to improve/add on:
* currently DELETE will always return a success message, whether or not user actually attended event
* throw JSON error for invalid user_id and event_id when trying to add or remove attendee from event
* add a get all events api

Scalable improvements:
* If users columns grow, we should me location (lat, long) into a seperate table 
* Add layers of security if for example we don't want to user getting requests to see user locations

