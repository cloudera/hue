__test__ = False

if __name__ == '__main__':
    import sys
    # On eventlet<=0.20.0 uncommenting this unpatched import fails test
    # because import_patched did not agressively repatch sub-imported modules cached in sys.modules
    # to be fixed in https://github.com/eventlet/eventlet/issues/368
    # import tests.patcher.shared_import_socket

    import eventlet
    target = eventlet.import_patched('tests.patcher.shared1').shared
    t = target.socket.socket
    import eventlet.green.socket as g
    if not issubclass(t, g.socket):
        print('Fail. Target socket not green: {0} bases {1}'.format(t, t.__bases__))
        sys.exit(1)

    print('pass')
