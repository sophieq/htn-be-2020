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
$ 
```
Note: 
1. Make sure you are in the root directory of the repository 

## Endpoints
**Get All Users**
```
GET __/users
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
    "events": [
      {
        "name": <string>
      }
    ]
  },
  ...
]
```
**Get a User**
```
GET __/users/<user_id>
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
  "events": [
    {
      "name": <string>
    }
  ]
}
```
**User Location Query**
```
GET _/users?lat=<float>&long=<float>&range=<float>
```
Response: a list of users {id, name} withthin the location range
``` json
[
  {
    "name": <string>,
    "user_id":<string>
  },
  ...
]
```
Note:
1. range > 0 

**Get an Event**
```
GET _/events/<event_id>
```
Response: an event object with attendees
``` json
{
  "event_name": <string>,
  "event_id": <number>,
  "attendees”: [
    {
      "name": <string>,
      "id": <number>,
      ...
    },
    ...
  ]
}
```
**Add a User to an Event**
```
POST _/events/<event_id>/attendees
```
with payload:
``` json
{
    "user_id": <user_id}
}

```
Response: 

**Remove a User from an Event**
```
DELETE _/events/<event_id>/attendees
```
with payload:
``` json
{
    "user_id": <user_id}
}
```
Response:

### Tests 
I tested my API endpoints using Postman and Google Chrome using a `sample.json`, a subset of the `data.json`. 

## Future Improvements

