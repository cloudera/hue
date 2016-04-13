#._cv_part guppy.heapy.ImpSet

class _GLUECLAMP_:
    _imports_ = (
	'_parent.UniSet:IdentitySetMulti',
	'_parent.UniSet:IdentitySet',
	'_parent.View:_hiding_tag_',
	'_root.guppy:sets',
	'_root.guppy.sets:NodeSet',
	'_root.guppy.sets:ImmNodeSet',
	'_root.guppy.sets:MutNodeSet',
	'_root.guppy.sets:immbit',
	'_root.guppy.sets:immbitrange',
	'_root.guppy.sets:immbitset',
	'_root.guppy.sets:mutbitset',
	)

    def _get_emptynodeset(self):
	return self.immnodeset()

    def immnodeset(self, it=()):
	return self.sets.immnodeset(it, self._hiding_tag_)

    def immnodeset_union(self, sets):
	return self.sets.immnodeset_union(sets, self._hiding_tag_)

    def laxnodeset(self, v):
	if not (isinstance(v, self.NodeSet) and v._hiding_tag_ is self._hiding_tag_):
	    v = self.sets.immnodeset(v, self._hiding_tag_)
	return v

    def mutnodeset(self, *args, **kwds):
	s = self.sets.mutnodeset(*args, **kwds)
	s._hiding_tag_ = self._hiding_tag_
	return s


    
