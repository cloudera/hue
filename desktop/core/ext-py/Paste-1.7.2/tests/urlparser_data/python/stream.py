def stream():
    def app(environ, start_response):
        writer = start_response('200 OK', [('Content-type', 'text/html')])
        writer('te')
        writer('st')
        return ['2']
    return app
