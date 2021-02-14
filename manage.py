#Use flask manager to provide CLI for setup

from flask_script import Manager
from domain_monitor import app, db, migrate
from flask_migrate import Migrate, MigrateCommand
import logging
    

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def run_merge_task():
    from domain_monitor.merge_task import merge_all_data
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, filename="task.log", format=log_format)
    merge_all_data()


@manager.command
def load_search_string(search_string):
    from domain_monitor.models import Search
    db.session.add(Search(search_string=search_string))
    db.session.commit()

if __name__ == "__main__":
    manager.run()