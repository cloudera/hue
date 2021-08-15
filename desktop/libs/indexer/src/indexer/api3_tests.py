import tempfile
import uuid
from desktop.lib.paths import get_desktop_root
from django.http import HttpRequest, QueryDict
from indexer.api3 import guess_field_types
from nose.tools import assert_equal, assert_true


def test_local_file_header_reformatting_with_header():
    username = 'test_user'
    filename = "%s_%s:testbook1.csv;" % (username, uuid.uuid4())
    temp_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
    temp_file.write(b'test 1,test.2,test_3,test_4\n10/10/10,1:00:00 AM,$30.00,\n"Sunday, October 10, 2021",3:00, 1/8,\n2010-10-10,9:00 AM,99.00%,\n10/10,4:00:00,500,\n10/10/10,9:00:00 AM,2.98E+04,\n10/10/10,00:00.0,50      ,\n10-Oct,988639:00:00,,\n10-Oct-10,10/11/12 3:00 AM,,\n10-Oct-10,10/11/12 9:00,,\nOct-10,10/10/22 2:00 PM,,\n\nOctober-10,10/10/21 15:00,,\n"October 10, 2010",,,\nO,,,\nO-10,scattered,,\n10/10/2010,,scattered,\n10-Oct-2010,,,\n,,,\n,,,\nscattered,,,\n,,scattered,\n,,,\n,,,\n,scattered,,\n,,,\n,,,\n,,,\nscattered,,,scattered\n,,,\n,,,\n,,,\n,,,\n,scattered,,')
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