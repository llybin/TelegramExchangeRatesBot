from sqlalchemy import engine_from_config
from sqlalchemy.orm import configure_mappers

from .. import config

# import or define all models here to ensure they are attached to the
# Base.metadata prior to any initialization routines
from .models import *  # flake8: noqa

from .meta import Base, db_session


# run configure_mappers after defining all of the models to ensure
# all relationships can be setup
configure_mappers()

engine = engine_from_config(config['app'])
db_session.configure(bind=engine)
Base.metadata.bind = engine
