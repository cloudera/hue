from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple, OrderedDict
import itertools
import json
from six import string_types
from six.moves.urllib import parse

import requests

from pydruid.db import exceptions


class Type(object):
    STRING = 1
    NUMBER = 2
    BOOLEAN = 3


def connect(
    host="localhost",
    port=8082,
    path="/druid/v2/sql/",
    scheme="http",
    user=None,
    password=None,
    context=None,
    header=False,
    ssl_verify_cert=True,
    ssl_client_cert=None,
    proxies=None,
):  # noqa: E125
    """
    Constructor for creating a connection to the database.

        >>> conn = connect('localhost', 8082)
        >>> curs = conn.cursor()

    """
    context = context or {}

    return Connection(
        host,
        port,
        path,
        scheme,
        user,
        password,
        context,
        header,
        ssl_verify_cert,
        ssl_client_cert,
        proxies,
    )


def check_closed(f):
    """Decorator that checks if connection/cursor is closed."""

    def g(self, *args, **kwargs):
        if self.closed:
            raise exceptions.Error(
                "{klass} already closed".format(klass=self.__class__.__name__)
            )
        return f(self, *args, **kwargs)

    return g


def check_result(f):
    """Decorator that checks if the cursor has results from `execute`."""

    def g(self, *args, **kwargs):
        if self._results is None:
            raise exceptions.Error("Called before `execute`")
        return f(self, *args, **kwargs)

    return g


def get_description_from_row(row):
    """
    Return description from a single row.

    We only return the name, type (inferred from the data) and if the values
    can be NULL. String columns in Druid are NULLable. Numeric columns are NOT
    NULL.
    """
    return [
        (
            name,  # name
            get_type(value),  # type_code
            None,  # [display_size]
            None,  # [internal_size]
            None,  # [precision]
            None,  # [scale]
            get_type(value) == Type.STRING,  # [null_ok]
        )
        for name, value in row.items()
    ]


def get_type(value):
    """
    Infer type from value.

    Note that bool is a subclass of int so order of statements matter.
    """

    if isinstance(value, string_types) or value is None:
        return Type.STRING
    elif isinstance(value, bool):
        return Type.BOOLEAN
    elif isinstance(value, (int, float)):
        return Type.NUMBER

    raise exceptions.Error("Value of unknown type: {value}".format(value=value))


class Connection(object):
    """Connection to a Druid database."""

    def __init__(
        self,
        host="localhost",
        port=8082,
        path="/druid/v2/sql/",
        scheme="http",
        user=None,
        password=None,
        context=None,
        header=False,
        ssl_verify_cert=True,
        ssl_client_cert=None,
        proxies=None,
    ):
        netloc = "{host}:{port}".format(host=host, port=port)
        self.url = parse.urlunparse((scheme, netloc, path, None, None, None))
        self.context = context or {}
        self.closed = False
        self.cursors = []
        self.header = header
        self.user = user
        self.password = password
        self.ssl_verify_cert = ssl_verify_cert
        self.ssl_client_cert = ssl_client_cert
        self.proxies = proxies

    @check_closed
    def close(self):
        """Close the connection now."""
        self.closed = True
        for cursor in self.cursors:
            try:
                cursor.close()
            except exceptions.Error:
                pass  # already closed

    @check_closed
    def commit(self):
        """
        Commit any pending transaction to the database.

        Not supported.
        """
        pass

    @check_closed
    def cursor(self):
        """Return a new Cursor Object using the connection."""

        cursor = Cursor(
            self.url,
            self.user,
            self.password,
            self.context,
            self.header,
            self.ssl_verify_cert,
            self.ssl_client_cert,
            self.proxies,
        )

        self.cursors.append(cursor)

        return cursor

    @check_closed
    def execute(self, operation, parameters=None):
        cursor = self.cursor()
        return cursor.execute(operation, parameters)

    def __enter__(self):
        return self.cursor()

    def __exit__(self, *exc):
        self.close()


class Cursor(object):
    """Connection cursor."""

    def __init__(
        self,
        url,
        user=None,
        password=None,
        context=None,
        header=False,
        ssl_verify_cert=True,
        proxies=None,
        ssl_client_cert=None,
    ):
        self.url = url
        self.context = context or {}
        self.header = header
        self.user = user
        self.password = password
        self.ssl_verify_cert = ssl_verify_cert
        self.ssl_client_cert = ssl_client_cert
        self.proxies = proxies

        # This read/write attribute specifies the number of rows to fetch at a
        # time with .fetchmany(). It defaults to 1 meaning to fetch a single
        # row at a time.
        self.arraysize = 1

        self.closed = False

        # this is updated only after a query
        self.description = None

        # this is set to an iterator after a successfull query
        self._results = None

    @property
    @check_result
    @check_closed
    def rowcount(self):
        # consume the iterator
        results = list(self._results)
        n = len(results)
        self._results = iter(results)
        return n

    @check_closed
    def close(self):
        """Close the cursor."""
        self.closed = True

    @check_closed
    def execute(self, operation, parameters=None):
        query = apply_parameters(operation, parameters)
        results = self._stream_query(query)

        # `_stream_query` returns a generator that produces the rows; we need to
        # consume the first row so that `description` is properly set, so let's
        # consume it and insert it back if it is not the header.
        try:
            first_row = next(results)
            self._results = (
                results if self.header else itertools.chain([first_row], results)
            )
        except StopIteration:
            self._results = iter([])

        return self

    @check_closed
    def executemany(self, operation, seq_of_parameters=None):
        raise exceptions.NotSupportedError(
            "`executemany` is not supported, use `execute` instead"
        )

    @check_result
    @check_closed
    def fetchone(self):
        """
        Fetch the next row of a query result set, returning a single sequence,
        or `None` when no more data is available.
        """
        try:
            return self.next()
        except StopIteration:
            return None

    @check_result
    @check_closed
    def fetchmany(self, size=None):
        """
        Fetch the next set of rows of a query result, returning a sequence of
        sequences (e.g. a list of tuples). An empty sequence is returned when
        no more rows are available.
        """
        size = size or self.arraysize
        return list(itertools.islice(self._results, size))

    @check_result
    @check_closed
    def fetchall(self):
        """
        Fetch all (remaining) rows of a query result, returning them as a
        sequence of sequences (e.g. a list of tuples). Note that the cursor's
        arraysize attribute can affect the performance of this operation.
        """
        return list(self._results)

    @check_closed
    def setinputsizes(self, sizes):
        # not supported
        pass

    @check_closed
    def setoutputsizes(self, sizes):
        # not supported
        pass

    @check_closed
    def __iter__(self):
        return self

    @check_closed
    def __next__(self):
        return next(self._results)

    next = __next__

    def _stream_query(self, query):
        """
        Stream rows from a query.

        This method will yield rows as the data is returned in chunks from the
        server.
        """
        self.description = None

        headers = {"Content-Type": "application/json"}

        payload = {"query": query, "context": self.context, "header": self.header}

        auth = (
            requests.auth.HTTPBasicAuth(self.user, self.password) if self.user else None
        )
        r = requests.post(
            self.url,
            stream=True,
            headers=headers,
            json=payload,
            auth=auth,
            verify=self.ssl_verify_cert,
            cert=self.ssl_client_cert,
            proxies=self.proxies,
        )
        if r.encoding is None:
            r.encoding = "utf-8"
        # raise any error messages
        if r.status_code != 200:
            try:
                payload = r.json()
            except Exception:
                payload = {
                    "error": "Unknown error",
                    "errorClass": "Unknown",
                    "errorMessage": r.text,
                }
            msg = "{error} ({errorClass}): {errorMessage}".format(**payload)
            raise exceptions.ProgrammingError(msg)

        # Druid will stream the data in chunks of 8k bytes, splitting the JSON
        # between them; setting `chunk_size` to `None` makes it use the server
        # size
        chunks = r.iter_content(chunk_size=None, decode_unicode=True)
        Row = None
        for row in rows_from_chunks(chunks):
            # update description
            if self.description is None:
                self.description = (
                    list(row.items()) if self.header else get_description_from_row(row)
                )

            # return row in namedtuple
            if Row is None:
                Row = namedtuple("Row", row.keys(), rename=True)
            yield Row(*row.values())


def rows_from_chunks(chunks):
    """
    A generator that yields rows from JSON chunks.

    Druid will return the data in chunks, but they are not aligned with the
    JSON objects. This function will parse all complete rows inside each chunk,
    yielding them as soon as possible.
    """
    body = ""
    for chunk in chunks:
        if chunk:
            body = "".join((body, chunk))

        # find last complete row
        boundary = 0
        brackets = 0
        in_string = False
        for i, char in enumerate(body):
            if char == '"':
                if not in_string:
                    in_string = True
                elif body[i - 1] != "\\":
                    in_string = False

            if in_string:
                continue

            if char == "{":
                brackets += 1
            elif char == "}":
                brackets -= 1
                if brackets == 0 and i > boundary:
                    boundary = i + 1

        rows = body[:boundary].lstrip("[,")
        body = body[boundary:]

        for row in json.loads(
            "[{rows}]".format(rows=rows), object_pairs_hook=OrderedDict
        ):
            yield row


def apply_parameters(operation, parameters):
    if not parameters:
        return operation

    escaped_parameters = {key: escape(value) for key, value in parameters.items()}
    return operation % escaped_parameters


def escape(value):
    """
    Escape the parameter value.

    Note that bool is a subclass of int so order of statements matter.
    """

    if value == "*":
        return value
    elif isinstance(value, string_types):
        return "'{}'".format(value.replace("'", "''"))
    elif isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    elif isinstance(value, (int, float)):
        return value
    elif isinstance(value, (list, tuple)):
        return ", ".join(escape(element) for element in value)
