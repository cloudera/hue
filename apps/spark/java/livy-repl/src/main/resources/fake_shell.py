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

    if code.startswith('%'):
        parts = code[1:].split(' ', 1)
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


magic_table_types = {
    type(None): ('NULL_TYPE', lambda x: x),
    bool: ('BOOLEAN_TYPE', lambda x: x),
    int: ('INT_TYPE', lambda x: x),
    long: ('BIGINT_TYPE', lambda x: x),
    float: ('DOUBLE_TYPE', lambda x: x),
    str: ('STRING_TYPE', lambda x: x),
    unicode: ('STRING_TYPE', lambda x: x.encode('utf-8')),
    datetime.date: ('DATE_TYPE', str),
    datetime.datetime: ('TIMESTAMP_TYPE', str),
    decimal.Decimal: ('DECIMAL_TYPE', str),
}


def magic_table(name):
    try:
        value = global_dict[name]
    except KeyError:
        exc_type, exc_value, tb = sys.exc_info()
        return execute_reply_error(exc_type, exc_value, [])

    if isinstance(value, dict):
        value = [value]

    if not isinstance(value, list):
      return execute_reply_error(Exception, 'row is not a list or dict', [])

    headers = {}
    table = []
    last_row_type = None

    for row in value:
        # Reject tables that contain different row types.
        if last_row_type is None:
            last_row_type = type(row)
        elif last_row_type != type(row):
            return execute_reply_error(Exception, 'table contains different row types', [])

        table_row = []
        table.append(table_row)

        if isinstance(row, dict):
            iterator = row.iteritems()
        elif isinstance(row, list):
            iterator = enumerate(row)
        else:
            return execute_reply_error(Exception, 'value is not a list or dict', [])

        for k, v in iterator:
            try:
                type_name, type_converter = magic_table_types[type(v)]
            except KeyError:
                type_name, type_converter = 'STRING', str

            table_row.append(type_converter(v))

            try:
                header = headers[k]
            except KeyError:
                header = {
                    'name': str(k),
                    'type': type_name,
                }
                headers[k] = header
            else:
                # Reject columns that have a different type.
                if header['type'] != type_name:
                    exc_type = Exception
                    exc_value = 'table rows have different types'
                    return execute_reply_error(exc_type, exc_value, [])

    headers = [v for k, v in sorted(headers.iteritems())]

    return execute_reply_ok({
        'application/vnd.livy.table.v1+json': {
            'headers': headers,
            'data': table,
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
