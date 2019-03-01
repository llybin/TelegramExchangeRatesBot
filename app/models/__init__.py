from sqlalchemy import create_engine
from sqlalchemy.orm import configure_mappers

from suite.conf import settings

# import or define all models here to ensure they are attached to the
# Base.metadata prior to any initialization routines
from .models import *  # flake8: noqa

from .meta import Base, db_session


# run configure_mappers after defining all of the models to ensure
# all relationships can be setup
configure_mappers()

engine = create_engine(settings.SQLALCHEMY['url'])
db_session.configure(bind=engine)
Base.metadata.bind = engine
