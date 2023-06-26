import os
import socket
__test__ = False
_ = socket  # mask unused import error

# prevent accidental imports
assert os.environ.get('eventlet_test_in_progress') == 'yes'
