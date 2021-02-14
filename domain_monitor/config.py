import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

# Dev configuration with SQLite3
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/app.db'

# Prod configuration with PostgreSQL
# SQLALCHEMY_DATABASE_URI='postgresql+psycopg2://user:password@mydbhost:5432/domain_monitor'
