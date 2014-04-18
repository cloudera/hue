#._cv_part guppy.etc.etc

from StringIO import StringIO

def reptable(tb):
    if not tb:
	return 0, []
    maxlens = [0]*len(tb[0])
    for r in tb:
	if r == '-':
	    continue
	for i, e in enumerate(r):
	    maxlens[i] = max(maxlens[i], len(str(e))+1)
	
    sumlens = len(maxlens)
    for s in maxlens:
	sumlens += s

    out = []
    for r in tb:
	if r == '-':
	    out.append( '-'*min(sumlens, 75) )
	else:
	    so = ''
	    for i, e in enumerate(r):
		s = str(e)
		if s.startswith('!>'):
		    s = s[2:]
		    fillright = 1
		elif s.isdigit():
		    fillright = 1
		else:
		    fillright = 0
		ml = maxlens[i]-1
		fill = ' '*(ml -len(s))
		if fillright:
		    s = fill + s
		else:
		    if 1 or i + 1 < len(r):
			s = s + fill
		so += s + ' '
	    out.append(so)
    return maxlens, out


def ptable(tb, f=None):
    if f is None:
	import sys
	f = sys.stdout
    _, lines = reptable(tb)
    for line in lines:
	line = line.rstrip()
	print >>f, line
    

def strtable(tb):
    f = StringIO()
    ptable(tb, f)
    return f.getvalue()

def str2int(s, msg = 'Hexadecimal literal in the form [-]0x... expected'):
    # xxx clumsy -- there should be a builtin function for this !
    if s.startswith('-'):
        sign = -1
        s = s [1:]
    else:
        sign = 1
    if not s.startswith('0x'):
        raise ValueError, msg
    s = s[2:]
    if s.endswith('l') or s.endswith('L'):
        s = s[:-1]
    return int(s, 16) * sign
