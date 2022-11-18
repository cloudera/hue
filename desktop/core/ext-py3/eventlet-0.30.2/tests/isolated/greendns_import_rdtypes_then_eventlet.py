__test__ = False

if __name__ == '__main__':
    import dns.rdtypes
    import eventlet.support.greendns
    # AttributeError: 'module' object has no attribute 'dnskeybase'
    # https://github.com/eventlet/eventlet/issues/479
    print('pass')
