# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ast
import cStringIO
import datetime
import decimal
import json
import logging
import sys
import traceback

logging.basicConfig()
LOG = logging.getLogger('fake_shell')

global_dict = {}


def execute_reply(status, content):
    return {
        'msg_type': 'execute_reply',
        'content': dict(
            content,
            status=status,
        )
    }


def execute_reply_ok(data):
    return execute_reply('ok', {
        'data': data,
    })


def execute_reply_error(exc_type, exc_value, tb):
    LOG.error('execute_reply', exc_info=True)
    return execute_reply('error', {
        'ename': unicode(exc_type.__name__),
        'evalue': unicode(exc_value),
        'traceback': traceback.format_exception(exc_type, exc_value, tb, -1),
    })


def execute_reply_internal_error(message, exc_info=None):
    LOG.error('execute_reply_internal_error', exc_info=exc_info)
    return execute_reply('error', {
        'ename': 'InternalError',
        'evalue': message,
        'traceback': [],
    })


class ExecutionError(Exception):
    def __init__(self, exc_info):
        self.exc_info = exc_info


class NormalNode(object):
    def __init__(self, code):
        self.code = compile(code, '<stdin>', 'exec', ast.PyCF_ONLY_AST, 1)

    def execute(self):
        to_run_exec, to_run_single = self.code.body[:-1], self.code.body[-1:]

        try:
            for node in to_run_exec:
                mod = ast.Module([node])
                code = compile(mod, '<stdin>', 'exec')
                exec code in global_dict

            for node in to_run_single:
                mod = ast.Interactive([node])
                code = compile(mod, '<stdin>', 'single')
                exec code in global_dict
        except:
            # We don't need to log the exception because we're just executing user
            # code and passing the error along.
            raise ExecutionError(sys.exc_info())


class UnknownMagic(Exception):
    pass


class MagicNode(object):
    def __init__(self, line):
        parts = line[1:].split(' ', 1)
        if len(parts) == 1:
            self.magic, self.rest = parts[0], ()
        else:
            self.magic, self.rest = parts[0], (parts[1],)

    def execute(self):
        if not self.magic:
            raise UnknownMagic('magic command not specified')

        try:
            handler = magic_router[self.magic]
        except KeyError:
            raise UnknownMagic("unknown magic command '%s'" % self.magic)

        return handler(*self.rest)


def parse_code_into_nodes(code):
    nodes = []
    try:
        nodes.append(NormalNode(code))
    except SyntaxError:
        # It's possible we hit a syntax error because of a magic command. Split the code groups
        # of 'normal code', and code that starts with a '%'. possibly magic code
        # lines, and see if any of the lines
        # Remove lines until we find a node that parses, then check if the next line is a magic
        # line
        # .

        # Split the code into chunks of normal code, and possibly magic code, which starts with
        # a '%'.
        normal = []
        chunks = []
        for i, line in enumerate(code.rstrip().split('\n')):
            if line.startswith('%'):
                if normal:
                    chunks.append(''.join(normal))
                    normal = []

                chunks.append(line)
            else:
                normal.append(line)

        if normal:
            chunks.append('\n'.join(normal))

        # Convert the chunks into AST nodes. Let exceptions propagate.
        for chunk in chunks:
            if chunk.startswith('%'):
                nodes.append(MagicNode(chunk))
            else:
                nodes.append(NormalNode(chunk))

    return nodes


def execute_request(content):
    try:
        code = content['code']
    except KeyError:
        return execute_reply_internal_error(
            'Malformed message: content object missing "code"', sys.exc_info()
        )

    try:
        nodes = parse_code_into_nodes(code)
    except SyntaxError:
        exc_type, exc_value, tb = sys.exc_info()
        return execute_reply_error(exc_type, exc_value, [])

    result = None

    try:
        for node in nodes:
            result = node.execute()
    except UnknownMagic:
        exc_type, exc_value, tb = sys.exc_info()
        return execute_reply_error(exc_type, exc_value, [])
    except ExecutionError, e:
        return execute_reply_error(*e.exc_info)

    if result is None:
        result = {}

    stdout = fake_stdout.getvalue()
    fake_stdout.truncate(0)

    stderr = fake_stderr.getvalue()
    fake_stderr.truncate(0)

    output = result.pop('text/plain', '')

    if stdout:
        output += stdout

    if stderr:
        output += stderr

    output = output.rstrip()

    # Only add the output if it exists, or if there are no other mimetypes in the result.
    if output or not result:
        result['text/plain'] = output.rstrip()

    return execute_reply_ok(result)


def magic_table_convert(value):
    try:
        converter = magic_table_types[type(value)]
    except KeyError:
        converter = magic_table_types[str]

    return converter(value)


def magic_table_convert_seq(items):
    last_item_type = None
    converted_items = []

    for item in items:
        item_type, item = magic_table_convert(item)

        if last_item_type is None:
            last_item_type = item_type
        elif last_item_type != item_type:
            raise ValueError('value has inconsistent types')

        converted_items.append(item)

    return 'ARRAY_TYPE', converted_items


def magic_table_convert_map(m):
    last_key_type = None
    last_value_type = None
    converted_items = {}

    for key, value in m:
        key_type, key = magic_table_convert(key)
        value_type, value = magic_table_convert(value)

        if last_key_type is None:
            last_key_type = key_type
        elif last_value_type != value_type:
            raise ValueError('value has inconsistent types')

        if last_value_type is None:
            last_value_type = value_type
        elif last_value_type != value_type:
            raise ValueError('value has inconsistent types')

        converted_items[key] = value

    return 'MAP_TYPE', converted_items


magic_table_types = {
    type(None): lambda x: ('NULL_TYPE', x),
    bool: lambda x: ('BOOLEAN_TYPE', x),
    int: lambda x: ('INT_TYPE', x),
    long: lambda x: ('BIGINT_TYPE', x),
    float: lambda x: ('DOUBLE_TYPE', x),
    str: lambda x: ('STRING_TYPE', str(x)),
    unicode: lambda x: ('STRING_TYPE', x.encode('utf-8')),
    datetime.date: lambda x: ('DATE_TYPE', str(x)),
    datetime.datetime: lambda x: ('TIMESTAMP_TYPE', str(x)),
    decimal.Decimal: lambda x: ('DECIMAL_TYPE', str(x)),
    tuple: magic_table_convert_seq,
    list: magic_table_convert_seq,
    dict: magic_table_convert_map,
}


def magic_table(name):
    try:
        value = global_dict[name]
    except KeyError:
        exc_type, exc_value, tb = sys.exc_info()
        return execute_reply_error(exc_type, exc_value, [])

    if not isinstance(value, (list, tuple)):
        value = [value]

    headers = {}
    data = []

    for row in value:
        cols = []
        data.append(cols)

        if not isinstance(row, (list, tuple, dict)):
            row = [row]

        if isinstance(row, (list, tuple)):
            iterator = enumerate(row)
        else:
            iterator = sorted(row.iteritems())

        for name, col in iterator:
            col_type, col = magic_table_convert(col)

            try:
                header = headers[name]
            except KeyError:
                header = {
                    'name': str(name),
                    'type': col_type,
                }
                headers[name] = header
            else:
                # Reject columns that have a different type.
                if header['type'] != col_type:
                    exc_type = Exception
                    exc_value = 'table rows have different types'
                    return execute_reply_error(exc_type, exc_value, [])

            cols.append(col)

    headers = [v for k, v in sorted(headers.iteritems())]

    return {
        'application/vnd.livy.table.v1+json': {
            'headers': headers,
            'data': data,
        }
    }


def magic_json(name):
    try:
        value = global_dict[name]
    except KeyError:
        exc_type, exc_value, tb = sys.exc_info()
        return execute_reply_error(exc_type, exc_value, [])

    return {
        'application/json': value,
    }


def shutdown_request(_content):
    sys.exit()


magic_router = {
    'table': magic_table,
    'json': magic_json,
}

msg_type_router = {
    'execute_request': execute_request,
    'shutdown_request': shutdown_request,
}

fake_stdin = cStringIO.StringIO()
fake_stdout = cStringIO.StringIO()
fake_stderr = cStringIO.StringIO()


def main():
    sys_stdin = sys.stdin
    sys_stdout = sys.stdout
    sys_stderr = sys.stderr

    sys.stdin = fake_stdin
    sys.stdout = fake_stdout
    sys.stderr = fake_stderr

    try:
        # Load spark into the context
        exec 'from pyspark.shell import sc' in global_dict

        print >> sys_stderr, fake_stdout.getvalue()
        print >> sys_stderr, fake_stderr.getvalue()

        fake_stdout.truncate(0)
        fake_stderr.truncate(0)

        print >> sys_stdout, 'READY'
        sys_stdout.flush()

        while True:
            line = sys_stdin.readline()

            if line == '':
                break
            elif line == '\n':
                continue

            try:
                msg = json.loads(line)
            except ValueError:
                LOG.error('failed to parse message', exc_info=True)
                continue

            try:
                msg_type = msg['msg_type']
            except KeyError:
                LOG.error('missing message type', exc_info=True)
                continue

            try:
                content = msg['content']
            except KeyError:
                LOG.error('missing content', exc_info=True)
                continue

            if not isinstance(content, dict):
                LOG.error('content is not a dictionary')
                continue

            try:
                handler = msg_type_router[msg_type]
            except KeyError:
                LOG.error('unknown message type: %s', msg_type)
                continue

            response = handler(content)

            try:
                response = json.dumps(response)
            except ValueError:
                response = json.dumps({
                    'msg_type': 'inspect_reply',
                    'content': {
                        'status': 'error',
                        'ename': 'ValueError',
                        'evalue': 'cannot json-ify %s' % response,
                        'traceback': [],
                    }
                })

            print >> sys_stdout, response
            sys_stdout.flush()
    finally:
        if 'sc' in global_dict:
            global_dict['sc'].stop()

        sys.stdin = sys_stdin
        sys.stdout = sys_stdout
        sys.stderr = sys_stderr


if __name__ == '__main__':
    sys.exit(main())
