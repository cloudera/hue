import sys
sys.modules['ssl'] = None
sys.modules['_hashlib'] = None

try:
   import memdbg
except Exception as e:
   pass

from twisted.scripts.trial import run
run()
