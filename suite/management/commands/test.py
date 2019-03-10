import importlib
import os
import unittest

import click
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database, drop_database

from suite.conf import settings, ENVIRONMENT_VARIABLE
from suite.management.commands.db import command_migrate, alembic_cfg


@click.command(help="Runs tests.")
def test():
    app_dir = os.environ.get(ENVIRONMENT_VARIABLE).split('.')[0]
    app_module = f'{app_dir}.db'
    app_db_module = importlib.import_module(app_module)

    msg = 'Module <app_dir>.db must contain: engine, db_session, Base'
    assert getattr(app_db_module, 'engine', None), msg
    assert getattr(app_db_module, 'db_session', None), msg
    assert getattr(app_db_module, 'Base', None), msg

    loader = unittest.TestLoader()
    tests = loader.discover('.')
    test_runner = unittest.TextTestRunner(verbosity=2)

    db_url, db_name = settings.DATABASE['url'].rsplit('/', 1)
    settings.DATABASE['url'] = f"{db_url}/test_{db_name}"

    click.echo("Creating DB...")

    engine = create_engine(settings.DATABASE['url'])

    # reload models db
    app_db_module.engine.dispose()
    app_db_module.db_session.configure(bind=engine)
    app_db_module.Base.metadata.bind = engine

    # reload alembic
    alembic_cfg.set_main_option('sqlalchemy.url', settings.DATABASE['url'])

    if database_exists(engine.url):
        drop_database(engine.url)

    create_database(engine.url)

    try:
        click.echo("Migrating DB...")
        command_migrate('head')

        click.echo("Running tests...")
        test_runner.run(tests)
    finally:
        click.echo("Deleting DB...")
        drop_database(engine.url)
