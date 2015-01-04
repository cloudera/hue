from __future__ import print_function
import os
import sys
import unittest
import io
import re

from xml.sax.saxutils import XMLGenerator
from xml.sax import SAXParseException
from pyexpat import ExpatError

from defusedxml import cElementTree, ElementTree, minidom, pulldom, sax, xmlrpc
from defusedxml import defuse_stdlib
from defusedxml import (DefusedXmlException, DTDForbidden, EntitiesForbidden,
                        ExternalReferenceForbidden, NotSupportedError)
from defusedxml.common import PY3, PY26, PY31


try:
    import gzip
except ImportError:
    gzip = None

try:
    from defusedxml import lxml
    from lxml.etree import XMLSyntaxError
    LXML3 = lxml.LXML3
except ImportError:
    lxml = None
    XMLSyntaxError = None
    LXML3 = False


HERE = os.path.dirname(os.path.abspath(__file__))

# prevent web access
# based on Debian's rules, Port 9 is discard
os.environ["http_proxy"] = "http://127.0.9.1:9"
os.environ["https_proxy"] = os.environ["http_proxy"]
os.environ["ftp_proxy"] = os.environ["http_proxy"]

if PY26 or PY31:
    class _AssertRaisesContext(object):
        def __init__(self, expected, test_case, expected_regexp=None):
            self.expected = expected
            self.failureException = test_case.failureException
            self.expected_regexp = expected_regexp

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, tb):
            if exc_type is None:
                try:
                    exc_name = self.expected.__name__
                except AttributeError:
                    exc_name = str(self.expected)
                raise self.failureException(
                    "{0} not raised".format(exc_name))
            if not issubclass(exc_type, self.expected):
                # let unexpected exceptions pass through
                return False
            self.exception = exc_value # store for later retrieval
            if self.expected_regexp is None:
                return True

            expected_regexp = self.expected_regexp
            if isinstance(expected_regexp, basestring):
                expected_regexp = re.compile(expected_regexp)
            if not expected_regexp.search(str(exc_value)):
                raise self.failureException('"%s" does not match "%s"' %
                         (expected_regexp.pattern, str(exc_value)))
            return True


class DefusedTestCase(unittest.TestCase):

    if PY3:
        content_binary = False
    else:
        content_binary = True

    xml_dtd = os.path.join(HERE, "xmltestdata", "dtd.xml")
    xml_external = os.path.join(HERE, "xmltestdata", "external.xml")
    xml_external_file = os.path.join(HERE, "xmltestdata", "external_file.xml")
    xml_quadratic = os.path.join(HERE, "xmltestdata", "quadratic.xml")
    xml_simple = os.path.join(HERE, "xmltestdata", "simple.xml")
    xml_simple_ns = os.path.join(HERE, "xmltestdata", "simple-ns.xml")
    xml_bomb = os.path.join(HERE, "xmltestdata", "xmlbomb.xml")
    xml_bomb2 = os.path.join(HERE, "xmltestdata", "xmlbomb2.xml")
    xml_cyclic = os.path.join(HERE, "xmltestdata", "cyclic.xml")

    if PY26 or PY31:
        # old Python versions don't have these useful test methods
        def assertRaises(self, excClass, callableObj=None, *args, **kwargs):
            context = _AssertRaisesContext(excClass, self)
            if callableObj is None:
                return context
            with context:
                callableObj(*args, **kwargs)

        def assertIn(self, member, container, msg=None):
            if member not in container:
                standardMsg = '%s not found in %s' % (repr(member),
                                                      repr(container))
                self.fail(self._formatMessage(msg, standardMsg))

    def get_content(self, xmlfile):
        mode = "rb" if self.content_binary else "r"
        with io.open(xmlfile, mode) as f:
            data = f.read()
        return data


class BaseTests(DefusedTestCase):
    module = None
    dtd_external_ref = False

    external_ref_exception = ExternalReferenceForbidden
    cyclic_error = None
    iterparse = None

    def test_simple_parse(self):
        self.parse(self.xml_simple)
        self.parseString(self.get_content(self.xml_simple))
        if self.iterparse:
            self.iterparse(self.xml_simple)

    def test_simple_parse_ns(self):
        self.parse(self.xml_simple_ns)
        self.parseString(self.get_content(self.xml_simple_ns))
        if self.iterparse:
            self.iterparse(self.xml_simple_ns)

    def test_entities_forbidden(self):
        self.assertRaises(EntitiesForbidden, self.parse, self.xml_bomb)
        self.assertRaises(EntitiesForbidden, self.parse, self.xml_quadratic)
        self.assertRaises(EntitiesForbidden, self.parse, self.xml_external)

        self.assertRaises(EntitiesForbidden, self.parseString,
                          self.get_content(self.xml_bomb))
        self.assertRaises(EntitiesForbidden, self.parseString,
                          self.get_content(self.xml_quadratic))
        self.assertRaises(EntitiesForbidden, self.parseString,
                          self.get_content(self.xml_external))

        if self.iterparse:
            self.assertRaises(EntitiesForbidden, self.iterparse,
                              self.xml_bomb)
            self.assertRaises(EntitiesForbidden, self.iterparse,
                              self.xml_quadratic)
            self.assertRaises(EntitiesForbidden, self.iterparse,
                              self.xml_external)

    def test_entity_cycle(self):
        self.assertRaises(self.cyclic_error, self.parse, self.xml_cyclic,
                          forbid_entities=False)

    def test_dtd_forbidden(self):
        self.assertRaises(DTDForbidden, self.parse, self.xml_bomb,
                          forbid_dtd=True)
        self.assertRaises(DTDForbidden, self.parse, self.xml_quadratic,
                          forbid_dtd=True)
        self.assertRaises(DTDForbidden, self.parse, self.xml_external,
                          forbid_dtd=True)
        self.assertRaises(DTDForbidden, self.parse, self.xml_dtd,
                          forbid_dtd=True)

        self.assertRaises(DTDForbidden, self.parseString,
                          self.get_content(self.xml_bomb),
                          forbid_dtd=True)
        self.assertRaises(DTDForbidden, self.parseString,
                          self.get_content(self.xml_quadratic),
                          forbid_dtd=True)
        self.assertRaises(DTDForbidden, self.parseString,
                          self.get_content(self.xml_external),
                          forbid_dtd=True)
        self.assertRaises(DTDForbidden, self.parseString,
                          self.get_content(self.xml_dtd),
                          forbid_dtd=True)

        if self.iterparse:
            self.assertRaises(DTDForbidden, self.iterparse,
                              self.xml_bomb, forbid_dtd=True)
            self.assertRaises(DTDForbidden, self.iterparse,
                              self.xml_quadratic, forbid_dtd=True)
            self.assertRaises(DTDForbidden, self.iterparse,
                              self.xml_external, forbid_dtd=True)
            self.assertRaises(DTDForbidden, self.iterparse,
                              self.xml_dtd, forbid_dtd=True)


    def test_dtd_with_external_ref(self):
        if self.dtd_external_ref:
            self.assertRaises(self.external_ref_exception, self.parse,
                              self.xml_dtd)
        else:
            self.parse(self.xml_dtd)

    def test_external_ref(self):
        self.assertRaises(self.external_ref_exception, self.parse,
                          self.xml_external, forbid_entities=False)

    def test_external_file_ref(self):
        content = self.get_content(self.xml_external_file)
        if isinstance(content, bytes):
            here = HERE.encode(sys.getfilesystemencoding())
            content = content.replace(b"/PATH/TO", here)
        else:
            content = content.replace("/PATH/TO", HERE)
        self.assertRaises(self.external_ref_exception, self.parseString,
                          content, forbid_entities=False)

    def test_allow_expansion(self):
        self.parse(self.xml_bomb2, forbid_entities=False)
        self.parseString(self.get_content(self.xml_bomb2),
                         forbid_entities=False)


class TestDefusedElementTree(BaseTests):
    module = ElementTree


    ## etree doesn't do external ref lookup
    #external_ref_exception = ElementTree.ParseError

    cyclic_error = ElementTree.ParseError

    def parse(self, xmlfile, **kwargs):
        tree = self.module.parse(xmlfile, **kwargs)
        return self.module.tostring(tree.getroot())

    def parseString(self, xmlstring, **kwargs):
        tree = self.module.fromstring(xmlstring, **kwargs)
        return self.module.tostring(tree)

    def iterparse(self, source, **kwargs):
        return list(self.module.iterparse(source, **kwargs))


class TestDefusedcElementTree(TestDefusedElementTree):
    module = cElementTree


class TestDefusedMinidom(BaseTests):
    module = minidom

    cyclic_error = ExpatError


    iterparse = None

    def parse(self, xmlfile, **kwargs):
        doc = self.module.parse(xmlfile, **kwargs)
        return doc.toxml()

    def parseString(self, xmlstring, **kwargs):
        doc = self.module.parseString(xmlstring, **kwargs)
        return doc.toxml()


class TestDefusedPulldom(BaseTests):
    module = pulldom

    cyclic_error = SAXParseException

    dtd_external_ref = True

    def parse(self, xmlfile, **kwargs):
        events = self.module.parse(xmlfile, **kwargs)
        return list(events)

    def parseString(self, xmlstring, **kwargs):
        events = self.module.parseString(xmlstring, **kwargs)
        return list(events)


class TestDefusedSax(BaseTests):
    module = sax

    cyclic_error = SAXParseException

    content_binary = True
    dtd_external_ref = True

    def parse(self, xmlfile, **kwargs):
        if PY3:
            result = io.StringIO()
        else:
            result = io.BytesIO()
        handler = XMLGenerator(result)
        self.module.parse(xmlfile, handler, **kwargs)
        return result.getvalue()

    def parseString(self, xmlstring, **kwargs):
        if PY3:
            result = io.StringIO()
        else:
            result = io.BytesIO()
        handler = XMLGenerator(result)
        self.module.parseString(xmlstring, handler, **kwargs)
        return result.getvalue()

    def test_exceptions(self):
        if PY26:
            # Python 2.6 unittest doesn't support with self.assertRaises()
            return

        with self.assertRaises(EntitiesForbidden) as ctx:
            self.parse(self.xml_bomb)
        msg = "EntitiesForbidden(name='a', system_id=None, public_id=None)"
        self.assertEqual(str(ctx.exception), msg)
        self.assertEqual(repr(ctx.exception), msg)

        with self.assertRaises(ExternalReferenceForbidden) as ctx:
            self.parse(self.xml_external, forbid_entities=False)
        msg = ("ExternalReferenceForbidden"
               "(system_id='http://www.w3schools.com/xml/note.xml', public_id=None)")
        self.assertEqual(str(ctx.exception), msg)
        self.assertEqual(repr(ctx.exception), msg)

        with self.assertRaises(DTDForbidden) as ctx:
            self.parse(self.xml_bomb, forbid_dtd=True)
        msg = "DTDForbidden(name='xmlbomb', system_id=None, public_id=None)"
        self.assertEqual(str(ctx.exception), msg)
        self.assertEqual(repr(ctx.exception), msg)


class TestDefusedLxml(BaseTests):
    module = lxml

    cyclic_error = XMLSyntaxError

    content_binary = True

    def parse(self, xmlfile, **kwargs):
        tree = self.module.parse(xmlfile, **kwargs)
        return self.module.tostring(tree)

    def parseString(self, xmlstring, **kwargs):
        tree = self.module.fromstring(xmlstring, **kwargs)
        return self.module.tostring(tree)

    if not LXML3:
        def test_entities_forbidden(self):
            self.assertRaises(NotSupportedError, self.parse, self.xml_bomb)

        def test_dtd_with_external_ref(self):
            self.assertRaises(NotSupportedError, self.parse, self.xml_dtd)

    def test_external_ref(self):
        pass

    def test_external_file_ref(self):
        pass

    def test_restricted_element1(self):
        tree = self.module.parse(self.xml_bomb, forbid_dtd=False,
                                 forbid_entities=False)
        root = tree.getroot()
        self.assertEqual(root.text, None)

        self.assertEqual(list(root), [])
        self.assertEqual(root.getchildren(), [])
        self.assertEqual(list(root.iter()), [root])
        self.assertEqual(list(root.iterchildren()), [])
        self.assertEqual(list(root.iterdescendants()), [])
        self.assertEqual(list(root.itersiblings()), [])
        self.assertEqual(list(root.getiterator()), [root])
        self.assertEqual(root.getnext(), None)

    def test_restricted_element2(self):
        tree = self.module.parse(self.xml_bomb2, forbid_dtd=False,
                                 forbid_entities=False)
        root = tree.getroot()
        bomb, tag = root
        self.assertEqual(root.text, "text")

        self.assertEqual(list(root), [bomb, tag])
        self.assertEqual(root.getchildren(), [bomb, tag])
        self.assertEqual(list(root.iter()), [root, bomb, tag])
        self.assertEqual(list(root.iterchildren()), [bomb, tag])
        self.assertEqual(list(root.iterdescendants()), [bomb, tag])
        self.assertEqual(list(root.itersiblings()), [])
        self.assertEqual(list(root.getiterator()), [root, bomb, tag])
        self.assertEqual(root.getnext(), None)
        self.assertEqual(root.getprevious(), None)

        self.assertEqual(list(bomb.itersiblings()), [tag])
        self.assertEqual(bomb.getnext(), tag)
        self.assertEqual(bomb.getprevious(), None)
        self.assertEqual(tag.getnext(), None)
        self.assertEqual(tag.getprevious(), bomb)

    def test_xpath_injection(self):
        # show XPath injection vulnerability
        xml = """<root><tag id="one" /><tag id="two"/></root>"""
        expr = "one' or @id='two"
        root = lxml.fromstring(xml)

        # insecure way
        xp = "tag[@id='%s']" % expr
        elements = root.xpath(xp)
        self.assertEqual(len(elements), 2)
        self.assertEqual(elements, list(root))

        # proper and safe way
        xp = "tag[@id=$idname]"
        elements = root.xpath(xp, idname=expr)
        self.assertEqual(len(elements), 0)
        self.assertEqual(elements, [])

        elements = root.xpath(xp, idname="one")
        self.assertEqual(len(elements), 1)
        self.assertEqual(elements, list(root)[:1])


class XmlRpcTarget(object):
    def __init__(self):
        self._data = []

    def __str__(self):
        return "".join(self._data)

    def xml(self, encoding, standalone):
        pass

    def start(self, tag, attrs):
        self._data.append("<%s>" % tag)

    def data(self, text):
        self._data.append(text)

    def end(self, tag):
        self._data.append("</%s>" % tag)

class TestXmlRpc(DefusedTestCase):
    module = xmlrpc
    def parse(self, xmlfile, **kwargs):
        target = XmlRpcTarget()
        parser = self.module.DefusedExpatParser(target, **kwargs)
        data = self.get_content(xmlfile)
        parser.feed(data)
        parser.close()
        return target

    def parse_unpatched(self, xmlfile):
        target = XmlRpcTarget()
        parser = self.module.ExpatParser(target)
        data = self.get_content(xmlfile)
        parser.feed(data)
        parser.close()
        return target

    def test_xmlrpc(self):
        self.assertRaises(EntitiesForbidden, self.parse, self.xml_bomb)
        self.assertRaises(EntitiesForbidden, self.parse, self.xml_quadratic)
        self.parse(self.xml_dtd)
        self.assertRaises(DTDForbidden, self.parse, self.xml_dtd,
                          forbid_dtd=True)

    #def test_xmlrpc_unpatched(self):
    #    for fname in (self.xml_external,  self.xml_dtd):
    #        print(self.parse_unpatched(fname))

    def test_monkeypatch(self):
        try:
            xmlrpc.monkey_patch()
        finally:
            xmlrpc.unmonkey_patch()


class TestDefusedGzip(DefusedTestCase):
    def get_gzipped(self, length):
        f = io.BytesIO()
        gzf = gzip.GzipFile(mode="wb", fileobj=f)
        gzf.write(b"d" * length)
        gzf.close()
        f.seek(0)
        return f

    def decode_response(self, response, limit=None, readlength=1024):
        dec = xmlrpc.DefusedGzipDecodedResponse(response, limit)
        acc = []
        while True:
            data = dec.read(readlength)
            if not data:
                break
            acc.append(data)
        return b"".join(acc)

    def test_defused_gzip_decode(self):
        data = self.get_gzipped(4096).getvalue()
        result = xmlrpc.defused_gzip_decode(data)
        self.assertEqual(result, b"d" *4096)
        result = xmlrpc.defused_gzip_decode(data, -1)
        self.assertEqual(result, b"d" *4096)
        result = xmlrpc.defused_gzip_decode(data, 4096)
        self.assertEqual(result, b"d" *4096)
        with self.assertRaises(ValueError):
            result = xmlrpc.defused_gzip_decode(data, 4095)
        with self.assertRaises(ValueError):
            result = xmlrpc.defused_gzip_decode(data, 0)

    def test_defused_gzip_response(self):
        clen = len(self.get_gzipped(4096).getvalue())

        response = self.get_gzipped(4096)
        data = self.decode_response(response)
        self.assertEqual(data, b"d" *4096)

        with self.assertRaises(ValueError):
            response = self.get_gzipped(4096)
            xmlrpc.DefusedGzipDecodedResponse(response, clen - 1)

        with self.assertRaises(ValueError):
            response = self.get_gzipped(4096)
            self.decode_response(response, 4095)

        with self.assertRaises(ValueError):
            response = self.get_gzipped(4096)
            self.decode_response(response, 4095, 8192)


def test_main():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestDefusedcElementTree))
    suite.addTests(unittest.makeSuite(TestDefusedElementTree))
    suite.addTests(unittest.makeSuite(TestDefusedMinidom))
    suite.addTests(unittest.makeSuite(TestDefusedPulldom))
    suite.addTests(unittest.makeSuite(TestDefusedSax))
    suite.addTests(unittest.makeSuite(TestXmlRpc))
    if lxml is not None:
        suite.addTests(unittest.makeSuite(TestDefusedLxml))
    if gzip is not None:
        suite.addTests(unittest.makeSuite(TestDefusedGzip))
    return suite

if __name__ == "__main__":
    suite = test_main()
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    # TODO: test that it actually works
    defuse_stdlib()
    sys.exit(not result.wasSuccessful())
