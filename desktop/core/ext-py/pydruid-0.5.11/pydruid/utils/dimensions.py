def build_dimension(dim):
    if isinstance(dim, DimensionSpec):
        dim = dim.build()

    return dim


class DimensionSpec(object):
    def __init__(
        self, dimension, output_name, extraction_function=None, filter_spec=None
    ):
        self._dimension = dimension
        self._output_name = output_name
        self._extraction_function = extraction_function
        self._filter_spec = filter_spec

    def build(self):
        dimension_spec = {
            "type": "default",
            "dimension": self._dimension,
            "outputName": self._output_name,
        }

        if self._extraction_function is not None:
            dimension_spec["type"] = "extraction"
            dimension_spec["extractionFn"] = self._extraction_function.build()

        if self._filter_spec is not None:
            dimension_spec = self._filter_spec.build(dimension_spec)

        return dimension_spec


class FilteredSpec(object):

    filter_type = None

    def build(self, delegate):
        dimension_spec = {"type": self.filter_type, "delegate": delegate}
        return dimension_spec


class ListFilteredSpec(FilteredSpec):

    filter_type = "listFiltered"

    def __init__(self, values, is_whitelist=True):
        self._values = values
        self._is_whitelist = is_whitelist

    def build(self, dimension_spec):
        filtered_dimension_spec = super(ListFilteredSpec, self).build(dimension_spec)
        filtered_dimension_spec["values"] = self._values

        if not self._is_whitelist:
            filtered_dimension_spec["isWhitelist"] = False

        return filtered_dimension_spec


class RegexFilteredSpec(FilteredSpec):

    filter_type = "regexFiltered"

    def __init__(self, pattern):
        self._pattern = pattern

    def build(self, dimension_spec):
        filtered_dimension_spec = super(RegexFilteredSpec, self).build(dimension_spec)
        filtered_dimension_spec["pattern"] = self._pattern

        return filtered_dimension_spec


class ExtractionFunction(object):

    extraction_type = None

    def build(self):
        return {"type": self.extraction_type}


class BaseRegexExtraction(ExtractionFunction):
    def __init__(self, expr):
        super(BaseRegexExtraction, self).__init__()
        self._expr = expr

    def build(self):
        extractor = super(BaseRegexExtraction, self).build()
        extractor["expr"] = self._expr

        return extractor


class RegexExtraction(BaseRegexExtraction):

    extraction_type = "regex"


class PartialExtraction(BaseRegexExtraction):

    extraction_type = "partial"


class JavascriptExtraction(ExtractionFunction):

    extraction_type = "javascript"

    def __init__(self, func, injective=False):
        super(JavascriptExtraction, self).__init__()
        self._func = func
        self._injective = injective

    def build(self):
        extractor = super(JavascriptExtraction, self).build()
        extractor["function"] = self._func
        extractor["injective"] = self._injective

        return extractor


class TimeFormatExtraction(ExtractionFunction):

    extraction_type = "timeFormat"

    def __init__(self, format, locale=None, time_zone=None):
        super(TimeFormatExtraction, self).__init__()
        self._format = format
        self._locale = locale
        self._time_zone = time_zone

    def build(self):
        extractor = super(TimeFormatExtraction, self).build()
        extractor["format"] = self._format
        if self._locale:
            extractor["locale"] = self._locale
        if self._time_zone:
            extractor["timeZone"] = self._time_zone

        return extractor


class LookupExtraction(ExtractionFunction):

    extraction_type = "lookup"
    lookup_type = None

    def __init__(
        self, retain_missing_values=False, replace_missing_values=None, injective=False
    ):
        super(LookupExtraction, self).__init__()
        self._retain_missing_values = retain_missing_values
        self._replace_missing_values = replace_missing_values
        self._injective = injective

    def build(self):
        extractor = super(LookupExtraction, self).build()
        extractor["lookup"] = self.build_lookup()
        extractor["retainMissingValue"] = self._retain_missing_values
        extractor["replaceMissingValueWith"] = self._replace_missing_values
        extractor["injective"] = self._injective

        return extractor

    def build_lookup(self):
        return {"type": self.lookup_type}


class MapLookupExtraction(LookupExtraction):

    lookup_type = "map"

    def __init__(self, mapping, **kwargs):
        super(MapLookupExtraction, self).__init__(**kwargs)
        self._mapping = mapping

    def build_lookup(self):
        lookup = super(MapLookupExtraction, self).build_lookup()
        lookup["map"] = self._mapping

        return lookup


class NamespaceLookupExtraction(LookupExtraction):

    lookup_type = "namespace"

    def __init__(self, namespace, **kwargs):
        super(NamespaceLookupExtraction, self).__init__(**kwargs)
        self._namespace = namespace

    def build_lookup(self):
        lookup = super(NamespaceLookupExtraction, self).build_lookup()
        lookup["namespace"] = self._namespace

        return lookup


class RegisteredLookupExtraction(LookupExtraction):

    extraction_type = "registeredLookup"

    def __init__(self, reglookup, **kwargs):
        super(RegisteredLookupExtraction, self).__init__(**kwargs)
        self._lookup = reglookup

    def build_lookup(self):
        return self._lookup
