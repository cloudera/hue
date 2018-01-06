import sys
import os
import traceback
try:
    import sqlite3
except ImportError:
    import pysqlite2.dbapi2 as sqlite3
import re
import glob


def parse_stdout(s):
    argv = re.search('^===ARGV=(.*?)$', s, re.M).group(1)
    argv = argv.split()
    testname = argv[-1]
    del argv[-1]
    hub = None
    reactor = None
    while argv:
        if argv[0] == '--hub':
            hub = argv[1]
            del argv[0]
            del argv[0]
        elif argv[0] == '--reactor':
            reactor = argv[1]
            del argv[0]
            del argv[0]
        else:
            del argv[0]
    if reactor is not None:
        hub += '/%s' % reactor
    return testname, hub

unittest_delim = '----------------------------------------------------------------------'


def parse_unittest_output(s):
    s = s[s.rindex(unittest_delim) + len(unittest_delim):]
    num = int(re.search('^Ran (\d+) test.*?$', s, re.M).group(1))
    ok = re.search('^OK$', s, re.M)
    error, fail, timeout = 0, 0, 0
    failed_match = re.search(
        r'^FAILED \((?:failures=(?P<f>\d+))?,? ?(?:errors=(?P<e>\d+))?\)$', s, re.M)
    ok_match = re.search('^OK$', s, re.M)
    if failed_match:
        assert not ok_match, (ok_match, s)
        fail = failed_match.group('f')
        error = failed_match.group('e')
        fail = int(fail or '0')
        error = int(error or '0')
    else:
        assert ok_match, repr(s)
    timeout_match = re.search('^===disabled because of timeout: (\d+)$', s, re.M)
    if timeout_match:
        timeout = int(timeout_match.group(1))
    return num, error, fail, timeout


def main(db):
    c = sqlite3.connect(db)
    c.execute('''create table if not exists parsed_command_record
              (id integer not null unique,
               testname text,
               hub text,
               runs integer,
               errors integer,
               fails integer,
               timeouts integer,
               error_names text,
               fail_names text,
               timeout_names text)''')
    c.commit()

    parse_error = 0

    SQL = ('select command_record.id, command, stdout, exitcode from command_record '
           'where not exists (select * from parsed_command_record where '
           'parsed_command_record.id=command_record.id)')
    for row in c.execute(SQL).fetchall():
        id, command, stdout, exitcode = row
        try:
            testname, hub = parse_stdout(stdout)
            if unittest_delim in stdout:
                runs, errors, fails, timeouts = parse_unittest_output(stdout)
            else:
                if exitcode == 0:
                    runs, errors, fails, timeouts = 1, 0, 0, 0
                if exitcode == 7:
                    runs, errors, fails, timeouts = 0, 0, 0, 1
                elif exitcode:
                    runs, errors, fails, timeouts = 1, 1, 0, 0
        except Exception:
            parse_error += 1
            sys.stderr.write('Failed to parse id=%s\n' % id)
            print(repr(stdout))
            traceback.print_exc()
        else:
            print(id, hub, testname, runs, errors, fails, timeouts)
            c.execute('insert into parsed_command_record '
                      '(id, testname, hub, runs, errors, fails, timeouts) '
                      'values (?, ?, ?, ?, ?, ?, ?)',
                      (id, testname, hub, runs, errors, fails, timeouts))
            c.commit()

if __name__ == '__main__':
    if not sys.argv[1:]:
        latest_db = sorted(glob.glob('results.*.db'), key=lambda f: os.stat(f).st_mtime)[-1]
        print(latest_db)
        sys.argv.append(latest_db)
    for db in sys.argv[1:]:
        main(db)
    execfile('generate_report.py')
