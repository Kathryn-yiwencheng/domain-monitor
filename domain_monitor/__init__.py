
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify

app = Flask(__name__)


# app should read config from application.cfg

app.config['SQLALCHEMY_DATABASE_URI'] = ''
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

app.config.from_object('config')

moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)