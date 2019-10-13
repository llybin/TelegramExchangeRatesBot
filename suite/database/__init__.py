from sqlalchemy import event, orm, schema
from sqlalchemy.ext.declarative import declarative_base

from zope.sqlalchemy import register

from . import models

Session = orm.scoped_session(orm.sessionmaker())
register(Session, keep_session=True)

metadata = schema.MetaData()

BaseObject = declarative_base(metadata=metadata)


def init_sqlalchemy(engine):
    Session.configure(bind=engine)
    metadata.bind = engine


def enable_sql_two_phase_commit(config, enable=True):
    Session.configure(twophase=enable)


@event.listens_for(BaseObject, "class_instrument")
def register_model(cls):
    setattr(models, cls.__name__, cls)


@event.listens_for(BaseObject, "class_uninstrument")
def unregister_model(cls):
    if hasattr(models, cls.__name__):
        delattr(models, cls.__name__)


__all__ = [
    "BaseObject",
    "Session",
    "metadata",
    "init_sqlalchemy",
    "enable_sql_two_phase_commit",
    "models",
]
