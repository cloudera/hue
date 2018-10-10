__test__ = False

if __name__ == '__main__':
    import subprocess as original
    from eventlet.green import subprocess as green

    cases = (
        'CalledProcessError',
        'TimeoutExpired',
    )
    for c in cases:
        if hasattr(original, c):
            assert getattr(green, c) is getattr(original, c), c
    print('pass')
