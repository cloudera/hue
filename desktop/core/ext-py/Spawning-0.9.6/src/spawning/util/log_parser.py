import time
from datetime import datetime, timedelta
import sys
import optparse
import re

__all__ = ['parse_line', 'parse_lines', 'parse_casual_time',
    'group_parsed_lines', 'select_timerange']

month_names = {'Jan': 1, 'Feb': 2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 
    'Aug':8,  'Sep': 9, 'Oct':10, 'Nov': 11, 'Dec': 12}


def parse_line(line):
    """ Parses a Spawning log line into a dictionary of fields.
    
    Returns the following fields: 
    * client_ip : The remote IP address.
    * date : datetime object representing when the request completed
    * method : HTTP method
    * path : url path
    * version : HTTP version
    * status_code : HTTP status code
    * size : length of the body
    * duration : time in seconds to complete the request
    """
    # note that a split-based version of the function is faster than
    # a regexp-based version
    segs = line.split()
    if len(segs) != 11:
        return None
    retval = {}
    try:
        retval['client_ip'] = segs[0]
        if segs[1] != '-' or segs[2] != '-':
            return None
        if segs[3][0] != '[' or segs[4][-1] != ']':
            return None
        # time parsing by explicitly poking at string slices is much faster 
        # than strptime, but it won't work in non-English locales because of 
        # the month names
        d = segs[3]
        t = segs[4]
        retval['date'] = datetime(
            int(d[8:12]),         # year
            month_names[d[4:7]],  # month
            int(d[1:3]),          # day
            int(t[0:2]),          # hour
            int(t[3:5]),          # minute
            int(t[6:8]))          # second
        if segs[5][0] != '"' or segs[7][-1] != '"':
            return None
        retval['method'] = segs[5][1:]
        retval['path'] = segs[6]
        retval['version'] = segs[7][:-1]
        retval['status_code'] = int(segs[8])
        retval['size'] = int(segs[9])
        retval['duration'] = float(segs[10])
    except (IndexError, ValueError):
        return None
    return retval
    
    
def parse_lines(fd):
    """Generator function that accepts an iterable file-like object and 
    yields all the parseable lines found in it.
    """
    for line in fd:
        parsed = parse_line(line)
        if parsed is not None:
            yield parsed


time_intervals = {"sec":1, "min":60, "hr":3600, "day": 86400,
                  "second":1, "minute":60, "hour":3600,
                  "s":1, "m":60, "h":3600, "d":86400}
for k,v in time_intervals.items():  # pluralize
    time_intervals[k + "s"] = v
    
    
def parse_casual_time(timestr, relative_to):
    """Lenient relative time parser.  Returns a datetime object if it can.
    
    Accepts such human-friendly times as "-1 hour", "-30s", "15min", "2d", "now".
    Any such relative time is interpreted as a delta applied to the relative_to
    argument, which should be a datetime.
    """
    timestr = timestr.lower()
    try:
        return datetime(*(time.strptime(timestr)[0:6]))
    except ValueError:
        pass
    if timestr == "now":
        return datetime.now()
    # match stuff like "-1 hour", "-30s"
    m = re.match(r'([-0-9.]+)\s*(\w+)?', timestr)
    if m:
        intervalsz = 1
        if len(m.groups()) > 1 and m.group(2) in time_intervals:
            intervalsz = time_intervals[m.group(2)]
        relseconds = float(m.group(1)) * intervalsz
        return relative_to + timedelta(seconds=relseconds)

def group_parsed_lines(lines, field):
    """Aggregates the parsed log lines by a field.  Counts
    the log lines in each group and their average duration.  The return
    value is a dict, where the keys are the unique field values, and the values
    are dicts of count, avg_duration, and the key.
    """
    grouped = {}
    for parsed in lines:
        key = parsed[field]
        summary = grouped.setdefault(key, {'count':0, 'total_duration':0.0})
        summary[field] = key
        summary['count'] += 1
        summary['total_duration'] += parsed['duration']
    # average dat up
    for summary in grouped.values():
        summary['avg_duration'] = summary['total_duration']/summary['count']
        del summary['total_duration']
    return grouped

def select_timerange(lines, earliest=None, latest=None):
    """ Generator that accepts an iterable of parsed log lines and yields
    the log lines that are between the earliest and latest dates.  If
    either earliest or latest is None, it is ignored."""
    for parsed in lines:
        if earliest and parsed['date'] < earliest:
            continue
        if latest and parsed['date'] > latest:
            continue
        yield parsed


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('--earliest', dest='earliest', default=None,
        help='Earliest date to count, either as a full date or a relative time \
such as "-1 hour".  Relative to --latest, so you generally want to\
specify a negative relative.')
    parser.add_option('--latest', dest='latest', default=None,
        help='Latest date to count, either as a full date or a relative time\
such as "-30s".  Relative to now.')
    parser.add_option('--group-by', dest='group_by', default='path',
        help='Compute counts and aggregates for log lines grouped by this\
attribute.  Good values include "status_code", "method", and\
"path" (the default).')
    opts, args = parser.parse_args()

    if opts.latest:
        opts.latest = parse_casual_time(opts.latest, datetime.now())
    if opts.earliest:
        opts.earliest = parse_casual_time(opts.earliest, 
                                            opts.latest or datetime.now())
    if opts.earliest or opts.latest:
        print "Including dates between", \
            opts.earliest or "the beginning of time", "and", opts.latest or "now"
    
    parsed_lines = parse_lines(sys.stdin)
    grouped = group_parsed_lines(
        select_timerange(parsed_lines, opts.earliest, opts.latest),
        opts.group_by)
    
    flat = grouped.values()
    flat.sort(key=lambda x: x['count'])
    flat.reverse()
    print "Count\tAvg Dur\t%s" % opts.group_by
    for summary in flat:
        print "%d\t%.4f\t%s" % (summary['count'], 
            summary['avg_duration'], summary[opts.group_by])

