#._cv_part guppy.etc.Code

def co_code_findloadednames(co):
    """Find in the code of a code object, all loaded names.
    (by LOAD_NAME, LOAD_GLOBAL or LOAD_FAST) """

    from opcode import HAVE_ARGUMENT, opmap
    hasloadname = (opmap['LOAD_NAME'],opmap['LOAD_GLOBAL'],opmap['LOAD_FAST'])
    code = co.co_code
    nargs = co.co_argcount
    len_co_names = len(co.co_names)
    indexset = {}
    n = len(code)
    i = 0
    while i < n:
        c = code[i]
        op = ord(c)
        i = i+1
        if op >= HAVE_ARGUMENT:
	    if op in hasloadname:
		oparg = ord(code[i]) + ord(code[i+1])*256
		name = co.co_names[oparg]
		indexset[name] = 1
		if len(indexset) >= len_co_names:
		    break
            i = i+2
    for name in co.co_varnames:
	try:
	    del indexset[name]
	except KeyError:
	    pass
    return indexset

def co_findloadednames(co):
    """Find all loaded names in a code object and all its consts of code type"""
    names = {}
    names.update(co_code_findloadednames(co))
    for c in co.co_consts:
	if isinstance(c, type(co)):
	    names.update(co_findloadednames(c))
    return names
    

