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

def execute_request(msg):
    global execution_count

    try:
        code = msg['code']
    except KeyError:
        logger.error('missing code', exc_info=True)
        return

    execution_count += 1

    try:
        code = compile(code, '<stdin>', 'single')
        exec code in global_dict
    except:
        exc_type, exc_value, tb = sys.exc_info()
        return {
            'msg_type': 'execute_reply',
            'execution_count': execution_count - 1,
            'content': {
                'status': 'error',
                'ename': exc_type.__name__,
                'evalue': str(exc_value),
                'traceback': traceback.extract_tb(tb),
            }
        }

    stdout = fake_stdout.getvalue()
    stderr = fake_stderr.getvalue()

    output = ''

    if stdout:
        output += stdout

    if stderr:
        output += stderr

    return {
        'msg_type': 'execute_result',
        'execution_count': execution_count,
        'content': {
            'status': 'ok',
            'execution_count': execution_count - 1,
            'data': {
                'text/plain': output,
            },
        }
    }

def inspect_value(name):
    try:
        value = global_dict[name]
    except KeyError:
        return {
            'msg_type': 'inspect_reply',
            'execution_count': execution_count - 1,
            'content': {
                'status': 'error',
                'ename': 'KeyError',
                'evalue': 'unknown variable %s' % name,
            }
        }

    return {
        'msg_type': 'inspect_result',
        'content': {
            'data': {
                'application/json': value,
            },
        }
    }


inspect_router = {
    '%inspect': inspect_value,
}

def inspect_request(msg):
    try:
        code = msg['code']
    except KeyError:
        logger.error('missing code', exc_info=True)
        return

    try:
        inspect_magic, code = code.split(' ', 1)
    except ValueError:
        logger.error('invalid magic', exc_info=True)
        return

    try:
        handler = inspect_router[inspect_magic]
    except KeyError:
        logger.error('unknown magic', exc_info=True)
        return

    return handler(code)


msg_type_router = {
    'execute_request': execute_request,
    'inspect_request': inspect_request,
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
            logger.error('missing message type')
            continue

        try:
            handler = msg_type_router[msg_type]
        except KeyError:
            logger.error('unknown message type: %s', msg_type)
            continue

        response = handler(msg)
        if response is not None:
            try:
                response = json.dumps(response)
            except ValueError:
                response = json.dumps({
                    'msg_type': 'inspect_reply',
                    'execution_count': execution_count - 1,
                    'content': {
                        'status': 'error',
                        'ename': 'ValueError',
                        'evalue': 'cannot json-ify %s' % name,
                    }
                })

            print >> sys_stdout, response
            sys_stdout.flush()
finally:
    sys.stdin = sys_stdin
    sys.stdout = sys_stdout
    sys.stderr = sys_stderr
