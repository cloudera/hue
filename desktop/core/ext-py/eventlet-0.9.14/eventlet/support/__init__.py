import sys
def get_errno(exc):
    """ Get the error code out of socket.error objects.
    socket.error in <2.5 does not have errno attribute
    socket.error in 3.x does not allow indexing access
    e.args[0] works for all.
    There are cases when args[0] is not errno.
    i.e. http://bugs.python.org/issue6471
    Maybe there are cases when errno is set, but it is not the first argument?
    """

    try:
        if exc.errno is not None: return exc.errno
    except AttributeError:
        pass
    try:
        return exc.args[0]
    except IndexError:
        return None

if sys.version_info[0]<3:
    from sys import exc_clear as clear_sys_exc_info
else:
    def clear_sys_exc_info():
        """No-op In py3k. 
        Exception information is not visible outside of except statements.
        sys.exc_clear became obsolete and removed."""
        pass

if sys.version_info[0]==2 and sys.version_info[1]<5:
    class BaseException:                      # pylint: disable-msg=W0622
        # not subclassing from object() intentionally, because in
        # that case "raise Timeout" fails with TypeError.
        pass
else:
    from __builtin__ import BaseException
