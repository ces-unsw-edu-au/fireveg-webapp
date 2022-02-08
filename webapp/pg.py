import os
import psycopg2
from configparser import ConfigParser
from flask import current_app, g
from flask.cli import with_appcontext


def get_pg_connection():
    if 'pg' not in g:
        filename = os.path.join(current_app.instance_path, 'database.ini')
        section = 'aws-lght-sl'
        parser = ConfigParser()
        parser.read(filename)
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))
        g.pg = psycopg2.connect(**db)
        return g.pg


def close_pg(e=None):
    pg = g.pop('pg', None)

    if pg is not None:
        pg.close()


def init_app(app):
    app.teardown_appcontext(close_pg)
