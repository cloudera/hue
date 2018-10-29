
referents = []     # list "object descriptor -> python object"
freelist = None

def store(x):
    "Store the object 'x' and returns a new object descriptor for it."
    global freelist
    p = freelist
    if p is None:
        p = len(referents)
        referents.append(x)
    else:
        freelist = referents[p]
        referents[p] = x
    return p

def discard(p):
    """Discard (i.e. close) the object descriptor 'p'.
    Return the original object that was attached to 'p'."""
    global freelist
    x = referents[p]
    referents[p] = freelist
    freelist = p
    return x

class Ref(object):
    """For use in 'with Ref(x) as ob': open an object descriptor
    and returns it in 'ob', and close it automatically when the
    'with' statement finishes."""
    def __init__(self, x):
        self.x = x
    def __enter__(self):
        self.p = p = store(self.x)
        return p
    def __exit__(self, *args):
        discard(self.p)

def count_pyobj_alive():
    result = len(referents)
    p = freelist
    while p is not None:
        assert result > 0
        result -= 1
        p = referents[p]
    return result

# ------------------------------------------------------------

if __name__ == '__main__':
    import api

    ffi = api.PythonFFI()

    ffi.cdef("""
        typedef int pyobj_t;
        int sum_integers(pyobj_t p_list);
        pyobj_t sum_objects(pyobj_t p_list, pyobj_t p_initial);
    """)

    @ffi.pyexport("int(pyobj_t)")
    def length(p_list):
        list = referents[p_list]
        return len(list)

    @ffi.pyexport("int(pyobj_t, int)")
    def getitem(p_list, index):
        list = referents[p_list]
        return list[index]

    @ffi.pyexport("pyobj_t(pyobj_t)")
    def pyobj_dup(p):
        return store(referents[p])

    @ffi.pyexport("void(pyobj_t)")
    def pyobj_close(p):
        discard(p)

    @ffi.pyexport("pyobj_t(pyobj_t, int)")
    def pyobj_getitem(p_list, index):
        list = referents[p_list]
        return store(list[index])

    @ffi.pyexport("pyobj_t(pyobj_t, pyobj_t)")
    def pyobj_add(p1, p2):
        return store(referents[p1] + referents[p2])

    lib = ffi.verify("""
        typedef int pyobj_t;    /* an "object descriptor" number */

        int sum_integers(pyobj_t p_list) {
            /* this a demo function written in C, using the API
               defined above: length() and getitem(). */
            int i, result = 0;
            int count = length(p_list);
            for (i=0; i<count; i++) {
                int n = getitem(p_list, i);
                result += n;
            }
            return result;
        }

        pyobj_t sum_objects(pyobj_t p_list, pyobj_t p_initial) {
            /* same as above, but keeps all additions as Python objects */
            int i;
            int count = length(p_list);
            pyobj_t p1 = pyobj_dup(p_initial);
            for (i=0; i<count; i++) {
                pyobj_t p2 = pyobj_getitem(p_list, i);
                pyobj_t p3 = pyobj_add(p1, p2);
                pyobj_close(p2);
                pyobj_close(p1);
                p1 = p3;
            }
            return p1;
        }
    """)

    with Ref([10, 20, 30, 40]) as p_list:
        print lib.sum_integers(p_list)
        with Ref(5) as p_initial:
            result = discard(lib.sum_objects(p_list, p_initial))
            print result

    assert count_pyobj_alive() == 0
