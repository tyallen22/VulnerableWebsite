import psycopg2
from psycopg2 import Error

import click
import os
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    try:
        if 'connection' not in g:

        	g.connection = psycopg2.connect(database="testing", user = "postgres", password = "choco", host = "104.197.128.56")
        
        return g.connection

    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)


def close_db(e=None):
    connection = g.pop('connection', None)

    if connection is not None:
        connection.close()
        print("PostgreSQL connection is closed")

def init_db():
    connection = get_db()

def init_app(app):
     # app.teardown_appcontext(close_db)
     app.cli.add_command(init_db_command)

@click.command('init-db')
@with_appcontext
def init_db_command():
     """Clear the existing data and create new tables."""
     init_db()
     click.echo('Initialized the database.')
