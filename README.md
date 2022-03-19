# Capstone Project

This is the capstone project for the Udacity Full Stack Nanodegree program.  
I developed this project to make use of the knowledge I acquired in this Nanodegree and hence gain confidence in these skills.  
The project based on the work of the Casting Agency. 
The Casting Agency models a company that is responsible for creating movies and managing and assigning actors to those movies.  
There are three roles of the agency employs: a casting assistant, a casting director and an executive producer. Each role has different permissions.

## URLs

Capstone app URL deployed on Heroku: https://udacity-capstone-shondy.herokuapp.com/  

## Start the capstone app on local machine 
### Installing Dependencies

### Installing Dependencies for the Backend

1. **Python 3.8** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)


2. **Virtual Enviornment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)


3. **PIP Dependencies** - Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:
```bash
pip install -r requirements.txt
```
This will install all of the required packages we selected within the `requirements.txt` file.


4. **Key Dependencies**
 - [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

 - [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

 - [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

### Database Setup
From within the `./test_app` directory with Postgres running, restore a database using the capstone_test.psql file provided. From the backend folder in terminal run:
```bash
psql movies_actors_test < capstone_test.psql
```

### Running the server

From the root directory of the capstone project first ensure you are working using your created virtual environment.

Each time you open a new terminal session, run:

```bash
export FLASK_APP=capstone
```

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.
 
The endpoints are defined in `/capstone/__init__.py`, DB models and SQLAlchemy 
setup - in `/capstone/models.py`. 

## Authentication

### Casting Assistant
A Casting Assistant can only view actors and movies.

#### Permissions:
```bash
get:actors         | get:movies
get:actors-detail  | get:movies-detail
get:actors-movies  | get:movies-actors
```

### Casting Director
A Casting Director has 
  - All permissions a Casting Assistant has and…
  - Add or delete an actor from the database
  - Modify actors or movies

#### Permissions:
```bash
get:actors         | get:movies
get:actors-detail  | get:movies-detail
get:actors-movies  | get:movies-actors
post:actors-movie  | post:movies-actor
patch:actors       | patch:movies
post:actors        |
delete:actors      | 
```

### Executive Producer
The Executive Producer has
 - All permissions a Casting Director has and…
 - Add or delete a movie from the database

#### Permissions:
```bash
get:actors         | get:movies
get:actors-detail  | get:movies-detail
get:actors-movies  | get:movies-actors
post:actors-movie  | post:movies-actor
patch:actors       | patch:movies
post:actors        | post:movies
delete:actors      | delete:movies 
```

## Endpoint conventions and Error codes
All responses are returned in JSON format and all contain a 
"success" key, which will return either True or False.

All requests contain a bearer token in a header, the API checks that the token provided is allowed to perform current operation. 

The API can return next error codes: 400, 404, 405, 422, and 500. 
The return format has the following structure (example for the 404 code): 
```
{
    "success": False,
    "error": 404,
    "message": "resource not found"
}
```
##### GET /actors
Returns: list of actor objects and success value
```
{
  "actors": [
        {
            "age": 12,
            "gender": "male",
            "id": 1,
            "name": "Yu"
        },
        {
            "age": 32,
            "gender": "male",
            "id": 3,
            "name": "Alen"
        }
    ],
    "success": true
}
```
##### GET /movies
Returns: list of movie objects and success value
```
{
    "movies": [
        {
            "id": 1,
            "release_date": "Sat, 02 Mar 2019 00:00:00 GMT",
            "title": "Father Brown"
        },
        {
            "id": 2,
            "release_date": "Sat, 02 Mar 1977 00:00:00 GMT",
            "title": "Star Wars"
        }
    ],
    "success": true
}
```
##### GET /actors/\<int:actor_id>
Returns: actor object with id=actor_id and success value
```
{
    "actor": {
        "age": 12,
        "gender": "male",
        "id": 2,
        "name": "Yu"
    },
    "success": true
}
```
##### GET /movies/\<movie_id>
Returns: list of movie objects with id=movie_id and success value
```
{
    "movie": {
        "id": 1,
        "release_date": "Sat, 02 Mar 2019 00:00:00 GMT",
        "title": "Father Brown"
    },
    "success": true
}
```
##### GET /actors/\<actor_id>/movies
Returns: actor_id, list of movie objects for actor object with id=actor_id, success value and total number of movies
```
{
    "actor_id": 3,
    "movies": [
        {
            "id": 1,
            "release_date": "Sat, 02 Mar 2019 00:00:00 GMT",
            "title": "Father Brown"
        }
    ],
    "success": true,
    "totalMovies": 1
}
```
##### GET /movies/\<movie_id>/actors
Returns: movie_id, list of actor objects for movie object with id=movie_id, success value and total number of actors
```
{
    "actors": [
        {
            "age": 32,
            "gender": "male",
            "id": 3,
            "name": "Alen"
        }
    ],
    "movie_id": 1,
    "success": true,
    "totalActors": 1
}
```
##### POST /actors/\<actor_id>/movies/\<movie_id>
Adds the movie with id=movie_id to the actor with id=actor_id
Returns: actor_id, movie_id and success value
```
{
    "actor_id": 3,
    "movie_id": 1,
    "success": true
}
```
##### POST /movies/\<movie_id>/actors/\<actor_id>
Adds the actor with id=actor_id to the movie with id=movie_id
Returns: actor_id, movie_id and success value
```
{
    "actor_id": 3,
    "movie_id": 1,
    "success": true
}
```
##### PATCH /actors/\<actor_id>
Request: actor object attributes and values that need to be updated in JSON format
 ```
{
    "age": 12
}
```
Returns: success value and id of updated actor
```
{
    "success": true,
    "updated": 1
}
```
##### PATCH /movies/\<movie_id>
Request: movie object attributes that need to be updated in JSON format
```
{
    "title": "Star War 1"
}
```
Returns: success value and id of updated movie
```
{
    "success": true,
    "updated": 1
}
```
##### POST /actors
Request: name, age, gender of created new actor object in JSON format. 
 ```
{
    'name': 'Arnold Schwarzenegger',
    'age': '74',
    'gender': 'male'
}
```
Returns: success value and id of newly created actor
```
{
    "success": true,
    "added": 4
}
```
##### POST /movies
Request: title and release_date of created new movie object in JSON format
```
{
    'title': 'Terminator',
    'release_date': "1984-07-01"
}
```
Returns: success value and id of newly created movie
```
{
    "success": true,
    "added": 4
}
```
##### DELETE /actor/\<actor_id>
Returns: success value and id of deleted actor
```
{
    'success': true,
    'deleted': 6
}
```
##### DELETE /movie/\<movie_id>
Returns: success value and id of deleted movie
```
{
    'success': true,
    'deleted': 6
}
```

## Testing
To run the unit tests, from within the `./test_app` directory run
```
createdb movies_actors_test
psql movies_actors_test < capstone_test.psql
python test_app.py
```
Set environment variable:
```
set DATABASE_URL=postgresql://<username>:<password>@localhost:5432/movies_actors_test
set APP_SETTINGS=config_app.TestingConfig
set CASTING_ASSISTANT_JWT=<JWT for casting assistant>
set CASTING_DIRECTOR_JWT=<JWT for casting director> 
set EXECUTIVE_PRODUCER_JWT=<JWT for executive producer>
```