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

import six


class Postaggregator:
    def __init__(self, fn, fields, name):
        self.post_aggregator = {'type': 'arithmetic',
                                'name': name,
                                'fn': fn,
                                'fields': fields}
        self.name = name

    def __mul__(self, other):
        return Postaggregator('*', self.fields(other),
                              self.name + 'mul' + other.name)

    def __sub__(self, other):
        return Postaggregator('-', self.fields(other),
                              self.name + 'sub' + other.name)

    def __add__(self, other):
        return Postaggregator('+', self.fields(other),
                              self.name + 'add' + other.name)

    def __div__(self, other):
        return Postaggregator('/', self.fields(other),
                              self.name + 'div' + other.name)

    def __truediv__(self, other):
        return self.__div__(other)

    def fields(self, other):
        return [self.post_aggregator, other.post_aggregator]

    @staticmethod
    def build_post_aggregators(postaggs):
        def rename_postagg(new_name, post_aggregator):
            post_aggregator['name'] = new_name
            return post_aggregator

        return [rename_postagg(new_name, postagg.post_aggregator)
                for (new_name, postagg) in six.iteritems(postaggs)]


class Quantile(Postaggregator):
    def __init__(self, name, probability):
        Postaggregator.__init__(self, None, None, name)
        self.post_aggregator = {
            'type': 'quantile', 'fieldName': name, 'probability': probability}


class Quantiles(Postaggregator):
    def __init__(self, name, probabilities):
        Postaggregator.__init__(self, None, None, name)
        self.post_aggregator = {
            'type': 'quantiles', 'fieldName': name,
            'probabilities': probabilities}


class Field(Postaggregator):
    def __init__(self, name):
        Postaggregator.__init__(self, None, None, name)
        self.post_aggregator = {
            'type': 'fieldAccess', 'fieldName': name}


class Const(Postaggregator):
    def __init__(self, value, output_name=None):

        if output_name is None:
            name = 'const'
        else:
            name = output_name

        Postaggregator.__init__(self, None, None, name)
        self.post_aggregator = {
            'type': 'constant', 'name': name, 'value': value}


class HyperUniqueCardinality(Postaggregator):
    def __init__(self, name):
        Postaggregator.__init__(self, None, None, name)
        self.post_aggregator = {
            'type': 'hyperUniqueCardinality', 'fieldName': name}


class DoubleGreatest(Postaggregator):
    def __init__(self, fields, output_name=None):

        if output_name is None:
            name = 'doubleGreatest'
        else:
            name = output_name

        Postaggregator.__init__(self, None, None, name)
        self.post_aggregator = {
                'type': 'doubleGreatest',
                'name': name,
                'fields': [f.post_aggregator for f in fields]}


class DoubleLeast(Postaggregator):
    def __init__(self, fields, output_name=None):

        if output_name is None:
            name = 'doubleLeast'
        else:
            name = output_name

        Postaggregator.__init__(self, None, None, name)
        self.post_aggregator = {
                'type': 'doubleLeast',
                'name': name,
                'fields': [f.post_aggregator for f in fields]}


class LongGreatest(Postaggregator):
    def __init__(self, fields, output_name=None):

        if output_name is None:
            name = 'longGreatest'
        else:
            name = output_name

        Postaggregator.__init__(self, None, None, name)
        self.post_aggregator = {
                'type': 'longGreatest',
                'name': name,
                'fields': [f.post_aggregator for f in fields]}


class LongLeast(Postaggregator):
    def __init__(self, fields, output_name=None):

        if output_name is None:
            name = 'longLeast'
        else:
            name = output_name

        Postaggregator.__init__(self, None, None, name)
        self.post_aggregator = {
                'type': 'longLeast',
                'name': name,
                'fields': [f.post_aggregator for f in fields]}


class ThetaSketchOp(object):
    def __init__(self, fn, fields, name):
        self.post_aggregator = {'type': 'thetaSketchSetOp',
                                'name': name,
                                'func': fn,
                                'fields': fields}
        self.name = name

    def __or__(self, other):
        return ThetaSketchOp('UNION', self.fields(other),
                             self.name + '_OR_' + other.name)

    def __and__(self, other):
        return ThetaSketchOp('INTERSECT', self.fields(other),
                             self.name + '_AND_' + other.name)

    def __ne__(self, other):
        return ThetaSketchOp('NOT', self.fields(other),
                             self.name + '_NOT_' + other.name)

    def fields(self, other):
        return [self.post_aggregator, other.post_aggregator]

    @staticmethod
    def build_post_aggregators(thetasketchops):
        def rename_thetasketchop(new_name, thetasketchop):
            thetasketchop['name'] = new_name
            return thetasketchop

        return [rename_thetasketchop(new_name, thetasketchop.post_aggregator)
                for (new_name, thetasketchop) in six.iteritems(thetasketchops)]


class ThetaSketch(ThetaSketchOp):
    def __init__(self, name):
        ThetaSketchOp.__init__(self, None, None, name)
        self.post_aggregator = {
            'type': 'fieldAccess', 'fieldName': name}


class ThetaSketchEstimate(Postaggregator):
    def __init__(self, fields):
        field = fields.post_aggregator \
            if type(fields) in [ThetaSketch, ThetaSketchOp] else fields
        self.post_aggregator = {
            'type': 'thetaSketchEstimate',
            'name': 'thetasketchestimate',
            'field': field,
        }
        self.name = 'thetasketchestimate'
