# module for flask to connect to sql database

import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def empty_tbl_products():
    db = get_db()

    with current_app.open_resource('schema_tbl_products.sql') as f:
        db.executescript(f.read().decode('utf8'))


def init_db():
    empty_tbl_products()


@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')


@click.command('dump-db')
@with_appcontext
def dump_db_command():
    db = get_db()
    with open('dump.sql', 'w') as f:
        for line in db.iterdump():
            f.write('%s\n' % line)


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(dump_db_command)


