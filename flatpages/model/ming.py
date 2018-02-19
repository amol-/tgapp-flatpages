from __future__ import absolute_import
from contextlib import closing
import os

from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty
from ming.odm.declarative import MappedClass
from ming.odm.mapper import MapperExtension
from bson import ObjectId

from flatpages import model
from tgext.pluggable import app_model, primary_key, plug_url

from datetime import datetime
from tg import config
from tg.caching import cached_property
from flatpages.lib.formatters import FORMATTERS
from depot.fields.ming import UploadedFileProperty


class UpdateDate(MapperExtension):
    def before_update(self, instance, state, sess):
        instance.updated_at = datetime.utcnow()


class FlatPage(MappedClass):
    class __mongometa__:
        session = model.DBSession
        name = 'flatpages_page'
        unique_indexes = [('slug', )]
        extensions = [ UpdateDate ]

    _id = FieldProperty(s.ObjectId)

    template = FieldProperty(s.String, if_missing=config['_flatpages'].get('templates')[0][0])
    slug = FieldProperty(s.String, required=True)
    title = FieldProperty(s.String, required=True)
    content = FieldProperty(s.String, if_missing='')
    required_permission = FieldProperty(s.String)

    updated_at = FieldProperty(s.DateTime, if_missing=datetime.utcnow)
    created_at = FieldProperty(s.DateTime, if_missing=datetime.utcnow)

    author_id = ForeignIdProperty('User')
    author = RelationProperty('User')

    @classmethod
    def by_id(cls, _id):
        return cls.query.get(ObjectId(_id))

    @classmethod
    def by_slug(cls, slug):
        return cls.query.find(dict(slug=slug)).first()

    @cached_property
    def url(self):
        return plug_url('flatpages', '/' + self.slug)

    @classmethod
    def all_pages(cls):
        """Returns a list of tuples with title and url of all the flat pages"""
        return [(page.title, page.url) for page in cls.query.find()]

    @cached_property
    def html_content(self):
        format = config['_flatpages']['format']
        formatter = FORMATTERS[format]

        content = self.content
        if content.startswith('file://'):
            package_path = config['paths']['root']
            file_path = os.path.join(package_path, content[7:])
            with closing(open(file_path)) as f:
                content = f.read()

        return formatter(content)


class FlatFile(MappedClass):
    class __mongometa__:
        session = model.DBSession
        name = 'flatpages_file'
        unique_indexes = [('name')]
        extensions = [ UpdateDate ]

    _id = FieldProperty(s.ObjectId)

    name = FieldProperty(s.String, required=True)
    file = UploadedFileProperty(upload_storage='flatfiles')

    updated_at = FieldProperty(s.DateTime, if_missing=datetime.utcnow)
    created_at = FieldProperty(s.DateTime, if_missing=datetime.utcnow)

    author_id = ForeignIdProperty('User')
    author = RelationProperty('User')

    @cached_property
    def url(self):
        return plug_url('flatpages', '/flatfiles/' + self.file.file_id)
