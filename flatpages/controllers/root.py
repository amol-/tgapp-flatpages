# -*- coding: utf-8 -*-
"""Main Controller"""
from io import BytesIO
from markupsafe import Markup
from tg import TGController, predicates, config, abort, override_template, tmpl_context, Request
from tg import expose, flash, require, url, lurl, request, redirect, validate, hooks
from tg.caching import cached_property
from tg.decorators import with_trailing_slash
from tgext.admin import AdminController, AdminConfig, CrudRestControllerConfig
from tgext.admin.widgets import BootstrapAdminTableFiller
from tgext.crud import EasyCrudRestController, addopts
from tgext.pluggable import instance_primary_key, app_model, plug_url
from tw2.core import Deferred, CSSSource
from tw2.forms import SingleSelectField, TextField, FileValidator

from flatpages import model
from flatpages.lib.widgets import MarkitUpArea
from flatpages.model import DBSession

from tgext.admin.layouts import BootstrapAdminLayout
from depot.middleware import DepotMiddleware
from tg.exceptions import HTTPNotFound


class FlatPagesAdminConfig(AdminConfig):
    include_left_menu = False
    layout = BootstrapAdminLayout
    default_index_template = 'kajiki:flatpages.templates.manage'

    class flatfile(CrudRestControllerConfig):
        class defaultCrudRestController(EasyCrudRestController):
            response_type = 'text/html'
            remember_values = ['file']

            _get_current_user = lambda: instance_primary_key(request.identity['user'])

            __form_options__ = {
                '__hide_fields__': ['author'],
                '__omit_fields__': ['uid', '_id', 'updated_at', 'created_at'],
                '__field_widget_args__': addopts(author={'value': Deferred(_get_current_user)},
                                                 file={'required': True})
            }

            __form_edit_options__ = {
                '__field_widget_args__': addopts(**{'file': {'required': False}})
            }

            __table_options__ = {
                '__omit_fields__': ['_id', 'uid', 'author_id', 'created_at'],
                '__xml_fields__': ['file'],

                'file': lambda filler, o: Markup('<a href="%s">%s</a>' % (o.url, o.url))
            }

    class flatpage(CrudRestControllerConfig):
        class defaultCrudRestController(EasyCrudRestController):
            response_type = 'text/html'
            crud_resources = [CSSSource(location='headbottom',
                                       src='''
        .crud-sidebar .active {
            font-weight: bold;
            border-left: 3px solid #eee;
        }

        @media (max-width: 991px) {
            .pull-sm-right {
                float: right;
            }
        }

        @media (min-width: 992px) {
            .pull-md-right {
                float: right;
            }
        }
        ''')]

            # Helpers to retrieve form data
            _get_current_user = lambda: instance_primary_key(request.identity['user'])
            _get_templates = lambda: config['_flatpages']['templates']
            if config.get('use_sqlalchemy', False):
                _get_permissions = lambda: [
                    ('public', 'Public'), ('not_anonymous', 'Only Registered Users')] + \
                    DBSession.query(app_model.Permission.permission_name,
                                    app_model.Permission.description).all()
            else:
                _get_permissions = lambda: [
                    ('public', 'Public'), ('not_anonymous', 'Only Registered Users')] + \
                    [(p.permission_name, p.description)
                     for p in app_model.Permission.query.find().all()]

            __form_options__ = {
                '__hide_fields__': ['author', 'updated_at'],
                '__omit_fields__': ['uid', '_id', 'created_at'],
                '__field_order__': ['slug', 'title', 'template', 'required_permission'],
                '__field_widget_types__': addopts(**{'template': SingleSelectField,
                                           'slug': TextField,
                                           'title': TextField,
                                           'required_permission': SingleSelectField,
                                           'content': MarkitUpArea}),
                '__field_widget_args__': addopts(**{
                    'author': {'value': Deferred(_get_current_user)},
                    'required_permission': {'prompt_text': None,
                                            'options': Deferred(_get_permissions)},
                    'content': {'rows': 20},
                    'template': {'prompt_text': None,
                                 'options': Deferred(_get_templates)},
                    })
            }

            __table_options__ = {
                '__omit_fields__': ['_id', 'uid', 'author_id', 'created_at', 'template', 'content'],
                '__xml_fields__': ['slug'],

                'slug': lambda filler, o: Markup('<a href="%s">%s</a>' % (o.url, o.slug)),
                '__actions__': lambda self, obj: request.controller_state.controller._build_actions(obj)
            }

            def _build_actions(self, obj):
                baseactions = super(self.table_filler.__class__, self.table_filler).__actions__(obj)
                if config['_flatpages']['format'] == 'rst':
                    extraactions = Markup('''
        <a href="%s/download" class="btn btn-default">
            <span class="glyphicon glyphicon-download-alt"></span>
        </a>''' % instance_primary_key(obj))
                else:
                    extraactions = ''
                return extraactions + baseactions

            @expose(content_type='application/pdf')
            def download(self, pageid):
                from rst2pdf.createpdf import RstToPdf
                p = model.FlatPage.by_id(pageid) or abort(404)
                out = BytesIO()

                rst2pdf = RstToPdf()
                rst2pdf.createPdf(p.content, output=out)

                out.seek(0)
                return out.read()


class FlatPagesAdminController(AdminController):
    allow_only = predicates.has_permission('flatpages')

    def __init__(self):
        super(FlatPagesAdminController, self).__init__(
            [model.FlatPage,
             model.FlatFile],
            DBSession.wrapped_session,
            config_type=FlatPagesAdminConfig
        )

    @expose()
    @with_trailing_slash
    def index(self, *args, **kwargs):
        return super(FlatPagesAdminController, self).index(*args, **kwargs)


class RootController(TGController):
    CACHE_EXPIRE = 7*86400  # 7 Days

    depotmiddleware = DepotMiddleware(HTTPNotFound(), '/pages')

    @expose()
    def _default(self, page=None, *args, **kw):

        page_slug = dict(slug=page)
        hooks.notify('flatpages.before_override_template', args=(page_slug, self))

        page = model.FlatPage.by_slug(page_slug['slug'])

        if page is None:
            abort(404, 'Page not found')


        permission = page.required_permission
        if permission and permission != 'public':
            if permission == 'not_anonymous':
                predicate = predicates.not_anonymous()
            else:
                predicate = predicates.has_permission(permission)

            if not predicate.is_met(request.environ):
                abort(403, 'Forbidden')

        try:
            userid = request.identity['user'].user_id
        except:
            userid = None

        override_template(RootController._default, page.template)

        hooks.notify('flatpages.after_override_template', (page, self))
        return dict(page=page,
                    tg_cache={'expire': self.CACHE_EXPIRE,
                              'key': '%s-%s-%s' % (page.slug, page.updated_at, userid)})

    @expose(content_type='text/html')
    def flatfiles(self, *args, **kwargs):
        r = Request.blank('/pages/flatfiles/' + '/'.join(args))
        return r.get_response(self.depotmiddleware)

    @cached_property
    def manage(self):
        return FlatPagesAdminController()
