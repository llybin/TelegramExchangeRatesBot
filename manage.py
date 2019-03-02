#!/usr/bin/env python
import os


if __name__ == '__main__':
    os.environ.setdefault('SETTINGS_MODULE', 'app.settings')

    from suite.management import cli
    cli()
