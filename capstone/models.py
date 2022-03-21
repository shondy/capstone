import os
from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import Table, Column, Integer, ForeignKey, String, Date

db = SQLAlchemy()
'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app):
    # https://stackoverflow.com/questions/54600434/how-to-set-flask-env-inside-config-file
    # https://stackoverflow.com/questions/39859234/keyerror-app-settings
    # when creating environment variable from command line in Windows don't use quotation marks
    app.config.from_object(os.environ['APP_SETTINGS'])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)
    #db.create_all()

# https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/

'''
Extend the base Model class to add common methods
'''
class ModelIUD(db.Model):
    __abstract__ = True

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

'''
Movie

'''
class Movie(ModelIUD):
    __tablename__ = 'Movie'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    release_date = db.Column(db.Date)

    actors = db.relationship('Actor', secondary='actor_movie', lazy='subquery',
                             backref=db.backref('movies', lazy='subquery'))

    def __init__(self, title, release_date=None):
        self.title = title
        self.release_date = release_date

    def format(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date
        }

class Actor(ModelIUD):
    __tablename__ = 'Actor'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(50))

    def __init__(self, name, age=None, gender=None):
        self.name = name
        self.age = age
        self.gender = gender

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender
        }


actor_movie = db.Table('actor_movie',
                       db.Column('actor_id', db.Integer, db.ForeignKey('Actor.id'), primary_key=True),
                       db.Column('movie_id', db.Integer, db.ForeignKey('Movie.id'), primary_key=True)
                       )
