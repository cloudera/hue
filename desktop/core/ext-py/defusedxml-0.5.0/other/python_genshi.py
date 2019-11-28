#!/usr/bin/python
import sys
from pprint import pprint
from genshi.input import XMLParser

with open(sys.argv[1]) as f:
    parser = XMLParser(f)
    pprint(list(parser))

