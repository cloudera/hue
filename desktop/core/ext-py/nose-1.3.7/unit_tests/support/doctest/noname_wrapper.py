def __bootstrap__():
    """ Import the code in ``noname_wrapped.not_py`` in file as our own name

    This is a simplified version of the wrapper that setuptools writes for
    dynamic libraries when installing.
    """
    import os
    import imp
    here = os.path.join(os.path.dirname(__file__))
    imp.load_source(__name__, os.path.join(here, 'noname_wrapped.not_py'))

__bootstrap__()
