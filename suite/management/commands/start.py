import os
from importlib import import_module

import click

from suite.conf import ENVIRONMENT_VARIABLE


@click.command(help="Starts application.")
def start():
    app_dir = os.environ.get(ENVIRONMENT_VARIABLE).split(".")[0]
    app_module = f"{app_dir}.main"
    m = import_module(app_module)
    m.main()
