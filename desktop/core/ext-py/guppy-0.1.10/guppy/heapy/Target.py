import os, sys
class Target:
    def __init__(self):
	self.wd = os.getcwd()
	self.pid = os.getpid()
	self.sys = sys
	
