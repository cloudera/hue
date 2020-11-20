import os

dirName = os.path.dirname(os.path.dirname(__file__))
exec(open(os.path.join(dirName, "db_config.py"), "r").read())
