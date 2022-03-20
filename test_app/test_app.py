import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from capstone import create_app
from capstone.models import Actor, Movie, db
from sqlalchemy import func

class CapstoneTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client

        # getting JWT of users with different roles
        self.CASTING_ASSISTANT = os.environ.get('CASTING_ASSISTANT_JWT')
        self.CASTING_DIRECTOR = os.environ.get('CASTING_DIRECTOR_JWT')
        self.EXECUTIVE_PRODUCER = os.environ.get('EXECUTIVE_PRODUCER_JWT')
        self.new_actor = {
            'name': 'Arnold Schwarzenegger',
            'age': '74',
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
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()


    def tearDown(self):
        """Executed after each test"""
        pass

    # Unit Tests

    # For actors
    def test_create_new_actor(self):
        """Test creating of an actor"""
        actors = Actor.query.all()
        num_actors_before = len(actors)
        res = self.client().post('/actors',
                                 headers={'Authorization': 'Bearer ' + self.CASTING_DIRECTOR},
                                 json=self.new_actor)
        data = json.loads(res.data)
        actors = Actor.query.all()
        num_actors_after = len(actors)
        max_id = db.session.query(func.max(Actor.id)).scalar()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(num_actors_after, num_actors_before + 1)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['added'], max_id)

    def test_400_if_actor_name_is_not_specified(self):
        """Test creating of an actor who name wasn't specified,
         should return 400 error"""
        self.new_actor["name"] = ""
        res = self.client().post('/actors',
                                 headers={'Authorization': 'Bearer ' + self.CASTING_DIRECTOR},
                                 json=self.new_actor)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bed request')
        self.new_actor["answer"] = "Arnold Schwarzenegger"

    def test_403_if_created_actor_by_CASTING_ASSISTANT(self):
        """Test creating of an actor by CASTING_ASSISTANT who is not authorized to that,
         should return 403 error"""
        res = self.client().post('/actors',
                                 headers={'Authorization': 'Bearer ' + self.CASTING_ASSISTANT},
                                 json=self.new_actor)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['code'], 'unauthorized')
        self.assertEqual(data['description'], 'Permission not found')


    def test_get_actors(self):
        """Gets the /actors endpoint and checks valid results"""
        res = self.client().get('/actors',
                                headers={'Authorization': 'Bearer ' + self.CASTING_ASSISTANT})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['actors']), 4)

    def test_get_actors_by_id(self):
        """Test searching for an actor by id"""
        res = self.client().get('/actors/1',
                                headers={'Authorization': 'Bearer ' + self.CASTING_ASSISTANT})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor']['id'], 1)
        self.assertEqual(data['actor']['name'], 'Tom')
        self.assertEqual(data['actor']['age'], 13)
        self.assertEqual(data['actor']['gender'], 'male')

    def test_400_get_actor_if_id_does_not_exist(self):
        """Test searching for an actor by id who's id s not in the DB,
         should return 400 error"""
        res = self.client().get('/actors/100',
                                headers={'Authorization': 'Bearer ' + self.CASTING_ASSISTANT})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_update_actor(self):
        """Test updating of an actor"""
        actor = Actor.query.filter(Actor.id == 1).first()
        age = actor.age + 1
        patch = {
            'age': age
        }
        res = self.client().patch(f'/actors/1',
                                  headers={'Authorization': 'Bearer ' + self.CASTING_DIRECTOR},
                                  json=patch)
        actor = Actor.query.filter(Actor.id == 1).first()
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['updated'], 1)
        self.assertEqual(actor.age, age)

    def test_400_if_updated_actor_does_not_exist(self):
        """Test updating of an actor that doesn't exist,
        should return 404 error"""
        res = self.client().patch('/actors/100',
                                  headers={'Authorization': 'Bearer ' + self.CASTING_DIRECTOR})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_403_if_updated_actor_by_CASTING_ASSISTANT(self):
        """Test updating of an actor by CASTING_ASSISTANT who is not authorized to that,
         should return 403 error"""
        patch = {
            'name': 'Boo'
        }
        res = self.client().patch(f'/actors/1',
                                  headers={'Authorization': 'Bearer ' + self.CASTING_ASSISTANT},
                                  json=patch)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['code'], 'unauthorized')
        self.assertEqual(data['description'], 'Permission not found')

    def test_delete_actor(self):
        """Test deleting of the actor with maximum id"""
        max_id = db.session.query(func.max(Actor.id)).scalar()
        res = self.client().delete('/actors/' + str(max_id),
                                   headers={'Authorization': 'Bearer ' + self.CASTING_DIRECTOR})
        data = json.loads(res.data)
        actor = Actor.query.filter(Actor.id == max_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], max_id)
        self.assertEqual(actor, None)

    def test_404_if_deleted_actor_does_not_exist(self):
        """Test deleting of an actor that doesn't exist, should return 404 error"""
        res = self.client().delete('/actors/100',
                                   headers={'Authorization': 'Bearer ' + self.CASTING_DIRECTOR})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_403_if_deleted_actor_by_CASTING_ASSISTANT(self):
        """Test deleting of an actor by CASTING_DIRECTOR who is not authorized to that,
         should return 403 error"""
        max_id = db.session.query(func.max(Actor.id)).scalar()
        res = self.client().delete('/actors/' + str(max_id),
                                   headers={'Authorization': 'Bearer ' + self.CASTING_ASSISTANT})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['code'], 'unauthorized')
        self.assertEqual(data['description'], 'Permission not found')


    def test_get_actor_movies(self):
        """Test getting actor's movies"""
        res = self.client().get('/actors/5/movies',
                                headers={'Authorization': 'Bearer ' + self.CASTING_ASSISTANT})
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor_id'], 5)
        self.assertEqual(data['totalMovies'], 1)

    def test_404_if_movies_actor_does_not_exist(self):
        """Test getting actor's movies if actor doesn't exist, should return 404 error"""
        # Get questions for category 100 (doesn't exist, should 404)
        res = self.client().get('/actors/100/movies',
                                headers={'Authorization': 'Bearer ' + self.CASTING_ASSISTANT})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_add_movie_to_actor(self):
        """Test adding movie to actor"""
        res = self.client().post('/actors/1/movies/2',
                                headers={'Authorization': 'Bearer ' + self.CASTING_DIRECTOR})
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor_id'], 1)
        self.assertEqual(data['movie_id'], 2)

    def test_404_if_actor_of_movie_does_not_exist(self):
        """Test adding movie to actor who does not exist"""
        res = self.client().post('/actors/100/movies/1',
                                headers={'Authorization': 'Bearer ' + self.CASTING_DIRECTOR})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_403_if_added_movie_actor_by_CASTING_ASSISTANT(self):
        """Test adding movie to actor by CASTING_DIRECTOR who is not authorized to that,
         should return 403 error"""
        res = self.client().post('/actors/1/movies/1',
                                 headers={'Authorization': 'Bearer ' + self.CASTING_ASSISTANT})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['code'], 'unauthorized')
        self.assertEqual(data['description'], 'Permission not found')

        # For movies

    def test_create_new_movie(self):
        """Test creating of an movie"""
        movies = Movie.query.all()
        num_movies_before = len(movies)
        res = self.client().post('/movies',
                                 headers={'Authorization': 'Bearer ' + self.EXECUTIVE_PRODUCER},
                                 json=self.new_movie)
        data = json.loads(res.data)
        movies = Movie.query.all()
        num_movies_after = len(movies)
        max_id = db.session.query(func.max(Movie.id)).scalar()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(num_movies_after, num_movies_before + 1)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['added'], max_id)

    def test_400_if_movie_title_is_not_specified(self):
        """Test creating of a movie who name wasn't specified,
         should return 400 error"""
        self.new_movie["title"] = ""
        res = self.client().post('/movies',
                                 headers={'Authorization': 'Bearer ' + self.EXECUTIVE_PRODUCER},
                                 json=self.new_movie)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bed request')
        self.new_movie["answer"] = "Arnold Schwarzenegger"

    def test_403_if_created_movie_by_CASTING_DIRECTOR(self):
        """Test creating of a movie by CASTING_DIRECTOR who is not authorized to that,
         should return 403 error"""
        res = self.client().post('/movies',
                                 headers={'Authorization': 'Bearer ' + self.CASTING_DIRECTOR},
                                 json=self.new_movie)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['code'], 'unauthorized')
        self.assertEqual(data['description'], 'Permission not found')

    def test_get_movies(self):
        """Gets the /movies endpoint and checks valid results"""
        res = self.client().get('/movies',
                                headers={'Authorization': 'Bearer ' + self.CASTING_ASSISTANT})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['movies']), 3)

    def test_get_movies_by_id(self):
        """Test searching for a movie by id"""
        res = self.client().get('/movies/1',
                                headers={'Authorization': 'Bearer ' + self.CASTING_ASSISTANT})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['movie']['id'], 1)
        self.assertEqual(data['movie']['title'], 'Father Brown')

    def test_400_get_movie_if_id_does_not_exist(self):
        """Test searching for a movie by id which's id s not in the DB,
         should return 400 error"""
        res = self.client().get('/movies/100',
                                headers={'Authorization': 'Bearer ' + self.CASTING_ASSISTANT})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_update_movie(self):
        """Test searching for an movie by id"""
        movie = Movie.query.filter(Movie.id == 3).first()
        title = movie.title + str(int(movie.title[-1]) + 1)
        patch = {
            'title': title
        }
        res = self.client().patch(f'/movies/3',
                                  headers={'Authorization': 'Bearer ' + self.CASTING_DIRECTOR},
                                  json=patch)
        movie = Movie.query.filter(Movie.id == 3).first()
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['updated'], 3)
        self.assertEqual(movie.title, title)

    def test_400_if_updated_movie_does_not_exist(self):
        """Test updating of an movie that doesn't exist,
        should return 404 error"""
        res = self.client().patch('/movies/100',
                                  headers={'Authorization': 'Bearer ' + self.CASTING_DIRECTOR})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_movie(self):
        """Test deleting of the movie with maximum id"""
        max_id = db.session.query(func.max(Movie.id)).scalar()
        res = self.client().delete('/movies/' + str(max_id),
                                   headers={'Authorization': 'Bearer ' + self.EXECUTIVE_PRODUCER})
        data = json.loads(res.data)
        movie = Movie.query.filter(Movie.id == max_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], max_id)
        self.assertEqual(movie, None)

    def test_404_if_deleted_movie_does_not_exist(self):
        """Test deleting of an movie that doesn't exist, should return 404 error"""
        res = self.client().delete('/movies/100',
                                   headers={'Authorization': 'Bearer ' + self.EXECUTIVE_PRODUCER})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_403_if_deleted_movie_by_CASTING_DIRECTOR(self):
        """Test deleting of an movie by CASTING_DIRECTOR who is not authorized to that,
         should return 403 error"""
        max_id = db.session.query(func.max(Movie.id)).scalar()
        res = self.client().delete('/movies/' + str(max_id),
                                   headers={'Authorization': 'Bearer ' + self.CASTING_DIRECTOR})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['code'], 'unauthorized')
        self.assertEqual(data['description'], 'Permission not found')

    def test_get_movie_actors(self):
        """Test getting movie's actors"""
        res = self.client().get('/movies/1/actors',
                                headers={'Authorization': 'Bearer ' + self.CASTING_ASSISTANT})
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['movie_id'], 1)
        self.assertEqual(data['totalActors'], 1)

    def test_404_if_actors_movie_does_not_exist(self):
        """Test getting movie's actors if movie doesn't exist, should return 404 error"""
        # Get questions for category 100 (doesn't exist, should 404)
        res = self.client().get('/movies/100/actors',
                                headers={'Authorization': 'Bearer ' + self.CASTING_ASSISTANT})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_add_actor_to_movie(self):
        """Test adding actor to movie"""
        res = self.client().post('/movies/3/actors/6',
                                 headers={'Authorization': 'Bearer ' + self.CASTING_DIRECTOR})
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['movie_id'], 3)
        self.assertEqual(data['actor_id'], 6)

    def test_404_if_movie_of_actor_does_not_exist(self):
        """Test adding actor to movie which does not exist"""
        res = self.client().post('/movies/100/actors/1',
                                 headers={'Authorization': 'Bearer ' + self.CASTING_DIRECTOR})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_403_if_added_actor_to_movie_by_CASTING_ASSISTANT(self):
        """Test adding actor to movie by CASTING_DIRECTOR who is not authorized to that,
         should return 403 error"""
        res = self.client().post('/movies/1/actors/1',
                                 headers={'Authorization': 'Bearer ' + self.CASTING_ASSISTANT})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['code'], 'unauthorized')
        self.assertEqual(data['description'], 'Permission not found')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

