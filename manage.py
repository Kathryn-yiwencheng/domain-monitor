#Use flask manager to provide CLI for setup

from flask_script import Manager
from domain_monitor import app, db, migrate
from flask_migrate import Migrate, MigrateCommand



manager = Manager(app)
manager.add_command('db', MigrateCommand)

@manager.command
def hello():
    print("hello")

@manager.command
def build_tables():
    from domain_monitor.merge_task import load_data
    load_data()


if __name__ == "__main__":
    manager.run()