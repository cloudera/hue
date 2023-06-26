__test__ = False

if __name__ == '__main__':
    from eventlet import tpool

    def do():
        print("should not get here")
    try:
        tpool.execute(do)
    except AssertionError:
        print('pass')
