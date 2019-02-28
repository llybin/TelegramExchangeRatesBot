import click

from commands.db.commands import (
    current,
    heads,
    makemigrations,
    merge,
    migrate,
    showmigrations,
)


@click.group(help="Subcommands to work with database")
def db():
    pass


db.add_command(current)
db.add_command(heads)
db.add_command(makemigrations)
db.add_command(merge)
db.add_command(migrate)
db.add_command(showmigrations)

