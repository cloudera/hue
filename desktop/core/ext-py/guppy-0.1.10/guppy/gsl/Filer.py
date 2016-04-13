#._cv_part guppy.gsl.Filer
""" Handles filing of data from low-level gsl filing and data records.
"""

class Filer:
    def __init__(self, mod, node):
	self.mod = mod
	self.writefile_envs = []
	self.writefile_names = {}

	node.accept(self)

    def visit_file(self, node):
	node.children_accept(self)

    visit_string = visit_file 

    def visit_write_file(self, node):
	name = node.arg
	if name in self.writefile_names:
	    raise SyntaxError, 'Duplicate file name: %r'%name
	self.writefile_names[name] = node
	self.writefile_envs.append(WriteFile(self, node))
	
    def get_info(self):
	infos = []
	for e in self.writefile_envs:
	    infos.append('write file: %s'%e.file_name)
	return '\n'.join(infos)

    def write(self):
	for e in self.writefile_envs:
	    e.write()

class WriteFile:
    node_data = None
    node_mode = None
    def __init__(self, filer, node):
	self.filer = filer
	self.mod = mod = filer.mod
	self.node_file = node
	self.file_name = node.arg
	
	node.children_accept(self)
	if self.node_data is None:
	    data = ''
	else:
	    data = self.node_data.arg
	self.data = data
	if self.node_mode is None:
	    mode = ''
	else:
	    mode = self.node_mode.arg
	self.mode = mode
	
    def visit_text(self, node):
	self.set_single('node_data', node)

    def visit_end(self, node):
	self.set_single('node_end', node)

    def visit_mode(self, node):
	self.set_single('node_mode', node)

    def set_single(self, name, node):
	if getattr(self, name, None) is not None:
	    raise SyntaxError, 'Duplicate %r at index %r'%(name, node.index)
	setattr(self, name, node)
	node.children_accept(self, 'no_node_expected')

    def write(self):
	IO = self.mod.IO
	if self.mod.backup_suffix:
	    backup_name = self.file_name + self.mod.backup_suffix
	    if IO.access(self.file_name, IO.R_OK | IO.W_OK):
		IO.rename(self.file_name, backup_name)
		
	IO.write_file(self.file_name, self.data)


class _GLUECLAMP_:
    _imports_ = (
	'_parent.FileIO:IO',
	)

    _setable_ = 'backup_suffix',

    # Files that are to be overwritten are renamed by
    # adding backup_suffix to the name. This is no substitute for a
    # versioning system but a last precaution, especially while I am
    # developing the system.
    # Set this to None to disable backuping.

    backup_suffix = ',gsl-backuped'

    syntax_gsl = '''
.tag writefile

'''

    def filer(self, node):
	return Filer(self, node)

    def _test_main_(self):
	IO = self.IO
	N = self._parent.SpecNodes
	tempdir = IO.mkdtemp()
	tempname = IO.path.join(tempdir, 'x')
	data = 'hello'
	try:
	    X = '''
.write file: %s
..text
%s
..end
'''%(tempname, data)
	    node = N.node_of_string(X)
	    f = self.filer(node)
	    assert f.get_info() == 'write file: %s'%tempname
	    f.write()
	    d = IO.read_file(tempname)
	    assert d == data

	    # Test multiple files and backup
	    # And that we can do without ..data / ..end

	    data2 = 'hello2\n'
	    data3 = '\nhello3'
	    X = '''
.write file: %s
%s
.write file: %s
..text
%s
..end
'''%(tempname, data2, tempname+'.3', data3)

	    node = N.node_of_string(X)
	    f = self.filer(node)
	    f.write()

	    assert IO.read_file(tempname+self.backup_suffix) == data
	    d = IO.read_file(tempname)
	    assert d == data2
	    assert IO.read_file(tempname+'.3') == data3

	finally:
	    for name in IO.listdir(tempdir):
		IO.remove(IO.path.join(tempdir, name))
	    IO.rmdir(tempdir)


if 0 or __name__=='__main__': # doesnt work
    from guppy import Root
    gsl = Root().guppy.gsl
    gsl.FileIO.set_test_mode()
    gsl.Filer._test_main_()

