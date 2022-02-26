# https://stackoverflow.com/questions/29872867/using-flask-migrate-with-flask-script-and-application-factory
# https://flask-migrate.readthedocs.io/en/latest/
from capstone import create_app
from flask_migrate import MigrateCommand, Manager

manager = Manager(create_app)
manager.add_command('db', MigrateCommand)

if __name__ == "__main__":
    manager.run()
