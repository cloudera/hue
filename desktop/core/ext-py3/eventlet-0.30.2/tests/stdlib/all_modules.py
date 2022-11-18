def get_modules():
    test_modules = [
        'test_select',
        'test_SimpleHTTPServer',
        'test_asynchat',
        'test_asyncore',
        'test_ftplib',
        'test_httplib',
        'test_os',
        'test_queue',
        'test_socket_ssl',
        'test_socketserver',
        #       'test_subprocess',
        'test_thread',
        'test_threading',
        'test_threading_local',
        'test_urllib',
        'test_urllib2_localnet']

    network_modules = [
        'test_httpservers',
        'test_socket',
        'test_ssl',
        'test_timeout',
        'test_urllib2']

    # quick and dirty way of testing whether we can access
    # remote hosts; any tests that try internet connections
    # will fail if we cannot
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(0.5)
        s.connect(('eventlet.net', 80))
        s.close()
        test_modules = test_modules + network_modules
    except socket.error as e:
        print("Skipping network tests")

    return test_modules
