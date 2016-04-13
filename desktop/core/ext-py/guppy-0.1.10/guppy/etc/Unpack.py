#._cv_part guppy.etc.Unpack

from opcode import *
import sys

CALL_FUNCTION = opmap['CALL_FUNCTION']
UNPACK_SEQUENCE = opmap['UNPACK_SEQUENCE']
STORE_FAST = opmap['STORE_FAST']
STORE_NAME = opmap['STORE_NAME']
STORE_GLOBAL = opmap['STORE_GLOBAL']
STORE_ATTR = opmap['STORE_ATTR']
STORE_SUBSCR = opmap['STORE_SUBSCR']
STORE_SLICE = opmap['STORE_SLICE+0']

def unpack(x):
    try:
	1/0
    except:
	typ, value, traceback = sys.exc_info()

	f = traceback.tb_frame.f_back
	co = f.f_code
	i = f.f_lasti
	code = co.co_code
	if ord(code[i]) == CALL_FUNCTION and ord(code[i+3]) == UNPACK_SEQUENCE:
	    i += 3
	    n = ord(code[i+1]) + ord(code[i+2])*256
	    i += 3
	    names = []
	    while len(names) < n and i < len(code):
		op = ord(code[i])
		i += 1
		if op >= HAVE_ARGUMENT:
		    oparg = ord(code[i]) + ord(code[i+1])*256
		    i += 2
		    if op == STORE_FAST:
			names.append(co.co_varnames[oparg])
		    elif op in (STORE_NAME, STORE_ATTR, STORE_GLOBAL):
			names.append(co.co_names[oparg])
		if op == STORE_SUBSCR or STORE_SLICE <= op <= STORE_SLICE+3:
		    break
	    if len(names) == n:
		r = []
		for name in names:
		    try:
			v = getattr(x, name)
		    except AttributeError:
			v = x[name]
		    r.append(v)
		return r
	raise SyntaxError
	    

def test_unpack():
    class C:
	a=1
	b=3
	c=4
    y = C()
    a, b, c = unpack(y)
    x =  [a,b,c]
    class D:
	pass
    D.a, c, D.b = unpack(y)
    x.extend([D.a, c, D.b])

    l=[None]
    try:
	l[0], c, b = unpack(y)
    except SyntaxError: 
	pass
    else:
	raise RuntimeError
    l=[None]
    try:
	l[1:2], c, b = unpack(y)
    except SyntaxError: 
	pass
    else:
	raise RuntimeError
    y=[]

    y = {'a':'A', 'b':'B'}
    a, b = unpack(y)
    x.extend([a, b])

    global g
    y['g']='G'
    g, b = unpack(y)
    x.extend([g, b])

    if x != [1, 3, 4, 1, 4, 3, 'A', 'B', 'G', 'B']:
	raise RuntimeError
    
__all__ = 'unpack'

if __name__ == '__main__':
    test_unpack()
