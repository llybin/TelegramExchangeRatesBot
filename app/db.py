from sqlalchemy import create_engine
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    configure_mappers,
)
from suite.conf import settings
from .models import Base

# run configure_mappers after defining all of the models to ensure
# all relationships can be setup
configure_mappers()

db_engine = create_engine(settings.DATABASE['url'])

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=db_engine))

Base.metadata.bind = db_engine
