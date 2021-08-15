import tempfile
import uuid
from django.http import HttpRequest, QueryDict
from indexer.api3 import guess_field_types
from nose.tools import assert_equal, assert_true


def test_local_file_header_reformatting_with_header():
    with open('apps/beeswax/data/tables/testbook1.csv', encoding='utf-8-sig') as upload_file:
        username = 'test_user'
        filename = "%s_%s:%s;" % (username, uuid.uuid4(), upload_file.name)
        temp_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        temp_file.write(bytes(upload_file.read(), encoding='utf-8'))
        local_file_url = temp_file.name
        temp_file.close()

    data = {'fileFormat':'{"inputFormat":"localfile","path": "%s","format":{"hasHeader":true}}' % local_file_url}
    request = HttpRequest()
    q = QueryDict(mutable=True)
    q.update(data)
    request.POST = q
    out = guess_field_types(request)
    out = out.content
    assert_equal(b'{"columns": [{"name": "test_1", "type": "string", "unique": false, "keep": true, "operations": [], "required": false, "multiValued": false, "showProperties": false, "nested": [], "level": 0, "length": 100, "keyType": "string", "isPartition": false, "partitionValue": "", "comment": "", "scale": 0, "precision": 10}, {"name": "test_2", "type": "string", "unique": false, "keep": true, "operations": [], "required": false, "multiValued": false, "showProperties": false, "nested": [], "level": 0, "length": 100, "keyType": "string", "isPartition": false, "partitionValue": "", "comment": "", "scale": 0, "precision": 10}, {"name": "test_3", "type": "string", "unique": false, "keep": true, "operations": [], "required": false, "multiValued": false, "showProperties": false, "nested": [], "level": 0, "length": 100, "keyType": "string", "isPartition": false, "partitionValue": "", "comment": "", "scale": 0, "precision": 10}, {"name": "test_4", "type": "string", "unique": false, "keep": true, "operations": [], "required": false, "multiValued": false, "showProperties": false, "nested": [], "level": 0, "length": 100, "keyType": "string", "isPartition": false, "partitionValue": "", "comment": "", "scale": 0, "precision": 10}], "sample": [["10/10/10", "1:00:00 AM", "$30.00", ""], ["Sunday, October 10, 2021", "3:00", " 1/8", ""], ["2010-10-10", "9:00 AM", "99.00%", ""], ["10/10", "4:00:00", "500", ""]]}',out)
    
   