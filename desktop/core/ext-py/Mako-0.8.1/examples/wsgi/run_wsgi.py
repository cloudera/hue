#!/usr/bin/python

import cgi, re, os, posixpath, mimetypes
from mako.lookup import TemplateLookup
from mako import exceptions

root = './'
port = 8000
error_style = 'html' # select 'text' for plaintext error reporting

lookup = TemplateLookup(directories=[root + 'templates', root + 'htdocs'], filesystem_checks=True, module_directory='./modules')

def serve(environ, start_response):
    """serves requests using the WSGI callable interface."""
    fieldstorage = cgi.FieldStorage(
            fp = environ['wsgi.input'],
            environ = environ,
            keep_blank_values = True
    )
    d = dict([(k, getfield(fieldstorage[k])) for k in fieldstorage])

    uri = environ.get('PATH_INFO', '/')
    if not uri:
        uri = '/index.html'
    else:
        uri = re.sub(r'^/$', '/index.html', uri)

    if re.match(r'.*\.html$', uri):
        try:
            template = lookup.get_template(uri)
            start_response("200 OK", [('Content-type','text/html')])
            return [template.render(**d)]
        except exceptions.TopLevelLookupException:
            start_response("404 Not Found", [])
            return ["Cant find template '%s'" % uri]
        except:
            if error_style == 'text':
                start_response("200 OK", [('Content-type','text/plain')])
                return [exceptions.text_error_template().render()]
            else:
                start_response("200 OK", [('Content-type','text/html')])
                return [exceptions.html_error_template().render()]
    else:
        u = re.sub(r'^\/+', '', uri)
        filename = os.path.join(root, u)
        start_response("200 OK", [('Content-type',guess_type(uri))])
        return [file(filename).read()]
 
def getfield(f):
    """convert values from cgi.Field objects to plain values."""
    if isinstance(f, list):
        return [getfield(x) for x in f]
    else:
        return f.value

extensions_map = mimetypes.types_map.copy()
extensions_map.update({
'': 'text/html', # Default
})

def guess_type(path):
    """return a mimetype for the given path based on file extension."""
    base, ext = posixpath.splitext(path)
    if ext in extensions_map:
        return extensions_map[ext]
    ext = ext.lower()
    if ext in extensions_map:
        return extensions_map[ext]
    else:
        return extensions_map['']
 
if __name__ == '__main__':
    import wsgiref.simple_server
    server = wsgiref.simple_server.make_server('', port, serve)
    print "Server listening on port %d" % port
    server.serve_forever()


