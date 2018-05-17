# -*- coding: utf-8 -*-
"""The tgapp-flatpages package"""
import tg


def plugme(app_config, options):
    config = {'templates': options.get('templates', [('kajiki:flatpages.templates.page', 'default')]),
              'format': options.get('format', 'html')}
    app_config['_flatpages'] = config
    from flatpages import model
    tg.configuration.milestones.config_ready.register(model.configure_models)
    return dict(appid='pages', global_helpers=False)
