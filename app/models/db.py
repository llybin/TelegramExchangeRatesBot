from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    configure_mappers,
)

from suite.conf import settings

db_session = scoped_session(sessionmaker())
db = declarative_base()

# run configure_mappers after defining all of the models to ensure
# all relationships can be setup
configure_mappers()

engine = create_engine(settings.SQLALCHEMY['url'])
db_session.configure(bind=engine)
db.metadata.bind = engine
