# -*- coding: utf-8 -*-
"""Setup the flatpages application"""
from __future__ import print_function

from flatpages import model
from tgext.pluggable import app_model

import logging

log = logging.getLogger(__name__)


def bootstrap(command, conf, vars):
    log.info('Bootstrapping flatpages...')
    # creating a new permission and assign it to managers group
    
    p = app_model.Permission(permission_name='flatpages', description='Can manage flat pages')

    try:  # sqlalchemy
        g = model.DBSession.query(app_model.Group).filter_by(group_name='managers').first()
    except:  # ming
        g = app_model.Group.query.find(dict(group_name='managers')).first()
    if g:
        p.groups = [g]

    try:
        model.DBSession.add(p)
    except AttributeError:
        pass  # ming doesn't need to add

    model.DBSession.flush()
