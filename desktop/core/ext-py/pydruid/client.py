#
# Copyright 2013 Metamarkets Group Inc.
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
import re

from six.moves import urllib

from pydruid.query import QueryBuilder
from base64 import b64encode


# extract error from the <PRE> tag inside the HTML response
HTML_ERROR = re.compile('<pre>\s*(.*?)\s*</pre>', re.IGNORECASE)


class BaseDruidClient(object):
    def __init__(self, url, endpoint):
        self.url = url
        self.endpoint = endpoint
        self.query_builder = QueryBuilder()
        self.username = None
        self.password = None

    def set_basic_auth_credentials(self, username, password):
        self.username = username
        self.password = password

    def _prepare_url_headers_and_body(self, query):
        querystr = json.dumps(query.query_dict).encode('utf-8')
        if self.url.endswith('/'):
            url = self.url + self.endpoint
        else:
            url = self.url + '/' + self.endpoint
        headers = {'Content-Type': 'application/json'}
        if (self.username is not None) and (self.password is not None):
            authstring = '{}:{}'.format(self.username, self.password)
            b64string = b64encode(authstring.encode()).decode()
            headers['Authorization'] = 'Basic {}'.format(b64string)

        return headers, querystr, url

    def _post(self, query):
        """
        Fills Query object with results.

        :param Query query: query to execute

        :return: Query filled with results
        :rtype: Query
        """
        raise NotImplementedError("Subclasses must implement this method")

    # --------- Query implementations ---------

    def topn(self, **kwargs):
        """
        A TopN query returns a set of the values in a given dimension,
        sorted by a specified metric. Conceptually, a topN can be
        thought of as an approximate GroupByQuery over a single
        dimension with an Ordering spec. TopNs are
        faster and more resource efficient than GroupBy for this use case.

        Required key/value pairs:

        :param str datasource: Data source to query
        :param str granularity: Aggregate data by hour, day, minute, etc.,
        :param intervals: ISO-8601 intervals of data to query
        :type intervals: str or list
        :param dict aggregations: A map from aggregator name to one of
          the pydruid.utils.aggregators e.g., doublesum
        :param str dimension: Dimension to run the query against
        :param str metric: Metric over which to sort the specified dimension by
        :param int threshold: How many of the top items to return

        :return: The query result
        :rtype: Query

        Optional key/value pairs:

        :param pydruid.utils.filters.Filter filter: Indicates which rows
          of data to include in the query
        :param post_aggregations:   A dict with string key = 'post_aggregator_name',
          and value pydruid.utils.PostAggregator
        :param dict context: A dict of query context options

        Example:

        .. code-block:: python
            :linenos:

                >>> top = client.topn(
                            datasource='twitterstream',
                            granularity='all',
                            intervals='2013-06-14/pt1h',
                            aggregations={"count": doublesum("count")},
                            dimension='user_name',
                            metric='count',
                            filter=Dimension('user_lang') == 'en',
                            threshold=1,
                            context={"timeout": 1000}
                        )
                >>> print top
                >>> [{'timestamp': '2013-06-14T00:00:00.000Z',
                    'result': [{'count': 22.0, 'user': "cool_user"}}]}]
        """
        query = self.query_builder.topn(kwargs)
        return self._post(query)

    def timeseries(self, **kwargs):
        """
        A timeseries query returns the values of the requested metrics (in aggregate)
        for each timestamp.

        Required key/value pairs:

        :param str datasource: Data source to query
        :param str granularity: Time bucket to aggregate data by hour, day, minute, etc.,
        :param intervals: ISO-8601 intervals for which to run the query on
        :type intervals: str or list
        :param dict aggregations: A map from aggregator name to one of the
          ``pydruid.utils.aggregators`` e.g., ``doublesum``

        :return: The query result
        :rtype: Query

        Optional key/value pairs:

        :param pydruid.utils.filters.Filter filter: Indicates which rows of
          data to include in the query
        :param post_aggregations:   A dict with string key =
          'post_aggregator_name', and value pydruid.utils.PostAggregator
        :param dict context: A dict of query context options

        Example:

        .. code-block:: python
            :linenos:

                >>> counts = client.timeseries(
                        datasource=twitterstream,
                        granularity='hour',
                        intervals='2013-06-14/pt1h',
                        aggregations=\
                            {"count": doublesum("count"), "rows": count("rows")},
                        post_aggregations=\
                            {'percent': (Field('count') / Field('rows')) * Const(100))},
                        context={"timeout": 1000}
                    )
                >>> print counts
                >>> [{'timestamp': '2013-06-14T00:00:00.000Z',
                    'result': {'count': 9619.0, 'rows': 8007,
                    'percent': 120.13238416385663}}]
        """
        query = self.query_builder.timeseries(kwargs)
        return self._post(query)

    def groupby(self, **kwargs):
        """
        A group-by query groups a results set (the requested aggregate
        metrics) by the specified dimension(s).

        Required key/value pairs:

        :param str datasource: Data source to query
        :param str granularity: Time bucket to aggregate data by hour, day, minute, etc.,
        :param intervals: ISO-8601 intervals for which to run the query on
        :type intervals: str or list
        :param dict aggregations: A map from aggregator name to one of the
          ``pydruid.utils.aggregators`` e.g., ``doublesum``
        :param list dimensions: The dimensions to group by

        :return: The query result
        :rtype: Query

        Optional key/value pairs:

        :param pydruid.utils.filters.Filter filter: Indicates which rows of
          data to include in the query
        :param pydruid.utils.having.Having having: Indicates which groups
          in results set of query to keep
        :param post_aggregations:   A dict with string key = 'post_aggregator_name',
          and value pydruid.utils.PostAggregator
        :param dict context: A dict of query context options
        :param dict limit_spec: A dict of parameters defining how to limit
          the rows returned, as specified in the Druid api documentation

        Example:

        .. code-block:: python
            :linenos:

                >>> group = client.groupby(
                        datasource='twitterstream',
                        granularity='hour',
                        intervals='2013-10-04/pt1h',
                        dimensions=["user_name", "reply_to_name"],
                        filter=~(Dimension("reply_to_name") == "Not A Reply"),
                        aggregations={"count": doublesum("count")},
                        context={"timeout": 1000}
                        limit_spec={
                            "type": "default",
                            "limit": 50,
                            "columns" : ["count"]
                        }
                    )
                >>> for k in range(2):
                    ...     print group[k]
                >>> {
                    'timestamp': '2013-10-04T00:00:00.000Z',
                    'version': 'v1',
                    'event': {
                        'count': 1.0,
                        'user_name': 'user_1',
                        'reply_to_name': 'user_2',
                    }
                }
                >>> {
                    'timestamp': '2013-10-04T00:00:00.000Z',
                    'version': 'v1',
                    'event': {
                        'count': 1.0,
                        'user_name': 'user_2',
                        'reply_to_name':
                        'user_3',
                    }
                }
        """
        query = self.query_builder.groupby(kwargs)
        return self._post(query)

    def segment_metadata(self, **kwargs):
        """
        A segment meta-data query returns per segment information about:

        * Cardinality of all the columns present
        * Column type
        * Estimated size in bytes
        * Estimated size in bytes of each column
        * Interval the segment covers
        * Segment ID

        Required key/value pairs:

        :param str datasource: Data source to query
        :param intervals: ISO-8601 intervals for which to run the query on
        :type intervals: str or list

        Optional key/value pairs:

        :param dict context: A dict of query context options

        :return: The query result
        :rtype: Query

        Example:

        .. code-block:: python
            :linenos:

                >>> meta = client.segment_metadata(
                    datasource='twitterstream', intervals = '2013-10-04/pt1h')
                >>> print meta[0].keys()
                >>> ['intervals', 'id', 'columns', 'size']
                >>> print meta[0]['columns']['tweet_length']
                >>> {
                    'errorMessage': None,
                    'cardinality': None,
                    'type': 'FLOAT',
                    'size': 30908008,
                }

        """
        query = self.query_builder.segment_metadata(kwargs)
        return self._post(query)

    def time_boundary(self, **kwargs):
        """
        A time boundary query returns the min and max timestamps present in a data source.

        Required key/value pairs:

        :param str datasource: Data source to query

        Optional key/value pairs:

        :param dict context: A dict of query context options

        :return: The query result
        :rtype: Query

        Example:

        .. code-block:: python
            :linenos:

                >>> bound = client.time_boundary(datasource='twitterstream')
                >>> print bound
                >>> [{
                    'timestamp': '2011-09-14T15:00:00.000Z',
                    'result': {
                        'minTime': '2011-09-14T15:00:00.000Z',
                        'maxTime': '2014-03-04T23:44:00.000Z',
                    }
                }]
        """
        query = self.query_builder.time_boundary(kwargs)
        return self._post(query)

    def select(self, **kwargs):
        """
        A select query returns raw Druid rows and supports pagination.

        Required key/value pairs:

        :param str datasource: Data source to query
        :param str granularity: Time bucket to aggregate data by hour, day, minute, etc.
        :param dict paging_spec: Indicates offsets into different scanned segments
        :param intervals: ISO-8601 intervals for which to run the query on
        :type intervals: str or list

        Optional key/value pairs:

        :param pydruid.utils.filters.Filter filter: Indicates which rows of
          data to include in the query
        :param list dimensions: The list of dimensions to select. If left
          empty, all dimensions are returned
        :param list metrics: The list of metrics to select. If left empty,
          all metrics are returned
        :param dict context: A dict of query context options

        :return: The query result
        :rtype: Query

        Example:

        .. code-block:: python
            :linenos:

                >>> raw_data = client.select(
                        datasource=twitterstream,
                        granularity='all',
                        intervals='2013-06-14/pt1h',
                        paging_spec={'pagingIdentifies': {}, 'threshold': 1},
                        context={"timeout": 1000}
                    )
                >>> print(raw_data)
                >>> [{
                    'timestamp': '2013-06-14T00:00:00.000Z',
                    'result': {
                        'pagingIdentifiers': {
                            'twitterstream_...08:00:00.000Z_v1': 1,
                            'events': [{
                                'segmentId': 'twitterstr...000Z_v1',
                                'offset': 0,
                                'event': {
                                    'timestamp': '2013-06-14T00:00:00.000Z',
                                    'dim': 'value',
                                }
                            }]
                        }
                }]
        """
        query = self.query_builder.select(kwargs)
        return self._post(query)

    def export_tsv(self, dest_path):
        """
        Export the current query result to a tsv file.

        .. deprecated::
            Use Query.export_tsv() method instead.
        """
        if self.query_builder.last_query is None:
            raise AttributeError(
                "There was no query executed by this client yet. Can't export!")
        else:
            return self.query_builder.last_query.export_tsv(dest_path)

    def export_pandas(self):
        """
        Export the current query result to a Pandas DataFrame object.

        .. deprecated::
            Use Query.export_pandas() method instead
        """
        if self.query_builder.last_query is None:
            raise AttributeError(
                "There was no query executed by this client yet. Can't export!")
        else:
            return self.query_builder.last_query.export_pandas()


class PyDruid(BaseDruidClient):
    """
    PyDruid contains the functions for creating and executing Druid queries.
    Returns Query objects that can be used for exporting query results
    into TSV files or pandas.DataFrame objects for subsequent analysis.

    :param str url: URL of Broker node in the Druid cluster
    :param str endpoint: Endpoint that Broker listens for queries on

    Example

    .. code-block:: python
        :linenos:

            >>> from pydruid.client import *

            >>> query = PyDruid('http://localhost:8083', 'druid/v2/')

            >>> top = query.topn(
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
            >>> [{
                'timestamp': '2013-10-04T00:00:00.000Z',
                'result': [
                    {
                        'count': 7.0,
                        'user_name': 'user_1',
                    },
                    {
                        'count': 6.0,
                        'user_name': 'user_2',
                    },
                ]}]

            >>> df = top.export_pandas()
            >>> print df
            >>>    count                 timestamp      user_name
                0      7  2013-10-04T00:00:00.000Z         user_1
                1      6  2013-10-04T00:00:00.000Z         user_2
    """
    def __init__(self, url, endpoint):
        super(PyDruid, self).__init__(url, endpoint)

    def _post(self, query):
        try:
            headers, querystr, url = self._prepare_url_headers_and_body(query)
            req = urllib.request.Request(url, querystr, headers)
            res = urllib.request.urlopen(req)
            data = res.read().decode("utf-8")
            res.close()
        except urllib.error.HTTPError as e:
            err = e.reason
            if e.code == 500:
                # has Druid returned an error?
                try:
                    err = json.loads(err)
                except ValueError:
                    if HTML_ERROR.search(err):
                        err = HTML_ERROR.search(err).group(1)
                except (ValueError, AttributeError, KeyError):
                    pass

            raise IOError('{0} \n Druid Error: {1} \n Query is: {2}'.format(
                    e, err, json.dumps(
                        query.query_dict,
                        indent=4,
                        sort_keys=True,
                        separators=(',', ': '))))
        else:
            query.parse(data)
            return query

    def scan(self, **kwargs):
        """
        A scan query returns raw Druid rows

        Required key/value pairs:

        :param str datasource: Data source to query
        :param str granularity: Time bucket to aggregate data by hour, day, minute, etc.
        :param int limit: The maximum number of rows to return
        :param intervals: ISO-8601 intervals for which to run the query on
        :type intervals: str or list

        Optional key/value pairs:

        :param pydruid.utils.filters.Filter filter: Indicates which rows of
          data to include in the query
        :param list dimensions: The list of dimensions to select. If left
          empty, all dimensions are returned
        :param list metrics: The list of metrics to select. If left empty,
          all metrics are returned
        :param dict context: A dict of query context options

        :return: The query result
        :rtype: Query

        Example:

        .. code-block:: python
            :linenos:

                >>> raw_data = client.scan(
                        datasource=twitterstream,
                        granularity='all',
                        intervals='2013-06-14/pt1h',
                        limit=1,
                        context={"timeout": 1000}
                    )
                >>> print raw_data
                >>> [{
                    u'segmentId': u'zzzz',
                    u'columns': [u'__time', 'status', 'region'],
                    'events': [{
                        u'status': u'ok', 'region': u'SF', u'__time': 1509494400000,
                    }]
                }]
        """
        query = self.query_builder.scan(kwargs)
        return self._post(query)
