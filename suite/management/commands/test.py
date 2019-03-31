import unittest

import click
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database, drop_database

from suite.database import init_sqlalchemy
from suite.conf import settings
from suite.management.commands.db import command_migrate, alembic_cfg


@click.command(help="Runs tests.")
@click.argument('tests_path', required=False)
def test(tests_path=None):
    loader = unittest.TestLoader()
    if tests_path:
        try:
            tests = loader.loadTestsFromName(tests_path)
            if not tests._tests:
                tests = loader.discover(tests_path, top_level_dir='.')
        except ModuleNotFoundError:
            tests = loader.discover('.')
    else:
        tests = loader.discover('.')

    test_runner = unittest.TextTestRunner(verbosity=2)

    settings.SENTRY_URL = None
    settings.BOT_TOKEN = None
    settings.DEVELOPER_BOT_TOKEN = None
    settings.DEVELOPER_USER_ID = None

    db_url, db_name = settings.DATABASE['url'].rsplit('/', 1)
    settings.DATABASE['url'] = f"{db_url}/test_{db_name}"

    db_engine = create_engine(settings.DATABASE['url'])
    init_sqlalchemy(db_engine)

    alembic_cfg.set_main_option('sqlalchemy.url', settings.DATABASE['url'])

    click.echo("Creating DB...")

    if database_exists(db_engine.url):
        drop_database(db_engine.url)

    create_database(db_engine.url)

    result = None
    try:
        click.echo("Migrating DB...")
        command_migrate('head')

        click.echo("Running tests...")
        result = test_runner.run(tests)
    finally:
        click.echo("Deleting DB...")
        drop_database(db_engine.url)

    if not result or result.failures or result.errors:
        exit(-1)
