from sqlalchemy import create_engine
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    configure_mappers,
)
from suite.conf import settings
from .models import Base


db_session = scoped_session(sessionmaker())

# run configure_mappers after defining all of the models to ensure
# all relationships can be setup
configure_mappers()

engine = create_engine(settings.DATABASE['url'])
db_session.configure(bind=engine)
Base.metadata.bind = engine
