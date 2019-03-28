#------------------------------------------------------------------------------
# Copyright (c) 2018, 2019, Oracle and/or its affiliates. All rights reserved.
#------------------------------------------------------------------------------

"""Module for testing Simple Oracle Document Access (SODA) Database"""

import TestEnv

import cx_Oracle
import json

class TestCase(TestEnv.BaseTestCase):

    def __dropExistingCollections(self, sodaDatabase):
        for name in sodaDatabase.getCollectionNames():
            sodaDatabase.openCollection(name).drop()

    def __verifyDocument(self, doc, rawContent, strContent=None, content=None,
            key=None, mediaType='application/json'):
        self.assertEqual(doc.getContentAsBytes(), rawContent)
        if strContent is not None:
            self.assertEqual(doc.getContentAsString(), strContent)
        if content is not None:
            self.assertEqual(doc.getContent(), content)
        self.assertEqual(doc.key, key)
        self.assertEqual(doc.mediaType, mediaType)

    def testCreateDocumentWithJson(self):
        "test creating documents with JSON data"
        sodaDatabase = self.connection.getSodaDatabase()
        val = {"testKey1" : "testValue1", "testKey2" : "testValue2" }
        strVal = json.dumps(val)
        bytesVal = strVal.encode("UTF-8")
        key = "MyKey"
        mediaType = "text/plain"
        doc = sodaDatabase.createDocument(val)
        self.__verifyDocument(doc, bytesVal, strVal, val)
        doc = sodaDatabase.createDocument(strVal, key)
        self.__verifyDocument(doc, bytesVal, strVal, val, key)
        doc = sodaDatabase.createDocument(bytesVal, key, mediaType)
        self.__verifyDocument(doc, bytesVal, strVal, val, key, mediaType)

    def testCreateDocumentWithRaw(self):
        "test creating documents with raw data"
        sodaDatabase = self.connection.getSodaDatabase()
        val = b"<html/>"
        key = "MyRawKey"
        mediaType = "text/html"
        doc = sodaDatabase.createDocument(val)
        self.__verifyDocument(doc, val)
        doc = sodaDatabase.createDocument(val, key)
        self.__verifyDocument(doc, val, key=key)
        doc = sodaDatabase.createDocument(val, key, mediaType)
        self.__verifyDocument(doc, val, key=key, mediaType=mediaType)

    def testGetCollectionNames(self):
        "test getting collection names from the database"
        sodaDatabase = self.connection.getSodaDatabase()
        self.__dropExistingCollections(sodaDatabase)
        self.assertEqual(sodaDatabase.getCollectionNames(), [])
        names = ["zCol", "dCol", "sCol", "aCol", "gCol"]
        sortedNames = list(sorted(names))
        for name in names:
            sodaDatabase.createCollection(name)
        self.assertEqual(sodaDatabase.getCollectionNames(), sortedNames)
        self.assertEqual(sodaDatabase.getCollectionNames(limit=2),
                sortedNames[:2])
        self.assertEqual(sodaDatabase.getCollectionNames("a"), sortedNames)
        self.assertEqual(sodaDatabase.getCollectionNames("C"), sortedNames)
        self.assertEqual(sodaDatabase.getCollectionNames("b", limit=3),
                sortedNames[1:4])
        self.assertEqual(sodaDatabase.getCollectionNames("z"),
                sortedNames[-1:])

    def testOpenCollection(self):
        "test opening a collection"
        sodaDatabase = self.connection.getSodaDatabase()
        self.__dropExistingCollections(sodaDatabase)
        coll = sodaDatabase.openCollection("CollectionThatDoesNotExist")
        self.assertEqual(coll, None)
        createdColl = sodaDatabase.createCollection("cxoTestOpenCollection")
        coll = sodaDatabase.openCollection(createdColl.name)
        self.assertEqual(coll.name, createdColl.name)
        coll.drop()

    def testRepr(self):
        "test SodaDatabase representation"
        con1 = self.connection
        con2 = TestEnv.GetConnection()
        sodaDatabase1 = con1.getSodaDatabase()
        sodaDatabase2 = con1.getSodaDatabase()
        sodaDatabase3 = con2.getSodaDatabase()
        self.assertEqual(str(sodaDatabase1), str(sodaDatabase2))
        self.assertEqual(str(sodaDatabase2), str(sodaDatabase3))

    def testNegative(self):
        "test negative cases for SODA database methods"
        sodaDatabase = self.connection.getSodaDatabase()
        self.assertRaises(TypeError, sodaDatabase.createCollection)
        self.assertRaises(TypeError, sodaDatabase.createCollection, 1)
        self.assertRaises(cx_Oracle.DatabaseError,
                sodaDatabase.createCollection, None)
        self.assertRaises(TypeError, sodaDatabase.getCollectionNames, 1)

if __name__ == "__main__":
    TestEnv.RunTestCases()

