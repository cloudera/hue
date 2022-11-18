import tests


def test_import():
    # https://github.com/eventlet/eventlet/issues/238
    # Ensure that it's possible to import eventlet.green.OpenSSL.
    # Most basic test to check Python 3 compatibility.
    try:
        import OpenSSL
    except ImportError:
        raise tests.SkipTest('need pyopenssl')

    import eventlet.green.OpenSSL.SSL
    import eventlet.green.OpenSSL.crypto
    import eventlet.green.OpenSSL.version
