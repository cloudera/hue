#._cv_part guppy.gsl.FileIO

class TestPath:
    _path_using_io = (
	'abspath', 'curdir', 'exists', 'expanduser', 'expandvars',
	'getatime', 'getctime', 'getmtime', 'getsize',
	'isfile', 'islink', 'ismount', 'realpath',
	'samefile', 'sameopenfile', 'samestat', 
	'walk', 
	
	)
    def __init__(self, os):
	for name in dir(os.path):
	    if (not name.startswith('_') and
		name not in self._path_using_io):
		setattr(self, name, getattr(os.path, name))

class TestIO:
    def __init__(self, mod):
	os = mod._root.os
	for name in mod.os_common:
	    setattr(self, name, getattr(os, name))
	self.path = TestPath(os)
	self.files = {}
	self.tempno = 0

    def access(self, name, mode):
	if name in self.files:
	    return True
	return False

    def listdir(self, name):
	li = []
	name = self.path.join(name, '')
	for k in self.files:
	    if k.startswith(name):
		rest = k[len(name):]
		if rest:
		    li.append(rest)
	return li

    def mkdtemp(self):
	self.tempno += 1
	return '/tmp/xyz%d'%self.tempno

    def read_file(self, name):
	return self.files[name]

    def remove(self, name):
	try:
	    del self.files[name]
	except KeyError:
	    raise IOError, 'No such file: %r'%name

    def rename(self, src, tgt):
	try:
	    data = self.files[src]
	except KeyError:
	    raise IOError, 'No such file: %r'%src
	del self.files[src]
	self.files[tgt] = data

    def rmdir(self, name):
	pass

    def write_file(self, name, text):
	self.files[name] = text

class RealIO:
    def __init__(self, mod):
	os = mod._root.os
	for name in mod.os_common:
	    setattr(self, name, getattr(os, name))
	self.path = os.path
	self.listdir = os.listdir
	self.makedirs = os.makedirs
	self.mkdtemp = mod._root.tempfile.mkdtemp
	self.rmdir = os.rmdir
	self.access = os.access
        self.chdir = os.chdir
	self.remove = os.remove
	self.rename = os.rename
	
    def read_file(self, name):
	f = open(name)
	data = f.read()
	f.close()
	return data

    def write_file(self, name, data):
	f = open(name, 'w')
	f.write(data)
	f.close()

class _GLUECLAMP_:

    _setable_ = 'IO',

    os_common = ('R_OK', 'W_OK', 'X_OK')

    def _get_IO(self):
	return RealIO(self)
	
    def set_IO(self, IO):
	self.IO = IO

    def set_test_mode(self):
	self.set_IO(TestIO(self))
