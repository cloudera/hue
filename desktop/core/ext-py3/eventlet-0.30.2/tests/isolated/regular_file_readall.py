__test__ = False

if __name__ == '__main__':
    import eventlet
    eventlet.monkey_patch()

    import six
    import io
    import os
    import tempfile

    with tempfile.NamedTemporaryFile() as tmp:
        with io.open(tmp.name, "wb") as fp:
            fp.write(b"content")

        # test BufferedReader.read()
        fd = os.open(tmp.name, os.O_RDONLY)
        fp = os.fdopen(fd, "rb")
        with fp:
            content = fp.read()
        assert content == b'content'

        # test FileIO.read()
        fd = os.open(tmp.name, os.O_RDONLY)
        fp = os.fdopen(fd, "rb", 0)
        with fp:
            content = fp.read()
        assert content == b'content'

        if six.PY3:
            # test FileIO.readall()
            fd = os.open(tmp.name, os.O_RDONLY)
            fp = os.fdopen(fd, "rb", 0)
            with fp:
                content = fp.readall()
            assert content == b'content'

        # test FileIO.readall() (for Python 2 and Python 3)
        with io.open(tmp.name, "rb", 0) as fp:
            content = fp.readall()
        assert content == b'content'

    print("pass")
