#._cv_part guppy.etc.ExecfileWithModuleInfo

import sys, os, imp, md5

_VERBOSE   = True
_RELOAD_ALWAYS = True # False
_MAGIC = '#._cv_part'

modsums = {}

def pyname(m):
    fname = m.__file__
    if not fname.endswith('.py'):
	se = os.path.splitext(fname)
	fname = se[0]+'.py'
    return fname

def calc_stringsum(s):
    return md5.md5(s).digest()
    
def calc_modsum(m):
    return calc_stringsum(open(pyname(m)).read())

def execfile(filename, globs=None, locs=None):
    if globs==None:
	# Do this in an interior frame to not change caller's sys.exc_info()
	def get_globs():
	    try:
		1/0
	    except:
		try:
		    typ, val, trb = sys.exc_info()
		    frame = trb.tb_frame.f_back.f_back
		    globs = frame.f_globals
		finally:
		    del typ,val,trb
	    return globs
	globs = get_globs()

    file = open(filename)

    text = file.read()
    file.close()

    if text.startswith(_MAGIC):
	ix = len(_MAGIC)
    else:
	ix = text.find('\n'+_MAGIC)
	if ix == -1:
	    code = compile(text, filename, 'exec')
	    exec code in globs, locs
	    return
	ix = ix + len(_MAGIC) + 1

    eix = text.find('\n', ix)
    name = text[ix:eix]
    name=name.strip()
    m = sys.modules.get(name)
    if m is None:
	if _VERBOSE:
	    print '%s.execfile: importing'%__name__, name
	__import__(name, globs, locs, [])
	m = sys.modules[name]

	msum = calc_modsum(m)
	modsums[m.__name__] = msum
	tsum = calc_stringsum(text)
    else:
	msum = modsums.get(m.__name__)
	if msum != calc_modsum(m):
	    msum = ''
	tsum = calc_stringsum(text)
	
    if _RELOAD_ALWAYS or msum != tsum:
	if _VERBOSE:
	    print '%s.execfile: reloading'%__name__, name
	fname = pyname(m)
	code = compile(text, fname, 'exec')
	exec code in m.__dict__
	modsums[m.__name__] = tsum
	    



