# -*- coding: utf-8 -*-
from tgext.pluggable import PluggableSession
import tg

import logging

log = logging.getLogger(__name__)

DBSession = PluggableSession()
DeclarativeBase = None

def init_model(app_session):
    DBSession.configure(app_session)

FlatPage = None
FlatFile = None

def configure_models():
    global FlatPage, FlatFile, DeclarativeBase
    if tg.config.get('use_sqlalchemy', False):
        log.info('Configuring FlatPages for SQLAclhemy')
        from .sqla import FlatPage, FlatFile
        from sqlalchemy.ext.declarative import declarative_base
        DeclarativeBase = declarative_base()
    elif tg.config.get('use_ming', False):
        log.info('Configuring FlatPages for Ming')
        from .ming import FlatPage, FlatFile
    else:
        raise ValueError('FlatPages should be used with SQLAclhemy or Ming')
