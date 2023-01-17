import eventlet
import six


if six.PY3:
    def test_pathlib_open_issue_534():
        pathlib = eventlet.import_patched('pathlib')
        path = pathlib.Path(__file__)
        with path.open():
            # should not raise
            pass
