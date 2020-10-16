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
try:
    import simplejson as json
except ImportError:
    import json


class Having:
    def __init__(self, **args):

        if args['type'] in ('equalTo', 'lessThan', 'greaterThan'):
            self.having = {'having': {'type': args['type'],
                                      'aggregation': args['aggregation'],
                                      'value': args['value']}}

        elif args['type'] == 'and':
            self.having = {'having': {'type': 'and',
                                      'havingSpecs': args['havingSpecs']}}

        elif args['type'] == 'or':
            self.having = {'having': {'type': 'or',
                                      'havingSpecs': args['havingSpecs']}}

        elif args['type'] == 'not':
            self.having = {'having': {'type': 'not',
                                      'havingSpec': args['havingSpec']}}
        else:
            raise NotImplemented(
                'Having type: {0} does not exist'.format(args['type']))

    def show(self):
        print(json.dumps(self.having, indent=4))

    def _combine(self, typ, x):
        # collapse nested and/ors
        if self.having['having']['type'] == typ:
            havingSpecs = self.having['having']['havingSpecs'] + [x.having['having']]
            return Having(type=typ, havingSpecs=havingSpecs)
        elif x.having['having']['type'] == typ:
            havingSpecs = [self.having['having']] + x.having['having']['havingSpecs']
            return Having(type=typ, havingSpecs=havingSpecs)
        else:
            return Having(type=typ,
                          havingSpecs=[self.having['having'], x.having['having']])

    def __and__(self, x):
        return self._combine('and', x)

    def __or__(self, x):
        return self._combine('or', x)

    def __invert__(self):
        return Having(type='not', havingSpec=self.having['having'])

    @staticmethod
    def build_having(having_obj):
        return having_obj.having['having']


class Aggregation:
    def __init__(self, agg):
        self.aggregation = agg

    def __eq__(self, other):
        return Having(type='equalTo', aggregation=self.aggregation, value=other)

    def __lt__(self, other):
        return Having(type='lessThan', aggregation=self.aggregation, value=other)

    def __gt__(self, other):
        return Having(type='greaterThan', aggregation=self.aggregation, value=other)
