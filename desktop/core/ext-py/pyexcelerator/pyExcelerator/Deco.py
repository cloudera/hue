# This code from 

# PEP: 318 
# Title: Decorators for Functions and Methods 
# Version: 1.35 
# Last-Modified: 2004/09/14 07:34:23 
# Author: Kevin D. Smith, Jim Jewett, Skip Montanaro, Anthony Baxter 

# This code fixes error in example 4: 
# authors' code contains
#       @accepts(int, (int,float))
#       @returns((int,float))
#       def func(arg1, arg2):
#           return arg1 * arg2
# 
# It should be:
#       @returns((int,float))
#       @accepts(int, (int,float))
#       def func(arg1, arg2):
#           return arg1 * arg2
# because of decorators are applied from bottom to up.


__rev_id__ = """$Id: Deco.py,v 1.4 2005/07/20 07:24:11 rvk Exp $"""


def accepts(*types):
    #print types
    def check_accepts(f):
        assert len(types) == f.func_code.co_argcount
        def new_f(*args, **kwds):
            for (a, t) in zip(args, types):
                assert isinstance(a, t), \
                       "arg %r does not match %s" % (a,t)
            return f(*args, **kwds)
        new_f.func_name = f.func_name
        return new_f
    return check_accepts

def returns(rtype):
    def check_returns(f):
        def new_f(*args, **kwds):
            result = f(*args, **kwds)
            assert isinstance(result, rtype), \
                   "return value %r does not match %s" % (result,rtype)
            return result
        new_f.func_name = f.func_name
        return new_f
    return check_returns


if __name__ == '__main__':
    import types 

    @returns(types.NoneType)
    @accepts(int, (int,float))
    def func(arg1, arg2):
        #return str(arg1 * arg2)
        pass

    func(1, 2)      
