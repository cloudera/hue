#
# Copyright 2016 Metamarkets Group Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import division
from __future__ import absolute_import

import json
from pydruid.client import BaseDruidClient

try:
    from tornado import gen
    from tornado.httpclient import AsyncHTTPClient, HTTPError
except ImportError:
    print('Warning: unable to import Tornado. The asynchronous client will not work.')


class AsyncPyDruid(BaseDruidClient):
    """
    Asynchronous PyDruid client which mirrors functionality of the synchronous
    PyDruid, but it executes queries
    asynchronously (using an asynchronous http client from Tornado framework).

    Returns Query objects that can be used for exporting query results into
    TSV files or pandas.DataFrame objects
    for subsequent analysis.

    :param str url: URL of Broker node in the Druid cluster
    :param str endpoint: Endpoint that Broker listens for queries on

    Example

    .. code-block:: python
        :linenos:

            >>> from pydruid.async_client import *

            >>> query = AsyncPyDruid('http://localhost:8083', 'druid/v2/')

            >>> top = yield query.topn(
                    datasource='twitterstream',
                    granularity='all',
                    intervals='2013-10-04/pt1h',
                    aggregations={"count": doublesum("count")},
                    dimension='user_name',
                    filter = Dimension('user_lang') == 'en',
                    metric='count',
                    threshold=2
                )

            >>> print json.dumps(top.query_dict, indent=2)
            >>> {
                  "metric": "count",
                  "aggregations": [
                    {
                      "type": "doubleSum",
                      "fieldName": "count",
                      "name": "count"
                    }
                  ],
                  "dimension": "user_name",
                  "filter": {
                    "type": "selector",
                    "dimension": "user_lang",
                    "value": "en"
                  },
                  "intervals": "2013-10-04/pt1h",
                  "dataSource": "twitterstream",
                  "granularity": "all",
                  "threshold": 2,
                  "queryType": "topN"
                }

            >>> print top.result
            >>> [{'timestamp': '2013-10-04T00:00:00.000Z',
                'result': [{'count': 7.0, 'user_name': 'user_1'},
                {'count': 6.0, 'user_name': 'user_2'}]}]

            >>> df = top.export_pandas()
            >>> print df
            >>>    count                 timestamp      user_name
                0      7  2013-10-04T00:00:00.000Z         user_1
                1      6  2013-10-04T00:00:00.000Z         user_2
    """

    def __init__(self, url, endpoint):
        super(AsyncPyDruid, self).__init__(url, endpoint)

    @gen.coroutine
    def _post(self, query):
        http_client = AsyncHTTPClient()
        try:
            headers, querystr, url = self._prepare_url_headers_and_body(query)
            response = yield http_client.fetch(
                url, method='POST', headers=headers, body=querystr)
        except HTTPError as e:
            self.__handle_http_error(e, query)
        else:
            query.parse(response.body.decode("utf-8"))
            raise gen.Return(query)

    @staticmethod
    def __handle_http_error(e, query):
        err = None
        if e.code == 500:
            # has Druid returned an error?
            try:
                err = json.loads(e.response.body.decode("utf-8"))
            except ValueError:
                pass
            else:
                err = err.get('error', None)
        raise IOError('{0} \n Druid Error: {1} \n Query is: {2}'.format(
                e, err, json.dumps(query.query_dict, indent=4)))

    @gen.coroutine
    def topn(self, **kwargs):
        query = self.query_builder.topn(kwargs)
        result = yield self._post(query)
        raise gen.Return(result)

    @gen.coroutine
    def timeseries(self, **kwargs):
        query = self.query_builder.timeseries(kwargs)
        result = yield self._post(query)
        raise gen.Return(result)

    @gen.coroutine
    def groupby(self, **kwargs):
        query = self.query_builder.groupby(kwargs)
        result = yield self._post(query)
        raise gen.Return(result)

    @gen.coroutine
    def segment_metadata(self, **kwargs):
        query = self.query_builder.segment_metadata(kwargs)
        result = yield self._post(query)
        raise gen.Return(result)

    @gen.coroutine
    def time_boundary(self, **kwargs):
        query = self.query_builder.time_boundary(kwargs)
        result = yield self._post(query)
        raise gen.Return(result)

    @gen.coroutine
    def select(self, **kwargs):
        query = self.query_builder.select(kwargs)
        result = yield self._post(query)
        raise gen.Return(result)
