import sys

from dsml import *

d = DSMLParser(open(sys.argv[1],'r'),DSMLv1Handler)
d.parse()
