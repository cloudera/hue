from __future__ import unicode_literals

import os
import re
import sys

from prompt_toolkit import prompt, AbortAction
from prompt_toolkit.history import FileHistory
from prompt_toolkit.contrib.completers import WordCompleter
from pygments.lexers import SqlLexer
from pygments.style import Style
from pygments.token import Token
from pygments.styles.default import DefaultStyle
from six.moves.urllib import parse
from tabulate import tabulate

from pydruid.db.api import connect


keywords = [
    'EXPLAIN PLAN FOR',
    'WITH',
    'SELECT',
    'ALL',
    'DISTINCT',
    'FROM',
    'WHERE',
    'GROUP BY',
    'HAVING',
    'ORDER BY',
    'ASC',
    'DESC',
    'LIMIT',
]

aggregate_functions = [
    'COUNT',
    'SUM',
    'MIN',
    'MAX',
    'AVG',
    'APPROX_COUNT_DISTINCT',
    'APPROX_QUANTILE',
]

numeric_functions = [
    'ABS',
    'CEIL',
    'EXP',
    'FLOOR',
    'LN',
    'LOG10',
    'POW',
    'SQRT',
]

string_functions = [
    'CHARACTER_LENGTH',
    'LOOKUP',
    'LOWER',
    'REGEXP_EXTRACT',
    'REPLACE',
    'SUBSTRING',
    'TRIM',
    'BTRIM',
    'RTRIM',
    'LTRIM',
    'UPPER',
]

time_functions = [
    'CURRENT_TIMESTAMP',
    'CURRENT_DATE',
    'TIME_FLOOR',
    'TIME_SHIFT',
    'TIME_EXTRACT',
    'TIME_PARSE',
    'TIME_FORMAT',
    'MILLIS_TO_TIMESTAMP',
    'TIMESTAMP_TO_MILLIS',
    'EXTRACT',
    'FLOOR',
    'CEIL',
]

other_functions = [
    'CAST',
    'CASE',
    'WHEN',
    'THEN',
    'END',
    'NULLIF',
    'COALESCE',
]


replacements = {
    '^SHOW SCHEMAS': 'SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA',
    '^SHOW TABLES': 'SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES',
    '^DESC (?P<table>[^;\s]*)': r"""
        SELECT COLUMN_NAME,
               ORDINAL_POSITION,
               COLUMN_DEFAULT,
               IS_NULLABLE,
               DATA_TYPE
          FROM INFORMATION_SCHEMA.COLUMNS
         WHERE TABLE_NAME='\1'
    """.strip(),
}


class DocumentStyle(Style):
    styles = {
        Token.Menu.Completions.Completion.Current: 'bg:#00aaaa #000000',
        Token.Menu.Completions.Completion: 'bg:#008888 #ffffff',
        Token.Menu.Completions.ProgressButton: 'bg:#003333',
        Token.Menu.Completions.ProgressBar: 'bg:#00aaaa',
    }
    styles.update(DefaultStyle.styles)


def get_connection_kwargs(url):
    parts = parse.urlparse(url)
    if ':' in parts.netloc:
        host, port = parts.netloc.split(':', 1)
        port = int(port)
    else:
        host = parts.netloc
        port = 8082

    return {
        'host': host,
        'port': port,
        'path': parts.path,
        'scheme': parts.scheme,
    }


def get_tables(connection):
    cursor = connection.cursor()
    return [
        row.TABLE_NAME for row in
        cursor.execute('SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES')
    ]


def get_autocomplete(connection):
    return (
        keywords +
        aggregate_functions +
        numeric_functions +
        string_functions +
        time_functions +
        other_functions +
        get_tables(connection)
    )


def main():
    history = FileHistory(os.path.expanduser('~/.pydruid_history'))

    try:
        url = sys.argv[1]
    except IndexError:
        url = 'http://localhost:8082/druid/v2/sql/'
    kwargs = get_connection_kwargs(url)
    connection = connect(**kwargs)
    cursor = connection.cursor()

    words = get_autocomplete(connection)
    sql_completer = WordCompleter(words, ignore_case=True)

    while True:
        try:
            query = prompt(
                '> ', lexer=SqlLexer, completer=sql_completer,
                style=DocumentStyle, history=history,
                on_abort=AbortAction.RETRY)
        except EOFError:
            break  # Control-D pressed.

        # run query
        query = query.strip('; ')
        if query:
            # shortcuts
            for pattern, repl in replacements.items():
                query = re.sub(pattern, repl, query)

            try:
                result = cursor.execute(query)
            except Exception as e:
                print(e)
                continue

            headers = [t[0] for t in cursor.description or []]
            print(tabulate(result, headers=headers))

    print('GoodBye!')


if __name__ == '__main__':
    main()
