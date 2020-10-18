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

from .dimensions import build_dimension


class Filter:

    # filter types supporting extraction function
    _FILTERS_WITH_EXTR_FN = (
        "selector",
        "regex",
        "javascript",
        "in",
        "bound",
        "interval",
        "extraction",
    )

    def __init__(self, extraction_function=None, ordering="lexicographic", **args):

        type_ = args.get("type", "selector")

        if extraction_function is not None:
            if type_ not in self._FILTERS_WITH_EXTR_FN:
                raise ValueError(
                    "Filter of type {0} doesn't support "
                    "extraction function".format(type_)
                )
        elif type_ == "extraction":
            raise ValueError(
                "Filter of type extraction requires extraction " "function"
            )

        self.extraction_function = extraction_function

        self.filter = {"filter": {"type": type_}}

        if type_ == "selector":
            self.filter["filter"].update(
                {"dimension": args["dimension"], "value": args["value"]}
            )
        elif type_ == "javascript":
            self.filter["filter"].update(
                {"dimension": args["dimension"], "function": args["function"]}
            )
        elif type_ == "and":
            self.filter["filter"].update({"fields": args["fields"]})
        elif type_ == "or":
            self.filter["filter"].update({"fields": args["fields"]})
        elif type_ == "not":
            self.filter["filter"].update({"field": args["field"]})
        elif type_ == "in":
            self.filter["filter"].update(
                {"dimension": args["dimension"], "values": args["values"]}
            )
        elif type_ == "regex":
            self.filter["filter"].update(
                {"dimension": args["dimension"], "pattern": args["pattern"]}
            )
        elif type_ == "bound":
            self.filter["filter"].update(
                {
                    "dimension": args["dimension"],
                    "lower": args["lower"],
                    "lowerStrict": args["lowerStrict"],
                    "upper": args["upper"],
                    "upperStrict": args["upperStrict"],
                    "alphaNumeric": args["alphaNumeric"],
                    "ordering": ordering,
                }
            )
        elif type_ == "columnComparison":
            self.filter["filter"].update({"dimensions": args["dimensions"]})
        elif type_ == "interval":
            self.filter["filter"].update(
                {"dimension": args["dimension"], "intervals": args["intervals"]}
            )
        elif type_ == "extraction":
            self.filter["filter"].update(
                {"dimension": args["dimension"], "value": args["value"]}
            )
        elif type_ == "search":
            self.filter["filter"].update(
                {
                    "dimension": args["dimension"],
                    "query": {
                        "type": "contains",
                        "value": args["value"],
                        "caseSensitive": args.get("caseSensitive", "false"),
                    },
                }
            )
        elif type_ == "like":
            self.filter["filter"].update(
                {"dimension": args["dimension"], "pattern": args["pattern"]}
            )
        elif type_ == "spatial":
            self.filter["filter"].update(
                {"dimension": args["dimension"], "bound": args["bound"]}
            )
        else:
            raise NotImplementedError("Filter type: {0} does not exist".format(type_))

    def show(self):
        print(json.dumps(self.filter, indent=4))

    def __and__(self, x):
        if self.filter["filter"]["type"] == "and":
            # if `self` is already `and`, don't create a new filter
            # but just append `x` to the filter fields.
            self.filter["filter"]["fields"].append(x)
            return self
        return Filter(type="and", fields=[self, x])

    def __or__(self, x):
        if self.filter["filter"]["type"] == "or":
            # if `self` is already `or`, don't create a new filter
            # but just append `x` to the filter fields.
            self.filter["filter"]["fields"].append(x)
            return self
        return Filter(type="or", fields=[self, x])

    def __invert__(self):
        return Filter(type="not", field=self)

    @staticmethod
    def build_filter(filter_obj):
        filter = filter_obj.filter["filter"]
        if filter["type"] in ["and", "or"]:
            filter = filter.copy()  # make a copy so we don't overwrite `fields`
            filter["fields"] = [Filter.build_filter(f) for f in filter["fields"]]
        elif filter["type"] in ["not"]:
            filter = filter.copy()
            filter["field"] = Filter.build_filter(filter["field"])
        elif filter["type"] in ["columnComparison"]:
            filter = filter.copy()
            filter["dimensions"] = [build_dimension(d) for d in filter["dimensions"]]

        if filter_obj.extraction_function is not None:
            if filter is filter_obj.filter["filter"]:  # copy if not yet copied
                filter = filter.copy()
            filter["extractionFn"] = filter_obj.extraction_function.build()

        return filter


class Dimension:
    def __init__(self, dim):
        self.dimension = dim

    def __eq__(self, other):
        return Filter(dimension=self.dimension, value=other)

    def __ne__(self, other):
        return ~Filter(dimension=self.dimension, value=other)


class JavaScript:
    def __init__(self, dim):
        self.dimension = dim

    def __eq__(self, func):
        return Filter(type="javascript", dimension=self.dimension, function=func)


class Bound(Filter):
    """
    Bound filter can be used to filter by comparing dimension values to an
    upper value or/and a lower value.

    :ivar str dimension: Dimension to filter on.
    :ivar str lower: Lower bound.
    :ivar str upper: Upper bound.
    :ivar bool lowerStrict: Strict lower inclusion. Initial value: False
    :ivar bool upperStrict: Strict upper inclusion. Initial value: False
    :ivar bool alphaNumeric: Numeric comparison. Initial value: False
        NOTE: For backwards compatibility - Use "ordering" instead.
    :ivar str ordering: Sorting Order. Initial value: lexicographic
        Specifies the sorting order to use when comparing values against the bound.
        Can be one of the following values: "lexicographic", "alphanumeric", "numeric",
        "strlen", "version". See Sorting Orders
        https://druid.apache.org/docs/latest/querying/filters.html#bound-filter
        for more details.
    :ivar ExtractionFunction extraction_function: extraction function to use,
                                                  if not None
    """

    def __init__(
        self,
        dimension,
        lower=None,
        upper=None,
        lowerStrict=False,
        upperStrict=False,
        alphaNumeric=False,
        ordering="lexicographic",
        extraction_function=None,
    ):
        if not lower and not upper:
            raise ValueError("Must include either lower or upper or both")
        Filter.__init__(
            self,
            type="bound",
            dimension=dimension,
            lower=lower,
            upper=upper,
            lowerStrict=lowerStrict,
            upperStrict=upperStrict,
            alphaNumeric=alphaNumeric,
            ordering=ordering,
            extraction_function=extraction_function,
        )


class Interval(Filter):
    """
    Interval filter can be used to filter by comparing dimension(__time)
    values to a list of intervals.

    :ivar str dimension: Dimension to filter on.
    :ivar list intervals: List of ISO-8601 intervals of data to filter out.
    :ivar ExtractionFunction extraction_function: extraction function to use,
                                                  if not None
    """

    def __init__(self, dimension, intervals, extraction_function=None):

        Filter.__init__(
            self,
            type="interval",
            dimension=dimension,
            intervals=intervals,
            extraction_function=extraction_function,
        )


class Spatial(Filter):
    """
    Spatial filter can be used to filter by spatial bounds

    :ivar str dimension: Dimension to filter on.
    :ivar str bound_type: Spatial bound type: ['rectangle','radius','polygon'].
    :param `**kwargs`: addition arguments required for the selected bound type:
        'rectange': 'minCoords' and 'maxCoords'
        'radius': 'coords' and 'radius'
        'polygon': 'abscissa' and 'ordinate'
    """

    def __init__(self, dimension, bound_type, **args):

        _bound = {"type": bound_type}

        if bound_type == "rectangle":
            if not args["minCoords"] or not args["maxCoords"]:
                raise ValueError(
                    "Rectangle bound must include both minCoords and maxCoords"
                )
            _bound["minCoords"] = args["minCoords"]
            _bound["maxCoords"] = args["maxCoords"]
        elif bound_type == "radius":
            if not args["coords"] or not args["radius"]:
                raise ValueError("Radius bound must include both coords and radius")
            _bound["coords"] = args["coords"]
            _bound["radius"] = args["radius"]
        elif bound_type == "polygon":
            if not args["abscissa"] or not args["ordinate"]:
                raise ValueError(
                    "Polygon bound must include both abscissa and ordinate"
                )
            _bound["abscissa"] = args["abscissa"]
            _bound["ordinate"] = args["ordinate"]
        else:
            raise ValueError("Unsupport Spatial Bound type: {0}".format(bound_type))

        Filter.__init__(self, type="spatial", dimension=dimension, bound=_bound)
