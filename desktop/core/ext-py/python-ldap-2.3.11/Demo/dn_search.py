#!/usr/bin/python2.1

version = '$Revision: 0.0 $'[11:-2]

"""
$Id$
$Revision$

Some unit tests for python-ldap.
"""

True=1 ; False=0 ; # builtin in 2.3!

#import getopt
#import os
#import re
import sys
#import time
import unittest

import ldap

class LDAPTestCase( unittest.TestCase ) :
    """Base class for python-ldap unit tests."""

    def __init__( self , server , base ) :
        unittest.TestCase.__init__( self )
        self.server = server
        self.search_base = base

    def setUp( self ) :
        self.conn = ldap.initialize( 'ldap://'+self.server )

    def tearDown( self ) :
        del self.conn
# end class LDAPTestCase


class TestCase1( LDAPTestCase ) :
    """ Test search_s for returning the 'dn' attribute.  """

    #def __init__( self ) :
    #    LDAPTestCase.__init__( methodName="" )

    def runTest( self ) :
        res = self.conn.search_s(   self.search_base ,
                                    ldap.SCOPE_BASE ,
                                    '(objectClass=*)' ,
                                    ['dn']
                                )
        assert len(res) == 1 , "Wrong number of results : %s" % repr(res)
        assert res[0][1].has_key( 'dn' ) , \
                                    "Attribute 'dn' missing.  %s" % repr(res)
    # end runTest()
# end class TestCase1


class TestCase2( LDAPTestCase ) :
    """ Test search_st for returning the 'dn' attribute.  """

    def runTest( self ) :
        res = self.conn.search_st(   self.search_base ,
                                    ldap.SCOPE_BASE ,
                                    '(objectClass=*)' ,
                                    ['dn'] ,
                                    4
                                )
        assert len(res) == 1, "Wrong number of results : %s" % repr(res)
        assert res[0][1].has_key( 'dn' ) , \
                                "Attribute 'dn' missing.  %s" % repr(res)
    # end runTest()
# end class TestCase2



class TestCase3( LDAPTestCase ) :
    """ Test search/result for returning the 'dn' attribute.  """

    def runTest( self ) :
        msgid = self.conn.search(   self.search_base ,
                                    ldap.SCOPE_BASE ,
                                    '(objectClass=*)' ,
                                    ['dn']
                                )
        res = self.conn.result( msgid , 4 )
        assert len(res) != 0, "No results from search." % repr(res)
        #assert res[0] == ldap.RES_SEARCH_RESULT, "unexpected result code %s"
        data = res[1]
        assert len(data) == 1, "Wrong number of results : %s" % repr(res)
        for attr in ( 'dn' , ) :
            assert data[0][1].has_key( attr ) , \
                    "Expected attribute '%s' missing.  %s" % (attr, repr(res))
    # end runTest()
# end class TestCase3


class TestCase4( LDAPTestCase ) :
    """ Test search/result for returning some attributes.  """

    def runTest( self ) :
        msgid = self.conn.search(   self.search_base ,
                                    ldap.SCOPE_BASE ,
                                    '(objectClass=*)' #,
                                    #['dn']
                                )
        res = self.conn.result( msgid , 4 )
        assert len(res) != 0, "No results from search." % repr(res)
        #assert res[0] == ldap.RES_SEARCH_RESULT, "unexpected result code %s"
        data = res[1]
        assert len(data) == 1, "Wrong number of results : %s" % repr(res)
        for attr in ( 'o' , ) :
            assert data[0][1].has_key( attr ) , \
                    "Expected attribute '%s' missing.  %s" % (attr, repr(res))
    # end runTest()
# end class TestCase3




def suite() :
    """Build the suite of test cases"""

    # suite1 = unittest.makeSuite( TestCase1 , "test_" )
    # return unittest.TestSuite( (suite1, ) )

    suite = unittest.TestSuite()
    server = "barak"
    base = "o=International Teams"
    for tclass in ( TestCase1, TestCase2, TestCase3, TestCase4 ) :
        suite.addTest( tclass( server=server , base=base ) )
    return suite
# end suite()



if __name__ == "__main__" :
    #unittest.main()
    unittest.TextTestRunner().run( suite() )


## ----------------------------------------------------------------------------
# History :
#   $Log$

