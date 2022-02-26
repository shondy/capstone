# https://realpython.com/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from capstone.models import setup_db, db, Actor, Movie, actor_movie
from capstone.auth import AuthError

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

    return app

app = create_app()
import capstone.movie
import capstone.actor

'''
if __name__ == '__main__':
    app.run
'''