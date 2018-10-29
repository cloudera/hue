import os
__test__ = False
shared = None


if os.environ.get('eventlet_test_in_progress') == 'yes':
    # pyopenssl imported urllib before we could patch it
    # we can ensure this shared module was not imported
    # https://github.com/eventlet/eventlet/issues/362
    import tests.patcher.shared_import_socket as shared
    _ = shared  # mask unused import error
