# -*- coding: utf-8 -*-

"""WebHelpers used in tgapp-flatpages."""

from markupsafe import Markup
from tg import config


def translated_pages(lang=None):
    """Returns all the flat pages that are translated in the given language.

    a page is considered translated if it's slug (url) ends in `-it` `-es` and so on
    if `lang` is not provided then the language of the browser of the user is used
    """
    from flatpages.model import FlatPage
    if not lang:
        from tg.i18n import get_lang
        lang = get_lang(all=False)[0]
    pages = FlatPage.all_pages()
    # p[0] -> title  # p[1] -> url
    return ((p[0], p[1]) for p in pages if p[1].endswith('-' + lang))
