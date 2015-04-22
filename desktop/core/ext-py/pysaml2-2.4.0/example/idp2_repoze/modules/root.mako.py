# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 6
_modified_time = 1357242050.211483
_template_filename=u'templates/root.mako'
_template_uri=u'root.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
_exports = ['css_link', 'pre', 'post', 'css']


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        def pre():
            return render_pre(context.locals_(__M_locals))
        self = context.get('self', UNDEFINED)
        set = context.get('set', UNDEFINED)
        def post():
            return render_post(context.locals_(__M_locals))
        next = context.get('next', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        self.seen_css = set() 
        
        __M_writer(u'\n')
        # SOURCE LINE 7
        __M_writer(u'\n')
        # SOURCE LINE 10
        __M_writer(u'\n')
        # SOURCE LINE 15
        __M_writer(u'\n')
        # SOURCE LINE 22
        __M_writer(u'\n')
        # SOURCE LINE 25
        __M_writer(u'<html>\n<head><title>IDP test login</title>\n    ')
        # SOURCE LINE 27
        __M_writer(unicode(self.css()))
        __M_writer(u'\n    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\n</head>\n<body>\n    ')
        # SOURCE LINE 31
        __M_writer(unicode(pre()))
        __M_writer(u'\n')
        # SOURCE LINE 34
        __M_writer(unicode(next.body()))
        __M_writer(u'\n')
        # SOURCE LINE 35
        __M_writer(unicode(post()))
        __M_writer(u'\n</body>\n</html>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_css_link(context,path,media=''):
    context.caller_stack._push_frame()
    try:
        context._push_buffer()
        self = context.get('self', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'\n')
        # SOURCE LINE 3
        if path not in self.seen_css:
            # SOURCE LINE 4
            __M_writer(u'        <link rel="stylesheet" type="text/css" href="')
            __M_writer(filters.html_escape(unicode(path)))
            __M_writer(u'" media="')
            __M_writer(unicode(media))
            __M_writer(u'">\n')
            pass
        # SOURCE LINE 6
        __M_writer(u'    ')
        self.seen_css.add(path) 
        
        __M_writer(u'\n')
    finally:
        __M_buf, __M_writer = context._pop_buffer_and_writer()
        context.caller_stack._pop_frame()
    __M_writer(filters.trim(__M_buf.getvalue()))
    return ''


def render_pre(context):
    context.caller_stack._push_frame()
    try:
        context._push_buffer()
        __M_writer = context.writer()
        # SOURCE LINE 11
        __M_writer(u'\n    <div class="header">\n        <h1><a href="/">Login</a></h1>\n    </div>\n')
    finally:
        __M_buf, __M_writer = context._pop_buffer_and_writer()
        context.caller_stack._pop_frame()
    __M_writer(filters.trim(__M_buf.getvalue()))
    return ''


def render_post(context):
    context.caller_stack._push_frame()
    try:
        context._push_buffer()
        __M_writer = context.writer()
        # SOURCE LINE 16
        __M_writer(u'\n    <div>\n        <div class="footer">\n            <p>&#169; Copyright 2011 Ume&#229; Universitet &nbsp;</p>\n        </div>\n    </div>\n')
    finally:
        __M_buf, __M_writer = context._pop_buffer_and_writer()
        context.caller_stack._pop_frame()
    __M_writer(filters.trim(__M_buf.getvalue()))
    return ''


def render_css(context):
    context.caller_stack._push_frame()
    try:
        context._push_buffer()
        def css_link(path,media=''):
            return render_css_link(context,path,media)
        __M_writer = context.writer()
        # SOURCE LINE 8
        __M_writer(u'\n    ')
        # SOURCE LINE 9
        __M_writer(unicode(css_link('/css/main.css', 'screen')))
        __M_writer(u'\n')
    finally:
        __M_buf, __M_writer = context._pop_buffer_and_writer()
        context.caller_stack._pop_frame()
    __M_writer(filters.trim(__M_buf.getvalue()))
    return ''


