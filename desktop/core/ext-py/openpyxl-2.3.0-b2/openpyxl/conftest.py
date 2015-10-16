import pytest

# Global objects under tests

@pytest.fixture
def Workbook():
    """Workbook Class"""
    from openpyxl import Workbook
    return Workbook


@pytest.fixture
def Worksheet():
    """Worksheet Class"""
    from openpyxl.worksheet import Worksheet
    return Worksheet


# Global fixtures

@pytest.fixture
def root_xml():
    """Root XML element <test>"""
    from openpyxl.xml.functions import Element
    return Element("test")


### Markers ###

def pytest_runtest_setup(item):
    if isinstance(item, item.Function):
        try:
            from PIL import Image
        except ImportError:
            Image = False
        if item.get_marker("pil_required") and Image is False:
            pytest.skip("PIL must be installed")
        elif item.get_marker("pil_not_installed") and Image:
            pytest.skip("PIL is installed")
        elif item.get_marker("not_py33"):
            pytest.skip("Ordering is not a given in Python 3")
        elif item.get_marker("lxml_required"):
            from openpyxl import LXML
            if not LXML:
                pytest.skip("LXML is required for some features such as schema validation")
        elif item.get_marker("lxml_buffering"):
            from lxml.etree import LIBXML_VERSION
            if LIBXML_VERSION < (3, 4, 0, 0):
                pytest.skip("LXML >= 3.4 is required")

