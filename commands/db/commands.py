import os
import datetime
from functools import wraps

import click
from alembic import command
from alembic.config import Config
from alembic.util.exc import CommandError

from suite.conf import settings

alembic_ini_path = os.path.join(settings.BASE_DIR, '..', 'alembic.ini')
alembic_cfg = Config(alembic_ini_path)
alembic_cfg.set_main_option('sqlalchemy.url', settings.SQLALCHEMY['url'])


def get_migration_name_timestamp():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M")


def get_auto_migration_name():
    return f"auto_{get_migration_name_timestamp()}"


def get_merge_migration_name():
    return f"merge_{get_migration_name_timestamp()}"


def catch_alembic_error(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)

        except CommandError as e:
            click.echo(f"Error: {e}")

        else:
            click.echo("Done.")

    return wrapper


@click.command(help="Updates database schema. Manages both apps with migrations and those without.")
@click.option("--migration_name",
              default="head",
              help="Database state will be brought to the state after that migration.")
@catch_alembic_error
def migrate(migration_name):
    """Upgrade to a later version."""

    command.upgrade(alembic_cfg, migration_name)


@click.command(help="Creates new migration(s) for apps.")
@click.option("-m", "--message", default=get_auto_migration_name, help="Apply a message to the revision")
@click.option("--empty", is_flag=True, help="Create an empty migration.")
@catch_alembic_error
def makemigrations(message, empty):
    """Create new migration."""

    # TODO: don't create empty migration when autogenerate
    command.revision(
        alembic_cfg,
        message=message,
        autogenerate=not empty,
    )


@click.command(help="Creates merge revision.")
@click.argument('revisions', nargs=-1, required=True)
@click.option("-m", "--message", default=get_merge_migration_name, help="Apply a message to the revision")
@catch_alembic_error
def merge(revisions, message):
    """Create merge revision."""

    if len(revisions) < 2:
        raise CommandError("Enter two or more revisions.")

    command.merge(alembic_cfg, revisions, message)


@click.command(help="Show current revision")
@click.option('-v', '--verbose', is_flag=True)
@catch_alembic_error
def current(verbose):
    """Show current revision."""

    command.current(alembic_cfg, verbose)


@click.command(help="Shows all available migrations for the current project.")
@click.option('-v', '--verbose', is_flag=True)
@catch_alembic_error
def showmigrations(verbose):
    """List revisions in chronological order."""

    command.history(alembic_cfg, verbose=verbose)


@click.command(help="Shows all latest revisions for the current project.")
@click.option('--resolve-dependencies', is_flag=True, help='Treat dependencies as down revisions.')
@click.option('-v', '--verbose', is_flag=True)
@catch_alembic_error
def heads(resolve_dependencies, verbose):
    """Show latest revisions."""

    command.heads(alembic_cfg, resolve_dependencies, verbose)
