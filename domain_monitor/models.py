
#SQLAlchemy models country, zone, domain tables - what if domain is expired and renew by someone else. 
#if it is expried and renew. With version number 

"""
Contains all Database configuration, models and relationships.
"""
import enum
from sqlalchemy import Integer, Enum
from flask_sqlalchemy import SQLAlchemy
from domain_monitor import app, db

class Zone(db.Model):
    __tablename__ = 'zone'

    id = db.Column(db.Integer(), primary_key=True)
    zone = db.Column(db.String())

    domains = db.relationship('Domain', backref='zone')

class Domain(db.Model):
    __tablename__ = 'domain'

    id = db.Column(db.Integer(), primary_key=True)
    domain_name = db.Column(db.String()) 
    zone_id = db.Column(db.Integer(), db.ForeignKey('zone.id'))

    registrations = db.relationship('Registration', backref='domain')
    
class Registration(db.Model):
    __tablename__ = 'registration'

    id = db.Column(db.Integer(), primary_key=True) # generate a id for registration
    domain_id = db.Column(db.Integer(),  db.ForeignKey("domain.id"))

    is_dead = db.Column(db.String())
    current_date = db.Column(db.String())

    create_date = db.Column(db.DateTime())
    update_date = db.Column(db.DateTime())
    end_date = db.Column(db.DateTime())

    hosted_countries = db.relationship("HostedCountry", backref='registration')
    resource_record = db.relationship("ResourceRecordType", backref='registration')


class HostedCountry(db.Model):
    __tablename__ = 'hosted_country'

    id = db.Column(db.Integer(), primary_key=True) # generate a id for country
    registration_id = db.Column(db.Integer(), db.ForeignKey('registration.id')) 
    country_id = db.Column(db.Integer(), db.ForeignKey('country.id'))


class Country(db.Model):
    __tablename__ = 'country'

    id = db.Column(db.Integer(), primary_key=True) # generate a id for country
    country_name = db.Column(db.String()) # Abbreviation for country (eg. JP, US)

    hosted_countries = db.relationship("HostedCountry", backref='country')


class ResourceRecordType(enum.Enum):
    a = 1
    cname = 2
    mx = 3
    ns = 4
    txt = 5

class ResourceRecord(db.Model):
    __tablename__ = 'resource_record'

    id = db.Column(db.Integer(), primary_key=True)
    registration_id = db.Column(db.Integer(), db.ForeignKey('registration.id')) 
    record_type = db.Column(db.Enum(ResourceRecordType))
    priority = db.Column(db.String())
    value = db.Column(db.String())

