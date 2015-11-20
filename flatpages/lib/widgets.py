# -*- coding: utf-8 -*-
from tg import lurl, config
from tw2.core import CSSLink, JSLink, JSSource
from tw2.forms import TextArea


class MarkupLanguageCSSLink(CSSLink):
    def prepare(self):
        super(MarkupLanguageCSSLink, self).prepare()
        self.link = str(self.link).format(language=config['_flatpages']['format'])


class MarkupLanguageJSLink(JSLink):
    def prepare(self):
        super(MarkupLanguageJSLink, self).prepare()
        self.link = str(self.link).format(language=config['_flatpages']['format'])


class MarkitUpArea(TextArea):
    resources = [
        CSSLink(link=lurl('/_pluggable/flatpages/markitup/skins/simple/style.css')),
        MarkupLanguageCSSLink(link=lurl('/_pluggable/flatpages/markitup/sets/{language}/style.css')),
        JSLink(link=lurl('/_pluggable/flatpages/jquery.js'), location='bodybottom'),
        JSLink(link=lurl('/_pluggable/flatpages/markitup/jquery.markitup.js'), location='bodybottom'),
        MarkupLanguageJSLink(link=lurl('/_pluggable/flatpages/markitup/sets/{language}/set.js'), location='bodybottom'),
        JSSource(src='var jQflatpages = jQuery.noConflict(true);'),
        JSSource(src='jQflatpages("#sx_content").markItUp(mySettings)')
    ]
