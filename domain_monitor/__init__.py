
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask

app = Flask(__name__)

# app should read config from application.cfg

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

import domain_monitor.models