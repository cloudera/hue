
from builtins import object
class Impala(object):
  NAME = 'Impala'
  TYPE = 'impala'

  VERSION = 1
  APP = 'notebook'
  INTERFACE = 'hiveserver2'
  PROPERTIES = [
    {'name': 'server_host', 'value': ''},
    {'name': 'server_port', 'value': ''},
  ]
