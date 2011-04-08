try:
    import greenlet
    getcurrent = greenlet.greenlet.getcurrent
    GreenletExit = greenlet.greenlet.GreenletExit
    greenlet = greenlet.greenlet
except ImportError, e:
    raise
    try:
        from py.magic import greenlet
        getcurrent = greenlet.getcurrent
        GreenletExit = greenlet.GreenletExit
    except ImportError:
        try:
            from stackless import greenlet
            getcurrent = greenlet.getcurrent
            GreenletExit = greenlet.GreenletExit
        except ImportError:
            try:
                from support.stacklesss import greenlet, getcurrent, GreenletExit
                (greenlet, getcurrent, GreenletExit) # silence pyflakes
            except ImportError, e:
                raise ImportError("Unable to find an implementation of greenlet.")
