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

import six
import json
import collections
from pydruid.utils.aggregators import build_aggregators
from pydruid.utils.filters import Filter
from pydruid.utils.having import Having
from pydruid.utils.dimensions import build_dimension
from pydruid.utils.postaggregator import Postaggregator
from pydruid.utils.query_utils import UnicodeWriter


class Query(collections.MutableSequence):
    """
    Query objects are produced by PyDruid clients and can be used for
    exporting query results into TSV files or
    pandas.DataFrame objects for subsequent analysis. They also hold
    information about the issued query.

    Query acts as a wrapper over raw result list of dictionaries.

    :ivar str result_json: JSON object representing a query result. Initial value: None
    :ivar list result: Query result parsed into a list of dicts. Initial value: None
    :ivar str query_type: Name of most recently run query, e.g., topN. Initial value: None
    :ivar dict query_dict: JSON object representing the query. Initial value: None
    """

    def __init__(self, query_dict, query_type):
        super(Query, self).__init__()
        self.query_dict = query_dict
        self.query_type = query_type
        self.result = None
        self.result_json = None

    def parse(self, data):
        if data:
            self.result_json = data
            res = json.loads(self.result_json)
            self.result = res
        else:
            raise IOError('{Error parsing result: {0} for {1} query'.format(
                    self.result_json, self.query_type))

    def export_tsv(self, dest_path):
        """
        Export the current query result to a tsv file.

        :param str dest_path: file to write query results to
        :raise NotImplementedError:

        Example

        .. code-block:: python
            :linenos:

                >>> top = client.topn(
                        datasource='twitterstream',
                        granularity='all',
                        intervals='2013-10-04/pt1h',
                        aggregations={"count": doublesum("count")},
                        dimension='user_name',
                        filter = Dimension('user_lang') == 'en',
                        metric='count',
                        threshold=2
                    )

                >>> top.export_tsv('top.tsv')
                >>> !cat top.tsv
                >>> count	user_name	timestamp
                    7.0	user_1	2013-10-04T00:00:00.000Z
                    6.0	user_2	2013-10-04T00:00:00.000Z
        """
        if six.PY3:
            f = open(dest_path, 'w', newline='', encoding='utf-8')
        else:
            f = open(dest_path, 'wb')
        w = UnicodeWriter(f)

        if self.query_type == "timeseries":
            header = list(self.result[0]['result'].keys())
            header.append('timestamp')
        elif self.query_type == 'topN':
            header = list(self.result[0]['result'][0].keys())
            header.append('timestamp')
        elif self.query_type == "groupBy":
            header = list(self.result[0]['event'].keys())
            header.append('timestamp')
            header.append('version')
        else:
            raise NotImplementedError(
                'TSV export not implemented for query type: {0}'.format(self.query_type))

        w.writerow(header)

        if self.result:
            if self.query_type == "topN" or self.query_type == "timeseries":
                for item in self.result:
                    timestamp = item['timestamp']
                    result = item['result']
                    if type(result) is list:  # topN
                        for line in result:
                            w.writerow(list(line.values()) + [timestamp])
                    else:  # timeseries
                        w.writerow(list(result.values()) + [timestamp])
            elif self.query_type == "groupBy":
                for item in self.result:
                    timestamp = item['timestamp']
                    version = item['version']
                    w.writerow(
                        list(item['event'].values()) + [timestamp] + [version])

        f.close()

    def export_pandas(self):
        """
        Export the current query result to a Pandas DataFrame object.

        :return: The DataFrame representing the query result
        :rtype: DataFrame
        :raise NotImplementedError:

        Example

        .. code-block:: python
            :linenos:

                >>> top = client.topn(
                        datasource='twitterstream',
                        granularity='all',
                        intervals='2013-10-04/pt1h',
                        aggregations={"count": doublesum("count")},
                        dimension='user_name',
                        filter = Dimension('user_lang') == 'en',
                        metric='count',
                        threshold=2
                    )

                >>> df = top.export_pandas()
                >>> print df
                >>>    count                 timestamp      user_name
                    0      7  2013-10-04T00:00:00.000Z         user_1
                    1      6  2013-10-04T00:00:00.000Z         user_2
        """
        import pandas

        if self.result:
            if self.query_type == "timeseries":
                nres = [list(v['result'].items()) + [('timestamp', v['timestamp'])]
                        for v in self.result]
                nres = [dict(v) for v in nres]
            elif self.query_type == "topN":
                nres = []
                for item in self.result:
                    timestamp = item['timestamp']
                    results = item['result']
                    tres = [dict(list(res.items()) + [('timestamp', timestamp)])
                            for res in results]
                    nres += tres
            elif self.query_type == "groupBy":
                nres = [list(v['event'].items()) + [('timestamp', v['timestamp'])]
                        for v in self.result]
                nres = [dict(v) for v in nres]
            elif self.query_type == "select":
                nres = []
                for item in self.result:
                    nres += [e.get('event') for e in item['result'].get('events')]
            elif self.query_type == "scan":
                nres = []
                for item in self.result:
                    nres += [e for e in item.get('events')]
            else:
                raise NotImplementedError(
                    'Pandas export not implemented for query '
                    'type: {0}'.format(self.query_type))

            df = pandas.DataFrame(nres)
            return df

    def __str__(self):
        return str(self.result)

    def __len__(self):
        return len(self.result)

    def __delitem__(self, index):
        del self.result[index]

    def insert(self, index, value):
        self.result.insert(index, value)

    def __setitem__(self, index, value):
        self.result[index] = value

    def __getitem__(self, index):
        return self.result[index]


class QueryBuilder(object):
    def __init__(self):
        self.last_query = None

    @staticmethod
    def parse_datasource(datasource, query_type):
        """
        Parse an input datasource object into valid dictionary

        Input can be a string, in which case it is simply returned, or a
        list, when it is turned into a UNION datasource.

        :param datasource: datasource parameter
        :param string query_type: query type
        :raise ValueError: if input is not string or list of strings
        """
        if not (
                    isinstance(datasource, six.string_types) or
                    (
                        isinstance(datasource, list) and
                        all([isinstance(x, six.string_types) for x in datasource])
                    )
                ):
            raise ValueError(
                'Datasource definition not valid. Must be string or list of strings')
        if isinstance(datasource, six.string_types):
            return datasource
        else:
            return {'type': 'union', 'dataSources': datasource}

    @staticmethod
    def validate_query(query_type, valid_parts, args):
        """
        Validate the query parts so only allowed objects are sent.

        Each query type can have an optional 'context' object attached which
        is used to set certain query context settings, etc. timeout or
        priority. As each query can have this object, there's
        no need for it to be sent - it might as well be added here.

        :param string query_type: a type of query
        :param list valid_parts: a list of valid object names
        :param dict args: the dict of args to be sent
        :raise ValueError: if an invalid object is given
        """
        valid_parts = valid_parts[:] + ['context']
        for key, val in six.iteritems(args):
            if key not in valid_parts:
                raise ValueError(
                        'Query component: {0} is not valid for query type: {1}.'
                        .format(key, query_type) +
                        'The list of valid components is: \n {0}'
                        .format(valid_parts))

    def build_query(self, query_type, args):
        """
        Build query based on given query type and arguments.

        :param string query_type: a type of query
        :param dict args: the dict of args to be sent
        :return: the resulting query
        :rtype: Query
        """
        query_dict = {'queryType': query_type}

        for key, val in six.iteritems(args):
            if key == 'aggregations':
                query_dict[key] = build_aggregators(val)
            elif key == 'post_aggregations':
                query_dict['postAggregations'] = \
                    Postaggregator.build_post_aggregators(val)
            elif key == 'context':
                query_dict['context'] = val
            elif key == 'datasource':
                query_dict['dataSource'] = self.parse_datasource(val, query_type)
            elif key == 'paging_spec':
                query_dict['pagingSpec'] = val
            elif key == 'limit_spec':
                query_dict['limitSpec'] = val
            elif key == "filter" and val is not None:
                query_dict[key] = Filter.build_filter(val)
            elif key == "having" and val is not None:
                query_dict[key] = Having.build_having(val)
            elif key == 'dimension' and val is not None:
                query_dict[key] = build_dimension(val)
            elif key == 'dimensions':
                query_dict[key] = [build_dimension(v) for v in val]
            else:
                query_dict[key] = val

        self.last_query = Query(query_dict, query_type)
        return self.last_query

    def topn(self, args):
        """
        A TopN query returns a set of the values in a given dimension,
        sorted by a specified metric. Conceptually, a
        topN can be thought of as an approximate GroupByQuery over a
        single dimension with an Ordering spec. TopNs are
        faster and more resource efficient than GroupBy for this use case.

        :param dict args: dict of arguments

        :return: topn query
        :rtype: Query
        """
        query_type = 'topN'
        valid_parts = [
            'datasource', 'granularity', 'filter', 'aggregations',
            'post_aggregations', 'intervals', 'dimension', 'threshold',
            'metric'
        ]
        self.validate_query(query_type, valid_parts, args)
        return self.build_query(query_type, args)

    def timeseries(self, args):
        """
        A timeseries query returns the values of the requested metrics
        (in aggregate) for each timestamp.

        :param dict args: dict of args

        :return: timeseries query
        :rtype: Query
        """
        query_type = 'timeseries'
        valid_parts = [
            'datasource', 'granularity', 'filter', 'aggregations', 'descending',
            'post_aggregations', 'intervals'
        ]
        self.validate_query(query_type, valid_parts, args)
        return self.build_query(query_type, args)

    def groupby(self, args):
        """
        A group-by query groups a results set (the requested aggregate
        metrics) by the specified dimension(s).

        :param dict args: dict of args

        :return: group by query
        :rtype: Query
        """
        query_type = 'groupBy'
        valid_parts = [
            'datasource', 'granularity', 'filter', 'aggregations',
            'having', 'post_aggregations', 'intervals', 'dimensions',
            'limit_spec',
        ]
        self.validate_query(query_type, valid_parts, args)
        return self.build_query(query_type, args)

    def segment_metadata(self, args):
        """
        * Column type
        * Estimated size in bytes
        * Estimated size in bytes of each column
        * Interval the segment covers
        * Segment ID

        :param dict args: dict of args

        :return: segment metadata query
        :rtype: Query
        """
        query_type = 'segmentMetadata'
        valid_parts = ['datasource', 'intervals', 'analysisTypes', 'merge']
        self.validate_query(query_type, valid_parts, args)
        return self.build_query(query_type, args)

    def time_boundary(self, args):
        """
        A time boundary query returns the min and max timestamps present in a data source.

        :param dict args: dict of args

        :return: time boundary query
        :rtype: Query
        """
        query_type = 'timeBoundary'
        valid_parts = ['datasource']
        self.validate_query(query_type, valid_parts, args)
        return self.build_query(query_type, args)

    def select(self, args):
        """
        A select query returns raw Druid rows and supports pagination.

        :param dict args: dict of args

        :return: select query
        :rtype: Query
        """
        query_type = 'select'
        valid_parts = [
            'datasource', 'granularity', 'filter', 'dimensions', 'metrics',
            'paging_spec', 'intervals'
        ]
        self.validate_query(query_type, valid_parts, args)
        return self.build_query(query_type, args)

    def search(self, args):
        """
        A search query returns dimension values that match the search specification.

        :param dict args: dict of args

        :return: search query
        :rtype: Query
        """
        query_type = 'search'
        valid_parts = [
            'datasource', 'granularity', 'filter', 'searchDimensions', 'query',
            'limit', 'intervals', 'sort'
        ]
        self.validate_query(query_type, valid_parts, args)
        return self.build_query(query_type, args)

    def scan(self, args):
        """
        A scan query returns raw Druid rows

        :param dict args: dict of args

        :return: select query
        :rtype: Query
        """
        query_type = 'scan'
        valid_parts = [
            'datasource', 'granularity', 'filter', 'dimensions', 'metrics',
            'intervals', 'limit',
        ]
        self.validate_query(query_type, valid_parts, args)
        return self.build_query(query_type, args)
