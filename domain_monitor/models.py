"""
Contains all Database configuration, models and relationships.
"""
import enum
from sqlalchemy import Integer, Enum
from flask_sqlalchemy import SQLAlchemy
from domain_monitor import app, db


class Search(db.Model):
    __tablename__ = 'search'

    id = db.Column(db.Integer(), primary_key=True)
    search_string = db.Column(db.String())


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

    is_dead = db.Column(db.Boolean())
    
    create_date = db.Column(db.DateTime())
    update_date = db.Column(db.DateTime())

    added_date = db.Column(db.DateTime())
    removed_date = db.Column(db.DateTime())
    last_seen_date = db.Column(db.DateTime())

    hosted_countries = db.relationship("HostedCountry", backref='registration')
    resource_records = db.relationship("ResourceRecord", backref='registration')

    def __repr__(self):
        return "<Registration domain=%r create_date=%r>" % (self.domain.domain_name, self.create_date)

class HostedCountry(db.Model):
    __tablename__ = 'hosted_country'

    id = db.Column(db.Integer(), primary_key=True) # generate a id for country
    registration_id = db.Column(db.Integer(), db.ForeignKey('registration.id')) 
    country_id = db.Column(db.Integer(), db.ForeignKey('country.id'))

    added_date = db.Column(db.DateTime())
    removed_date = db.Column(db.DateTime())
    last_seen_date = db.Column(db.DateTime())

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

    added_date = db.Column(db.DateTime())
    removed_date = db.Column(db.DateTime())
    last_seen_date = db.Column(db.DateTime())