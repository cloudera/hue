__test__ = False

if __name__ == '__main__':
    import eventlet
    eventlet.monkey_patch()
    import subprocess
    import gc

    p = subprocess.Popen(['ls'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # the following line creates a _SocketDuckForFd(3) and .close()s it, but the
    # object has not been collected by the GC yet
    p.communicate()

    f = open('/dev/null', 'rb')    # f.fileno() == 3
    gc.collect() # this calls the __del__ of _SocketDuckForFd(3), close()ing it again

    f.close() # OSError, because the fd 3 has already been closed
    print('pass')
