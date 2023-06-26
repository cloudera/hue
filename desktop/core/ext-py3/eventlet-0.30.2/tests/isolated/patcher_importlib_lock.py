__test__ = False


def do_import():
    import encodings.idna


if __name__ == '__main__':
    import sys
    import eventlet

    eventlet.monkey_patch()
    threading = eventlet.patcher.original('threading')

    sys.modules.pop('encodings.idna', None)

    # call "import encodings.idna" in a new thread
    thread = threading.Thread(target=do_import)
    thread.start()

    # call "import encodings.idna" in the main thread
    do_import()

    thread.join()
    print('pass')
