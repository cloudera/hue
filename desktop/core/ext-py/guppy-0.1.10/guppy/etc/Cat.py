#._cv_part guppy.etc.Cat

class Graph:
    def __init__(self, objects, arrows):
	self.objects = objects	# Sequence of objects
	self.arrows = arrows	# Map[name] ->pair(object, object)

    def source(self, x):
	return self.arrows[x][0]

    def target(self, x):
	return self.arrows[x][1]


    def get_dual(self):
	objects = self.objects
	arrows = dict([(arrow, (tgt, src)) for (arrow, (src, tgt)) in self.arrows.items()])
	return self.__class__(objects, arrows)

class Cat:
    # Category presented by a graph (with objects and generators) and relations.
    def __init__(self, graph, relations):
	# category is defined by the parameters:
	#    graph.objects: sequenceof(O)
	#    graph.arrows: dict mapping(A, pairof(O in objects))
	#    relations: sequence(pairof(sequence(A), sequence(A)))
	self.graph = graph
	self.relations = relations

    def get_dual(self):
	graph = self.graph.get_dual()
	relations = dual_relations(self.relations)
	return self.__class__(graph, relations)


class Functor:
    def __init__(self, fo, fa, src = None, tgt = None):
	self.fo = adapt_function(fo)
	self.fa = adapt_function(fa)
	self.src = src
	self.tgt = tgt
    
class Function:
    def __init__(self, map, src, tgt):
	f = getattr(map, '__getitem__', None)
	if callable(f):
	    pass
	else:
	    f = map
	    if not callable(f):
		raise TypeError, 'Function: map is neither callable or indexable'
	self.__getitem__ = self.__call__ = f
	self.src = src
	self.tgt = tgt
    
    def __str__(self):
	return '%s(%s, %s, %s)'%(self.__class__, self.src, self.tgt, self.__call__)

    def asdict(self):
	return dict([(x, self[x]) for x in self.src])

    def items(self):
	return [(x, self[x]) for x in self.src]

    def keys(self):
	return list(self.src)

    def values(self):
	return [v for (k, v) in self.items()]


class Identity(Function):
    def __init__(self, src):
	Function.__init__(lambda x:x, src, src)

def check_graph(G):
    # Check that G is a valid graph object
    # with arrows that have all source and target in G.objects

    Gob = G.objects
    for a in G.arrows:
	if not G.source(a) in Gob:
	    raise ValueError, 'Arrow %r has source %r not in graph objects'%(a, G.source(a))
	if not G.target(a) in Gob:
	    raise ValueError, 'Arrow %r has target %r not in graph objects'%(a, G.target(a))

def check_rules(R, G):
    # Check that the rules in R contain valid composing arrows in graph G

    coms = []
    for (left, right) in R:
	coms.append(left)
	coms.append(right)

    for com in coms:
	a0 = None
	for a in com:
	    if a not in G.arrows:
		raise ValueError, 'Arrow %r, used in a rule, is not a valid arrow'%(a,)
	    if a0 is not None:
		if G.source(a) != G.target(a0):
		    raise ValueError, '''\
Source of arrow %r (%r) does not match target of arrow %r (%r)'''%(
		a, G.source(a), a0, G.target(a0))
	    a0 = a


def check_cat(C):
    check_graph(C.graph)
    check_rules(C.relations, C.graph)
    

def oarcat(objects, arrows, relations):
    return Cat(Graph(objects, arrows), relations)

def adapt_function(f):
    if not isinstance(f, Function):
	if isinstance(f, dict):
	    src = f.keys()
	    tgt = f.values()
	else:
	    src = None
	    tgt = None
	f = Function(f, src, tgt)
    return f
	
def dual_relations(relations):
    dual = []
    for (a, b) in relations:
	a = list(a)
	b = list(b)
	a.reverse()
	b.reverse()
	dual.append((tuple(a), tuple(b)))
    return dual

