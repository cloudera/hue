import json
import codecs
import tempfile
from django.http import HttpRequest, QueryDict
from indexer.api3 import upload_local_file
from nose.tools import assert_equal, assert_true
from django.utils.datastructures import MultiValueDict
from django.core.files.uploadhandler import InMemoryUploadedFile
from urllib.parse import urlparse, unquote as urllib_unquote

def test_xlsx_local_file_upload():

    class User:
        def __init__(self, username='test'):
            self.username = username
    
    with open('apps/beeswax/data/tables/testbook1.xlsx','rb') as file:
        #must keep indentation like this or file will leave scope and not get read by xlsxreader
        f = InMemoryUploadedFile(file=file,field_name='test',name='testbook1.xlsx', content_type='xlsx',size=100,charset='utf-8')
        request = HttpRequest()
        request.user = User()
        request.FILES = MultiValueDict({'file': [f]})
        response = upload_local_file(request)
    path = urllib_unquote(json.loads(response.content.decode('utf-8'))['local_file_url'])
    with open(path, 'r') as test_file:
        test = test_file.read()
        with open('apps/beeswax/data/tables/testbook1.csv', 'r') as correct_file:
            correct = correct_file.read()
        assert_equal(correct, test)