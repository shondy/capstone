import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from capstone import create_app
from capstone.models import setup_db, Actor, Movie, db
from sqlalchemy import func


class CapstoneTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        '''
        self.client = self.app.test_client
        self.database_name = "capstone_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('helen',
                                                               'pop23',
                                                               'localhost:5432',
                                                               self.database_name)
        setup_db(self.app, self.database_path)
        '''
        self.new_actor = {
            'name': 'Arnold Schwarzenegger',
            'age': 74,
            'gender': 'male'
        }

        self.new_movie = {
            'title': 'Terminator',
            'release_date': "1984-07-01"
        }

        # binds the app to the current context
        # https://flask-sqlalchemy.palletsprojects.com/en/2.x/api/
        # https://stackoverflow.com/questions/20036520/what-is-the-purpose-of-flasks-context-stacks
        with self.app.app_context():
            #self.db = SQLAlchemy()
            #self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after each test"""
        pass

    def get_api_token(self):
        response = self.client.post('/api/tokens', auth=('susan', 'foo'))
        return response.json['token']

    # Unit Tests

    # For actors

    def test_get_actors(self):
        """Gets the /actors endpoint and checks valid results"""
        token = self.get_api_token()
        res = self.client.get(
            '/actors', headers={'Authorization': f'Bearer {token}'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['actors']), 3)

    def test_404_get_actors_from_empty_table(self):
        """Test rising of 404 error if requested all categories from
        empty Category table
        """
        db.session.query(Actor).delete()
        db.session.flush()
        token = self.get_api_token()
        res = self.client().get('/actors',
                                headers={'Authorization': f'Bearer {token}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

        db.session.rollback()

    def test_get_actors_by_id(self):
        """Test searching for an actor by id"""
        token = self.get_api_token()
        res = self.client().get('/actors/1',
                                headers={'Authorization': f'Bearer {token}'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor']['id'], 1)
        self.assertEqual(data['actor']['name'], 'Yurasik')
        self.assertEqual(data['actor']['age'], 12)
        self.assertEqual(data['actor']['gender'], 'male')

    def test_400_get_questions_containing_long_searchTerm(self):
        """Test searching for an actor by id who's id s not in the DB,
         should return 400 error"""
        token = self.get_api_token()
        res = self.client().get('/actors/100',
                                headers={'Authorization': f'Bearer {token}'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_create_new_actor(self):
        """Test creating of an actor"""
        actors = Actor.query.all()
        num_actors_before = len(actors)
        token = self.get_api_token()
        res = self.client().post('/actors',
                                 json=self.new_actor,
                                 headers={'Authorization': f'Bearer {token}'})
        data = json.loads(res.data)
        actors = Actor.query.all()
        num_actors_after = len(actors)
        max_id = db.session.query(func.max(Actor.id)).scalar()
        self.assertEqual(num_actors_after, num_actors_before + 1)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['added'], max_id)

    def test_400_if_actor_name_is_not_specified(self):
        """Test creating of an actor who name wasn't specified,
         should return 400 error"""
        self.new_actor["name"] = ""
        token = self.get_api_token()
        res = self.client().post('/actors',
                                 json=self.new_question,
                                 headers={'Authorization': f'Bearer {token}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bed request')
        self.new_question["answer"] = "Arnold Schwarzenegger"

    def test_delete_actor(self):
        """Test deleting of the actor with maximum id"""
        max_id = db.session.query(func.max(Actor.id)).scalar()
        token = self.get_api_token()
        res = self.client().delete('/actor/' + str(max_id),
                                   headers={'Authorization': f'Bearer {token}'})
        data = json.loads(res.data)
        actor = Actor.query.filter(Actor.id == max_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], max_id)
        self.assertEqual(actor, None)

    def test_404_if_deleted_actor_does_not_exist(self):
        """Test deleting of an actor that doesn't exist, should return 404 error"""
        token = self.get_api_token()
        res = self.client().delete('/actors/100',
                                   headers={'Authorization': f'Bearer {token}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_update_actor(self):
        """Test searching for an actor by id"""
        actor = Actor.query.filter(Actor.id == 1).first()
        age = actor.age + 1
        patch = {
            'age': age
        }
        token = self.get_api_token()
        res = self.client().patch('/actors/1',
                                  json=patch,
                                  headers={'Authorization': f'Bearer {token}'})
        actor = Actor.query.filter(Actor.id == 1).first()
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['updated'], 1)
        self.assertEqual(actor.age, age)

    def test_400_if_updated_actor_does_not_exist(self):
        """Test updating of an actor that doesn't exist,
        should return 404 error"""
        token = self.get_api_token()
        res = self.client().patch('/actors/100',
                                  headers={'Authorization': f'Bearer {token}'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_actor_movies(self):
        """Test getting actor's movies"""
        token = self.get_api_token()
        res = self.client().get('/actors/1/movies',
                                headers={'Authorization': f'Bearer {token}'})
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor_id'], 1)
        self.assertEqual(data['totalMovies'], 2)

    def test_404_if_movies_actor_does_not_exist(self):
        """Test deleting of a question that doesn't exist, should return 404 error"""
        # Get questions for category 100 (doesn't exist, should 404)
        token = self.get_api_token()
        res = self.client().get('/actors/100/movies',
                                headers={'Authorization': f'Bearer {token}'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_add_movie_to_actor(self):
        """Test adding movie to actor"""
        token = self.get_api_token()
        res = self.client().get('/actors/1/movies/1',
                                headers={'Authorization': f'Bearer {token}'})
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor_id'], 1)
        self.assertEqual(data['movie_id'], 1)

    def test_404_if_actor_of_movie_does_not_actor(self):
        """Test adding movie to actor who does not exist"""
        token = self.get_api_token()
        res = self.client().get('/actors/100/movies/1',
                                headers={'Authorization': f'Bearer {token}'})
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor_id'], 1)
        self.assertEqual(data['movie_id'], 1)

        # For movies

    def test_get_movies(self):
        """Gets the /movies endpoint and checks valid results"""
        token = self.get_api_token()
        res = self.client.get(
            '/movies', headers={'Authorization': f'Bearer {token}'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['actors']), 3)

    '''
    def test_404_get_actors_from_empty_table(self):
        """Test rising of 404 error if requested all categories from
        empty Category table
        """
        db.session.query(Actor).delete()
        db.session.flush()
        res = self.client().get('/actors')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

        db.session.rollback()

    def test_get_actors_by_id(self):
        """Test searching for an actor by id"""
        res = self.client().get('/actors/1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor']['id'], 1)
        self.assertEqual(data['actor']['name'], 'Yurasik')
        self.assertEqual(data['actor']['age'], 12)
        self.assertEqual(data['actor']['gender'], 'male')

    def test_400_get_questions_containing_long_searchTerm(self):
        """Test searching for an actor by id who's id s not in the DB,
         should return 400 error"""
        res = self.client().get('/actors/100')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_create_new_actor(self):
        """Test creating of an actor"""
        actors = Actor.query.all()
        num_actors_before = len(actors)
        res = self.client().post('/actors', json=self.new_actor)
        data = json.loads(res.data)
        actors = Actor.query.all()
        num_actors_after = len(actors)
        max_id = db.session.query(func.max(Actor.id)).scalar()
        self.assertEqual(num_actors_after, num_actors_before + 1)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['added'], max_id)

    def test_400_if_actor_name_is_not_specified(self):
        """Test creating of an actor who name wasn't specified,
         should return 400 error"""
        self.new_actor["name"] = ""
        res = self.client().post('/actors', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bed request')
        self.new_question["answer"] = "Arnold Schwarzenegger"

    def test_delete_actor(self):
        """Test deleting of the actor with maximum id"""
        max_id = db.session.query(func.max(Actor.id)).scalar()
        res = self.client().delete('/actor/' + str(max_id))
        data = json.loads(res.data)
        actor = Actor.query.filter(Actor.id == max_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], max_id)
        self.assertEqual(actor, None)

    def test_404_if_deleted_actor_does_not_exist(self):
        """Test deleting of an actor that doesn't exist, should return 404 error"""
        res = self.client().delete('/actors/100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_update_actor(self):
        """Test searching for an actor by id"""
        actor = Actor.query.filter(Actor.id == 1).first()
        age = actor.age + 1
        patch = {
            'age': age
        }
        res = self.client().patch('/actors/1', json=patch)
        actor = Actor.query.filter(Actor.id == 1).first()
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['updated'], 1)
        self.assertEqual(actor.age, age)

    def test_400_if_updated_actor_does_not_exist(self):
        """Test updating of an actor that doesn't exist,
        should return 404 error"""
        res = self.client().patch('/actors/100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_actor_movies(self):
        """Test getting actor's movies"""
        res = self.client().get('/actors/1/movies')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor_id'], 1)
        self.assertEqual(data['totalMovies'], 2)

    def test_404_if_movies_actor_does_not_exist(self):
        """Test deleting of a question that doesn't exist, should return 404 error"""
        # Get questions for category 100 (doesn't exist, should 404)
        res = self.client().get('/actors/100/movies')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_add_movie_to_actor(self):
        """Test adding movie to actor"""
        res = self.client().get('/actors/1/movies/1')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor_id'], 1)
        self.assertEqual(data['movie_id'], 1)

    def test_404_if_actor_of_movie_does_not_actor(self):
        """Test adding movie to actor who does not exist"""
        res = self.client().get('/actors/100/movies/1')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor_id'], 1)
        self.assertEqual(data['movie_id'], 1)
    '''

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

