import importlib
import os

import click

from suite.conf import ENVIRONMENT_VARIABLE


@click.command(help="Starts application.")
def start():
    app_dir = os.environ.get(ENVIRONMENT_VARIABLE).split('.')[0]
    app_module = f'{app_dir}.main'
    m = importlib.import_module(app_module)
    m.main()
