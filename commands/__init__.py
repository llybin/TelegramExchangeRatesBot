import click

from .db import db


@click.group()
def cli():
    pass


cli.add_command(db)
