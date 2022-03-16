# https://realpython.com/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from flask_migrate import Migrate
from capstone.models import setup_db, db, Actor, Movie, actor_movie
from capstone.auth import AuthError, requires_auth

migrate = Migrate()

def create_app(test_config=None):
    # configure the app
    app = Flask(__name__)
    setup_db(app)
    migrate.init_app(app, db)
    CORS(app)

    # https://developer.mozilla.org/en-US/docs/Glossary/Preflight_request
    # https://stackoverflow.com/questions/29954037/why-is-an-options-request-sent-and-can-i-disable-it#:~:text=OPTIONS%20requests%20are%20what%20we,different%20origins%20in%20specific%20situations.

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,POST,DELETE,PATCH,OPTIONS')
        return response

    '''
        Error handlers for all expected errors
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bed_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bed request"
        }), 400

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500

    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        return response


    '''
    endpoints for Actors
    '''

    '''
        Create an endpoint to handle GET requests for all available actors.
    '''

    @app.route('/actors')
    @requires_auth('get:actors')
    def get_actors():
        actors = Actor.query.all()
        actors_list = [actor.format() for actor in actors]
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

    '''
    Endpoints for Movies
    '''
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
                "movie_id": movie_id,
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

    return app

app = create_app()

'''
if __name__ == '__main__':
    app.run
'''