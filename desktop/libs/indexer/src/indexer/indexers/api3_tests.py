from django.http import HttpRequest, QueryDict
from indexer.api3 import upload_local_file
from nose.tools import assert_equal, assert_true

def test_xlsx_local_file_upload():
    request = HttpRequest()
    request.FILES