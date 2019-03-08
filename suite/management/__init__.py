import click

from .commands.db import db
from .commands.start import start
from .commands.test import test


@click.group()
def cli():
    pass


cli.add_command(db)
cli.add_command(start)
cli.add_command(test)
