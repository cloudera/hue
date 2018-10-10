import distutils.version

import greenlet
getcurrent = greenlet.greenlet.getcurrent
GreenletExit = greenlet.greenlet.GreenletExit
preserves_excinfo = (distutils.version.LooseVersion(greenlet.__version__)
                     >= distutils.version.LooseVersion('0.3.2'))
greenlet = greenlet.greenlet
