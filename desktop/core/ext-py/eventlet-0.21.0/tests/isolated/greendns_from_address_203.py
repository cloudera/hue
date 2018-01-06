__test__ = False

if __name__ == '__main__':
    import eventlet
    from eventlet.support.dns import reversename
    eventlet.monkey_patch(all=True)
    reversename.from_address('127.0.0.1')
    print('pass')
