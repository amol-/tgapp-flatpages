# -*- coding: utf-8 -*-

"""WebHelpers used in tgapp-flatpages."""

from markupsafe import Markup
from tg import config

default_index_template_manage = config['_flatpages'].get('default_index_template_manage',
                                           'genshi:flatpages.templates.manage')
default_index_template_page = config['_flatpages'].get('default_index_template_page',
                                         'genshi:flatpages.templates.page')
