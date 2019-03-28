import unittest

import click
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database, drop_database

from suite.database import init_sqlalchemy
from suite.conf import settings
from suite.management.commands.db import command_migrate, alembic_cfg


@click.command(help="Runs tests.")
def test():
    loader = unittest.TestLoader()
    tests = loader.discover('.')
    test_runner = unittest.TextTestRunner(verbosity=2)

    settings.SENTRY_URL = None

    db_url, db_name = settings.DATABASE['url'].rsplit('/', 1)
    settings.DATABASE['url'] = f"{db_url}/test_{db_name}"

    db_engine = create_engine(settings.DATABASE['url'])
    init_sqlalchemy(db_engine)

    alembic_cfg.set_main_option('sqlalchemy.url', settings.DATABASE['url'])

    click.echo("Creating DB...")

    if database_exists(db_engine.url):
        drop_database(db_engine.url)

    create_database(db_engine.url)

    try:
        click.echo("Migrating DB...")
        command_migrate('head')

        click.echo("Running tests...")
        test_runner.run(tests)
    finally:
        click.echo("Deleting DB...")
        drop_database(db_engine.url)
