import click

from .commands.db import db
from .commands.start import start
from .commands.test import test
from .commands.newsletter import newsletter


@click.group()
def cli():
    pass


cli.add_command(db)
cli.add_command(newsletter)
cli.add_command(start)
cli.add_command(test)
