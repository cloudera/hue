__test__ = False

if __name__ == '__main__':
    import eventlet
    eventlet.monkey_patch()

    from six.moves.BaseHTTPServer import (
        HTTPServer,
        BaseHTTPRequestHandler,
    )
    import threading

    server = HTTPServer(('localhost', 0), BaseHTTPRequestHandler)
    thread = threading.Thread(target=server.serve_forever)

    # Before fixing it the code would never go pass this line because:
    # * socketserver.BaseServer that's used behind the scenes here uses
    #   selectors.PollSelector if it's available and we don't have green poll
    #   implementation so this just couldn't work
    # * making socketserver use selectors.SelectSelector wasn't enough as
    #   until now we just failed to monkey patch selectors module
    #
    # Due to the issues above this thread.start() call effectively behaved
    # like calling server.serve_forever() directly in the current thread
    #
    # Original report: https://github.com/eventlet/eventlet/issues/249
    thread.start()

    server.shutdown()
    print('pass')
