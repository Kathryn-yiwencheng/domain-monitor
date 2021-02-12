
#SQLAlchemy models country, zone, domain tables - what if domain is expired and renew by someone else. 
#if it is expried and renew. With version number 

"""
Contains all Database configuration, models and relationships.
"""

from flask_sqlalchemy import SQLAlchemy
from domain_monitor import app, db

class Domain(db.Model):
    __tablename__ = 'domain'

    domain_name = db.Column(db.Integer(), db.ForeignKey('registration.domain_name'), primary_key=True) 
    zone_id = db.Column(db.Integer, db.ForeignKey('zone.id'), primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'), primary_key=True)

class Country(db.Model):
    __tablename__ = 'country'

    id = db.Column(db.Integer, primary_key=True) # generate a id for country
    country_name = db.Column(db.String()) # Abbreviation for country (eg. JP, US)

class Zone(db.Model):
    __tablename__ = 'zone'

    id = db.Column(db.Integer, primary_key=True)
    zone = db.Column(db.String())


class Registration(db.Model):
    __tablename__ = 'registration'

    domain_name = db.Column(db.Integer(),  primary_key=True)
    a = db.Column(db.String())
    ns = db.Column(db.String())
    cname = db.Column(db.String())
    mx = db.Column(db.String())
    txt = db.Column(db.String())

    is_dead = db.Column(db.String())
    current_date = db.Column(db.String())

    create_date = db.Column(db.DateTime())
    update_date = db.Column(db.DateTime())
    end_date = db.Column(db.DateTime())


