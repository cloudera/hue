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
from six import iteritems

from .filters import Filter


def thetasketch(raw_column, isinputthetasketch=False, size=16384):
    return {
        "type": "thetaSketch",
        "fieldName": raw_column,
        "isInputThetaSketch": isinputthetasketch,
        "size": size,
    }


def min(raw_metric):
    """
    .. note:: Deprecated use `longMin`, `doubleMin' instead
    """
    return {"type": "min", "fieldName": raw_metric}


def max(raw_metric):
    """
    .. note:: Deprecated use `longMax`, `doubleMax' instead
    """
    return {"type": "max", "fieldName": raw_metric}


def longsum(raw_metric):
    return {"type": "longSum", "fieldName": raw_metric}


def longmin(raw_metric):
    return {"type": "longMin", "fieldName": raw_metric}


def longmax(raw_metric):
    return {"type": "longMax", "fieldName": raw_metric}


def doublesum(raw_metric):
    return {"type": "doubleSum", "fieldName": raw_metric}


def doublemin(raw_metric):
    return {"type": "doubleMin", "fieldName": raw_metric}


def doublemax(raw_metric):
    return {"type": "doubleMax", "fieldName": raw_metric}


def count(raw_metric):
    return {"type": "count", "fieldName": raw_metric}


def hyperunique(raw_metric):
    return {"type": "hyperUnique", "fieldName": raw_metric}


def cardinality(raw_column, by_row=False):
    if type(raw_column) is not list:
        raw_column = [raw_column]
    return {"type": "cardinality", "fieldNames": raw_column, "byRow": by_row}


def filtered(filter, agg):
    return {"type": "filtered",
            "filter": Filter.build_filter(filter),
            "aggregator": agg}


def javascript(columns_list, fn_aggregate, fn_combine, fn_reset):
    return {
        "type": "javascript",
        "fieldNames": columns_list,
        "fnAggregate": fn_aggregate,
        "fnCombine": fn_combine,
        "fnReset": fn_reset,
    }


def build_aggregators(agg_input):
    return [_build_aggregator(name, kwargs)
            for (name, kwargs) in iteritems(agg_input)]


def _build_aggregator(name, kwargs):
    if kwargs["type"] == "filtered":
        kwargs["aggregator"] = _build_aggregator(name, kwargs["aggregator"])
    else:
        kwargs.update({"name": name})

    return kwargs
