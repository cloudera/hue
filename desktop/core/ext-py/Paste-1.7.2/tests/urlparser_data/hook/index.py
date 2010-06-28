def application(environ, start_response):
    start_response('200 OK', [('Content-type', 'text/html')])
    return ['index: %s' % environ['app.user']]

