# -*- encoding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 6
_modified_time = 1367126126.936375
_template_filename='htdocs/login.mako'
_template_uri='login.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding='utf-8'
_exports = []


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    pass
def _mako_inherit(template, context):
    _mako_generate_namespaces(context)
    return runtime._inherit_from(context, u'root.mako', _template_uri)
def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        redirect_uri = context.get('redirect_uri', UNDEFINED)
        key = context.get('key', UNDEFINED)
        action = context.get('action', UNDEFINED)
        authn_reference = context.get('authn_reference', UNDEFINED)
        login = context.get('login', UNDEFINED)
        password = context.get('password', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n\n<h1>Please log in</h1>\n<p class="description">\n    To register it\'s quite simple: enter a login and a password\n</p>\n\n<form action="')
        # SOURCE LINE 8
        __M_writer(unicode(action))
        __M_writer(u'" method="post">\n    <input type="hidden" name="key" value="')
        # SOURCE LINE 9
        __M_writer(unicode(key))
        __M_writer(u'"/>\n    <input type="hidden" name="authn_reference" value="')
        # SOURCE LINE 10
        __M_writer(unicode(authn_reference))
        __M_writer(u'"/>\n    <input type="hidden" name="redirect_uri" value="')
        # SOURCE LINE 11
        __M_writer(unicode(redirect_uri))
        __M_writer(u'"/>\n\n    <div class="label">\n        <label for="login">Username</label>\n    </div>\n    <div>\n        <input type="text" name="login" value="')
        # SOURCE LINE 17
        __M_writer(unicode(login))
        __M_writer(u'"/><br/>\n    </div>\n\n    <div class="label">\n        <label for="password">Password</label>\n    </div>\n    <div>\n        <input type="password" name="password"\n               value="')
        # SOURCE LINE 25
        __M_writer(unicode(password))
        __M_writer(u'"/>\n    </div>\n\n    <input class="submit" type="submit" name="form.submitted" value="Log In"/>\n</form>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


