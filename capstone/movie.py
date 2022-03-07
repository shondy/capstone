from capstone import app
from capstone.models import db, Movie, Actor, actor_movie
from flask import jsonify, request, abort
from capstone.auth import requires_auth

'''
    Create an endpoint to handle GET requests for all available movies.
'''
@app.route('/movies')
@requires_auth('get:movies')
def get_movies():
    movies = Movie.query.all()
    movies_list = [movie.format() for movie in movies]
    return jsonify({
        "success": True,
        "movies": movies_list
    })


'''
    Create an endpoint to handle GET requests for the movie.
'''
@app.route('/movies/<int:movie_id>')
@requires_auth('get:movies-detail')
def get_movie(movie_id):
    movie = Movie.query.get(movie_id)
    if movie is None:
        abort(404)
    else:
        return jsonify({
            "success": True,
            "movie": movie.format()
        })


'''
    Create an endpoint to handle GET requests for all actors in the movie.
'''
@app.route('/movies/<int:movie_id>/actors')
@requires_auth('get:movies-actors')
def get_movie_actors(movie_id):
    movie = Movie.query.get(movie_id)
    if movie is None:
        abort(404)
    else:
        # get all actors for movie:
        actors = Actor.query.join(actor_movie).join(Movie) \
            .filter(actor_movie.c.actor_id == Actor.id and actor_movie.c.movie_id == Movie.id) \
            .filter(Movie.id == movie_id) \
            .all()
        return jsonify({
            "success": True,
            "movie": movie_id,
            "totalActors": len(actors),
            "actors": [actor.format() for actor in actors]
        })


'''
    Create an endpoint to handle POST requests to connect the actor and the movie
'''
@app.route('/movies/<int:movie_id>/actors/<int:actor_id>', methods=['POST'])
@requires_auth('post:movies-actor')
def add_actor_to_movie(actor_id, movie_id):
    actor = Actor.query.get(actor_id)
    movie = Movie.query.get(movie_id)
    if actor is None or movie is None:
        abort(404)
    else:
        # https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#many-to-many
        movie.actors.append(actor)
        try:
            movie.update()
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
    Create an endpoint to POST a new movie   
'''
@app.route('/movies', methods=['POST'])
@requires_auth('post:movies')
def create_movie():
    content = request.get_json()
    if content['title'].strip() == "":
        # if name of the actor isn't specified,
        # we don't create new question
        abort(400, "title of the movie isn't specified")

    try:
        # list of column names for Movie
        columns = ['title', 'release_date']
        # list of column values for new movie
        values = [content[c] if c in content else None for c in columns]

        new_movie = Movie(*values)
        new_movie.insert()
        return jsonify({
            "success": True,
            "added": new_movie.id
        })
    except:
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()



'''
    Create an endpoint to DELETE movie using a movie ID.   
'''
@app.route('/movies/<int:movie_id>', methods=['DELETE'])
@requires_auth('delete:movies')
def delete_movie(movie_id):
    movie = Movie.query.get(movie_id)
    if movie is None:
        abort(404)
    else:
        try:
            # db.session.query(actor_movie).filter_by(movie_id=movie_id).delete()
            movie.delete()
            return jsonify({
                "success": True,
                "deleted": movie_id
            })
        except:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

'''
    Create an endpoint to PATCH movie using a movie ID and movie's parameters that need to be changed.   
'''
@app.route('/movies/<int:movie_id>', methods=['PATCH'])
@requires_auth('patch:movies')
def update_movie(movie_id):
    movie = Movie.query.get(movie_id)
    if movie is None:
        abort(404)
    else:
        try:
            # https://stackoverflow.com/questions/2612610/how-to-access-object-attribute-given-string-corresponding-to-name-of-that-attrib
            content = request.get_json()
            for c in content:
                setattr(movie, c, content[c])
            movie.insert()
            return jsonify({
                "success": True,
                "updated": movie_id
            })
        except:
            db.session.rollback()
            abort(422)
        finally:
            db.session.close()

