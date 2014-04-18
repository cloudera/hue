#._cv_part guppy.etc.IterPermute

def iterpermute(*args):
    args = [iter(a) for a in args]
    la = len(args)
    stopped = [0] * la
    lens = [0] * la
    bufs = [[] for i in range(la)]
    nexts = [None] * la
    n = 0
    while 1:
	anynew = 0
	for i in range(la):
	    if stopped[i]:
		next = bufs[i][n%lens[i]]
	    else:
		try:
		    next = args[i].next()
		except StopIteration:
		    if lens[i] == 0:
			# raise ValueError, 'The iterator passed in arg %d did not return any item'%i
			return
		    stopped[i] = 1
		    next = bufs[i][n%lens[i]]
		else:
		    anynew = 1
		    bufs[i].append(next)
		    lens[i] += 1
	    nexts[i] = next
	if anynew:
	    n += 1
	    yield tuple(nexts)
	else:
	    break
    
    wanted = reduce(lambda x, y: x*y, lens, 1)
    if n >= wanted:
	assert n == wanted
	return
    ixs = list(enumerate(lens))
    ixs.sort(lambda (ixa, lna), (ixb, lnb) : cmp(lna, lnb))
    ixs = [ix for (ix,ln) in ixs]
    jxs = [0] * la
    seen = dict([(tuple([j%lens[i] for i in ixs]), 1)
		 for j in range(n)])

    while n < wanted:
	t = tuple([jxs[i] for i in ixs]) 
	if t not in seen:
	    yield tuple([bufs[i][jxs[i]] for i in range(la)])
	    n += 1

	for i in ixs:
	    j = jxs[i]
	    j = (j + 1)%lens[i]
	    jxs[i] = j
	    if j != 0:
		break



def test_iterpermute():
    import itertools
    repeat = itertools.repeat
    assert list(iterpermute()) == [()]
    assert list(iterpermute(repeat(1, 2))) == [(1,), (1,)]
    assert list(iterpermute(repeat(1, 1), repeat(2, 1))) == [(1,2)]
    assert list(iterpermute(range(0,2), range(2,3))) == [(0, 2), (1, 2)]
    assert list(iterpermute(range(0,2), range(2,4))) == [(0, 2), (1, 3), (1, 2), (0, 3)]
    print list(iterpermute(range(0,2), range(0,3)))
    print list(iterpermute(range(0,3), range(0,2)))


if __name__ == '__main__':
    test_iterpermute()
