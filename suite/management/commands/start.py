import importlib
import os

import click

from suite.conf import ENVIRONMENT_VARIABLE


@click.command(help="Starts application.")
def start():
    app_dir = os.environ.get(ENVIRONMENT_VARIABLE).split('.')[0]
    m = importlib.import_module(app_dir)
    m.start_app()
