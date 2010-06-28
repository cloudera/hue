cdef extern class lxml.etree._Document:
 cdef int _ns_counter
 cdef object _prefix_tail
 cdef xmlDoc (*_c_doc)
 cdef _BaseParser _parser
cdef extern class lxml.etree._Element:
 cdef PyObject (*_gc_doc)
 cdef _Document _doc
 cdef xmlNode (*_c_node)
 cdef object _tag
 cdef object _attrib
cdef extern class lxml.etree._ElementTree:
 cdef _Document _doc
 cdef _Element _context_node
cdef extern class lxml.etree._ElementTagMatcher:
 cdef object _pystrings
 cdef int _node_type
 cdef char (*_href)
 cdef char (*_name)
cdef extern class lxml.etree._ElementIterator:
 cdef _Element _node
 cdef xmlNode (*((*_next_element)(xmlNode (*))))
cdef extern class lxml.etree.ElementBase:
 pass
cdef extern class lxml.etree.ElementClassLookup:
 cdef object ((*_lookup_function)(object ,_Document ,xmlNode (*)))
cdef extern class lxml.etree.FallbackElementClassLookup:
 cdef ElementClassLookup fallback
 cdef object ((*_fallback_function)(object ,_Document ,xmlNode (*)))
cdef extern void (appendChild(_Element ,_Element ))
cdef extern object (attributeValue(xmlNode (*),xmlAttr (*)))
cdef extern object (attributeValueFromNsName(xmlNode (*),char (*),char (*)))
cdef extern object (callLookupFallback(FallbackElementClassLookup ,_Document ,xmlNode (*)))
cdef extern object (collectAttributes(xmlNode (*),int ))
cdef extern _Element (deepcopyNodeToDocument(_Document ,xmlNode (*)))
cdef extern int (delAttribute(_Element ,object ) except -1)
cdef extern int (delAttributeFromNsName(xmlNode (*),char (*),char (*)))
cdef extern _Document (documentOrRaise(object ))
cdef extern _Element (elementFactory(_Document ,xmlNode (*)))
cdef extern _ElementTree (elementTreeFactory(_Element ))
cdef extern xmlNode (*(findChild(xmlNode (*),Py_ssize_t )))
cdef extern xmlNode (*(findChildBackwards(xmlNode (*),Py_ssize_t )))
cdef extern xmlNode (*(findChildForwards(xmlNode (*),Py_ssize_t )))
cdef extern xmlNs (*(findOrBuildNodeNsPrefix(_Document ,xmlNode (*),char (*),char (*)) except NULL))
cdef extern object (getAttributeValue(_Element ,object ,object ))
cdef extern object (getNsTag(object ))
cdef extern int (hasChild(xmlNode (*)))
cdef extern int (hasTail(xmlNode (*)))
cdef extern int (hasText(xmlNode (*)))
cdef extern void (initTagMatch(_ElementTagMatcher ,object ))
cdef extern void (iteratorStoreNext(_ElementIterator ,_Element ))
cdef extern object (iterattributes(_Element ,int ))
cdef extern object (lookupDefaultElementClass(object ,object ,xmlNode (*)))
cdef extern object (lookupNamespaceElementClass(object ,object ,xmlNode (*)))
cdef extern _Element (makeElement(object ,_Document ,object ,object ,object ,object ,object ))
cdef extern _Element (makeSubElement(_Element ,object ,object ,object ,object ,object ))
cdef extern object (namespacedName(xmlNode (*)))
cdef extern object (namespacedNameFromNsName(char (*),char (*)))
cdef extern _ElementTree (newElementTree(_Element ,object ))
cdef extern xmlNode (*(nextElement(xmlNode (*))))
cdef extern xmlNode (*(previousElement(xmlNode (*))))
cdef extern object (pyunicode(char (*)))
cdef extern _Element (rootNodeOrRaise(object ))
cdef extern int (setAttributeValue(_Element ,object ,object ) except -1)
cdef extern void (setElementClassLookupFunction(object ((*)(object ,_Document ,xmlNode (*))),object ))
cdef extern int (setNodeText(xmlNode (*),object ) except -1)
cdef extern int (setTailText(xmlNode (*),object ) except -1)
cdef extern int (tagMatches(xmlNode (*),char (*),char (*)))
cdef extern object (tailOf(xmlNode (*)))
cdef extern object (textOf(xmlNode (*)))
cdef extern object (utf8(object ))
