# Database Interface Documentation

## SQLAlchemy with Flask-SQLAlchemy

### Documentation

Quickstart with Flask: https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/#a-minimal-application
DB Models: https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
Querying DB: https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/#querying-records

### Usage

Create data models in the models.py file

Query the database from anywhere

## Alembic with Flask-Migrate

### Documentation
Main docs: https://flask-migrate.readthedocs.io/en/latest/#example

Alembic docs: https://alembic.sqlalchemy.org/en/latest/tutorial.html#the-migration-environment

### Usage

YOU DO NOT NEED TO RUN `flask db init` AGAIN

To create a migration run: `flask db migrate -m "WHAT YOU CHANGED"`

You should do this everytime you change the DB models

This will create a new file in the migrations/versions/ directory explaining your changes

To apply migrations run: `flask db upgrade`

To upgrade live database and run migrations: `heroku run flask db upgrade`

You should do this everytime you push if the DB models were edited