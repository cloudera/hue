import ast
import cStringIO
import datetime
import decimal
import json
import logging
import sys
import traceback

logging.basicConfig()
logger = logging.getLogger('fake_shell')

sys_stdin = sys.stdin
sys_stdout = sys.stdout
sys_stderr = sys.stderr

fake_stdin = cStringIO.StringIO()
fake_stdout = cStringIO.StringIO()
fake_stderr = cStringIO.StringIO()

sys.stdin = fake_stdin
sys.stdout = fake_stdout
sys.stderr = fake_stderr

global_dict = {}

execution_count = 0


def execute_reply(status, content):
    global execution_count
    execution_count += 1

    return {
        'msg_type': 'execute_reply',
        'content': dict(
            content,
            status=status,
            execution_count=execution_count - 1
        )
    }

def execute_reply_ok(data):
    return execute_reply('ok', {
        'data': data,
    })

def execute_reply_error(exc_type, exc_value, tb):
    logger.error('execute_reply', exc_info=True)
    return execute_reply('error', {
        'ename': unicode(exc_type.__name__),
        'evalue': unicode(exc_value),
        'traceback': traceback.format_exception(exc_type, exc_value, tb, -1),
    })


def execute(code):
    try:
        code = ast.parse(code)
        to_run_exec, to_run_single = code.body[:-1], code.body[-1:]

        for node in to_run_exec:
            mod = ast.Module([node])
            code = compile(mod, '<stdin>', 'exec')
            exec code in global_dict

        for node in to_run_single:
            mod = ast.Interactive([node])
            code = compile(mod, '<stdin>', 'single')
            exec code in global_dict
    except:
        return execute_reply_error(*sys.exc_info())

    stdout = fake_stdout.getvalue()
    stderr = fake_stderr.getvalue()

    output = ''

    if stdout:
        output += stdout

    if stderr:
        output += stderr

    return execute_reply_ok({
        'text/plain': output.rstrip(),
        })


def execute_request(content):
    try:
        code = content['code']
    except KeyError:
        exc_type, exc_value, tb = sys.exc_info()
        return execute_reply_error(exc_type, exc_value, [])

    lines = code.split('\n')

    if lines and lines[-1].startswith('%'):
        code, magic = lines[:-1], lines[-1]

        # Make sure to execute the other lines first.
        if code:
            result = execute('\n'.join(code))
            if result['content']['status'] != 'ok':
                return result

        parts = magic[1:].split(' ', 1)
        if len(parts) == 1:
            magic, rest = parts[0], ()
        else:
            magic, rest = parts[0], (parts[1],)

        try:
            handler = magic_router[magic]
        except KeyError:
            exc_type, exc_value, tb = sys.exc_info()
            return execute_reply_error(exc_type, exc_value, [])
        else:
            return handler(*rest)
    else:
        return execute(code)


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

    return 'MAP_TYPE', items


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
            iterator = row.iteritems()

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

    return execute_reply_ok({
        'application/vnd.livy.table.v1+json': {
            'headers': headers,
            'data': data,
        }
    })


magic_router = {
    'table': magic_table,
}


msg_type_router = {
    'execute_request': execute_request,
}


try:
    while True:
        fake_stdout.truncate(0)

        line = sys_stdin.readline()

        if line == '':
            break
        elif line == '\n':
            continue

        try:
            msg = json.loads(line)
        except ValueError:
            logger.error('failed to parse message', exc_info=True)
            continue

        try:
            msg_type = msg['msg_type']
        except KeyError:
            logger.error('missing message type', exc_info=True)
            continue

        try:
            content = msg['content']
        except KeyError:
            logger.error('missing content', exc_info=True)
            continue

        try:
            handler = msg_type_router[msg_type]
        except KeyError:
            logger.error('unknown message type: %s', msg_type)
            continue

        response = handler(content)
        try:
            response = json.dumps(response)
        except ValueError, e:
            response = json.dumps({
                'msg_type': 'inspect_reply',
                'execution_count': execution_count - 1,
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
    sys.stdin = sys_stdin
    sys.stdout = sys_stdout
    sys.stderr = sys_stderr
