from capstone import app
from capstone.models import db, Movie, Actor, actor_movie
from flask import jsonify, request, abort
from capstone.auth import requires_auth

'''
    Create an endpoint to handle GET requests for all available actors.
'''
@app.route('/actors')
@requires_auth('get:actors')
def get_actors():
    actors = Actor.query.all()
    actors_list = [actor.format() for actor in actors]
    if len(actors_list) == 0:
        abort(404)

    return jsonify({
        "success": True,
        "actors": actors_list
    })

'''
    Create an endpoint to handle GET requests for the actor
'''
@app.route('/actors/<int:actor_id>')
@requires_auth('get:actors-detail')
def get_actor(actor_id):
    # print(actor_id)
    actor = Actor.query.get(actor_id)
    if actor is None:
        abort(404)
    else:
        return jsonify({
            "success": True,
            "actor": actor.format()
        })


'''
    Create an endpoint to handle GET requests for all movies of the actor
'''
@app.route('/actors/<int:actor_id>/movies')
@requires_auth('get:actors-movies')
def get_actor_movies(actor_id):
    actor = Actor.query.get(actor_id)
    if actor is None:
        abort(404)
    else:
        # https://docs.sqlalchemy.org/en/14/orm/query.html#sqlalchemy.orm.Query.join
        # https://docs.sqlalchemy.org/en/14/core/metadata.html
        # https://stackoverflow.com/questions/48206047/how-to-return-all-the-columns-with-flask-sqlalchemy-query-join-from-two-tables

        # get all movies for actor:
        movies = Movie.query.join(actor_movie).join(Actor) \
            .filter(actor_movie.c.movie_id == Movie.id and actor_movie.c.actor_id == Actor.id) \
            .filter(Actor.id == actor_id) \
            .all()
        return jsonify({
            "success": True,
            "actor_id": actor_id,
            "totalMovies": len(movies),
            "movies": [movie.format() for movie in movies]
        })


'''
    Create an endpoint to handle POST requests to connect the actor and the movie
'''
@app.route('/actors/<int:actor_id>/movies/<int:movie_id>', methods=['POST'])
@requires_auth('post:actors-movie')
def add_movie_to_actor(actor_id, movie_id):
    actor = Actor.query.get(actor_id)
    movie = Movie.query.get(movie_id)
    if actor is None or movie is None:
        abort(404)
    else:
        # https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#many-to-many
        actor.movies.append(movie)
        try:
            actor.update()
            return jsonify({
                "success": True,
                "actor_id": actor_id,
                "movie_id": movie_id
            })
        except:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()


'''
    Create an endpoint to POST a new actor 
'''
# https://stackabuse.com/how-to-get-and-parse-http-post-body-in-flask-json-and-form-data/
@app.route('/actors', methods=['POST'])
@requires_auth('post:actors')
def create_actor():
    content = request.get_json()
    if content['name'].strip() == "":
        # if name of the actor isn't specified,
        # we don't create new question
        abort(400, "name of the actor isn't specified")
    try:
        # list of column names for Actor
        columns = ['name', 'age', 'gender']
        # list of column values for new actor
        values = [content[c] if c in content else None for c in columns]
        new_actor = Actor(*values)
        new_actor.insert()
        return jsonify({
            "success": True,
            "added": new_actor.id
        })
    except:
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()

'''
    Create an endpoint to DELETE actor using an actor ID.   
'''
@app.route('/actors/<int:actor_id>', methods=['DELETE'])
@requires_auth('delete:actors')
def delete_actor(actor_id):
    actor = Actor.query.get(actor_id)
    if actor is None:
        abort(404)
    else:
        try:
            # db.session.query(actor_movie).filter_by(actor_id=actor_id).delete()
            actor.delete()
            return jsonify({
                "success": True,
                "deleted": actor_id
            })
        except:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()


'''
    Create an endpoint to PATCH actor using an actor ID and actor's parameters that need to be changed.   
'''
@app.route('/actors/<int:actor_id>', methods=['PATCH'])
@requires_auth('patch:actors')
def update_actor(actor_id):
    actor = Actor.query.get(actor_id)
    if actor is None:
        abort(404)
    else:
        try:
            # https://stackoverflow.com/questions/2612610/how-to-access-object-attribute-given-string-corresponding-to-name-of-that-attrib
            content = request.get_json()
            for c in content:
                setattr(actor, c, content[c])
            actor.insert()
            return jsonify({
                "success": True,
                "updated": actor_id
            })
        except:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

