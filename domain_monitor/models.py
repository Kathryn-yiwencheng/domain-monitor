
#SQLAlchemy models country, zone, domain tables - what if domain is expired and renew by someone else. 
#if it is expried and renew. With version number 

"""
Contains all Database configuration, models and relationships.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from domain_monitor.config import SQLALCHEMY_DATABASE_URI # Import local database URI from Config File

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 



class Country(db.Model):
    __tablename__ = 'country'

    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String())


class Zone(db.Model):
    __tablename__ = 'zone'

    id = db.Column(db.Integer, primary_key=True)
    zone = db.Column(db.String())

class Domans(db.Model):
    __tablename__ = 'domain'

    zone_id = db.Column(db.Integer, db.ForeignKey('zone.id'), primary_key=True)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'), primary_key=True)
    domain = db.Column(db.Integer())
    create_date = db.Column(db.DateTime())
    update_date = db.Column(db.DateTime())
    is_dead = db.Column(db.String())
    a = db.Column(db.String())
    ns = db.Column(db.String())
    cname = db.Column(db.String())
    mx = db.Column(db.String())
    txt = db.Column(db.String())



