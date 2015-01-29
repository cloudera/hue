import cStringIO
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
        code = compile(code, '<stdin>', 'single')
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


def table_magic(name):
    try:
        value = global_dict[name]
    except KeyError:
        exc_type, exc_value, tb = sys.exc_info()
        return execute_reply_error(exc_type, exc_value, [])

    max_list_cols = 0
    dict_headers = set()

    if isinstance(value, list):
        for row in value:
            if isinstance(row, dict):
                dict_headers.update(row.iterkeys())
            elif isinstance(row, list):
                max_list_cols = max(max_list_cols, len(row))
            else:
                return execute_reply_error(Exception, 'row is not a list or dict', [])
    elif isinstance(value, dict):
        dict_headers = value.keys()
        value = [value]
    else:
        return execute_reply_error(Exception, 'value is not a list or dict', [])

    headers = [i for i in xrange(max_list_cols)]
    dict_header_offset = len(headers)
    dict_header_index = {}

    for i, key in enumerate(sorted(dict_headers)):
        headers.append(key)
        dict_header_index[key] = dict_header_offset + i

    table = []

    for row in value:
        table_row = [None] * len(headers)
        table.append(table_row)

        if isinstance(row, list):
            for i, col in enumerate(row):
                table_row[i] = col
        else:
            for key, col in row.iteritems():
                i = dict_header_index[key]
                table_row[i] = col

    return execute_reply_ok({
        'application/vnd.livy.table.v1+json': {
            'headers': headers,
            'data': table,
        }
    })


magic_router = {
    'table': table_magic,
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
