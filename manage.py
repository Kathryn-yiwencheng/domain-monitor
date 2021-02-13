#Use flask manager to provide CLI for setup

from flask_script import Manager

from domain_monitor import app, db, migrate

from domain_monitor.models import Zone, Country

from domain_monitor.domainsdb_client import get_domains

from flask_migrate import Migrate, MigrateCommand



manager = Manager(app)
manager.add_command('db', MigrateCommand)

@manager.command
def hello():
    print("hello")

@manager.command
def build_zone_table():
    results = get_domains("lava")
    zones = {domain.zone for domain in results.domains if domain.zone is not None}
    zone_models = [Zone(zone=zone) for zone in zones]
    for zone_model in zone_models:
        db.session.add(zone_model)
    db.session.commit()

@manager.command   
def build_country_table():
    results = get_domains("lava")
    countries = {domain.country for domain in results.domains if domain.country is not None}
    country_models = [Country(country_name=country) for country in countries]
    for country_model in country_models:
        db.session.add(country_model)
    db.session.commit()



if __name__ == "__main__":
    manager.run()