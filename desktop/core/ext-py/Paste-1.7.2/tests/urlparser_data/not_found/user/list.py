def application(environ, start_response):
    start_response('200 OK', [('Content-type', 'text/plain')])
    return ['user: %s' % environ.get('app.user')]
