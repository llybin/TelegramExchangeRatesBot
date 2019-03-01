import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SQLALCHEMY = {
    'url': 'postgresql://postgres:@db:5432/postgres',
}
