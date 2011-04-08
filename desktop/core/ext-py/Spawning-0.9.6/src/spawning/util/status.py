import datetime
try:
    import json
except ImportError:
    import simplejson as json

import eventlet
from eventlet import event
from eventlet import wsgi
from eventlet.green import os

class Server(object):
    def __init__(self, controller, host, port):
        self.controller = controller
        self.host = host
        self.port = port
        self.status_waiter = None
        self.child_events = {}
        socket = eventlet.listen((host, port))
        wsgi.server(socket, self.application)

    def get_status_data(self):
        # using a waiter because we only want one child collection ping
        # happening at a time; if there are multiple concurrent status requests,
        # they all simply share the same set of data results
        if self.status_waiter is None:
            self.status_waiter = eventlet.spawn(self._collect_status_data)
        return self.status_waiter.wait()
    
    def _collect_status_data(self):
        try:
            now = datetime.datetime.now()
            children = self.controller.children.values()
            status_data = {
                'active_children_count':len([c 
                    for c in children
                    if c.active]),
                'killed_children_count':len([c 
                    for c in children
                    if not c.active]),
                'configured_children_count':self.controller.num_processes,
                'now':now.ctime(),
                'pid':os.getpid(),
                'uptime':format_timedelta(now - self.controller.started_at),
                'started_at':self.controller.started_at.ctime(),
                'config':self.controller.config}
            # fire up a few greenthreads to wait on children's responses
            p = eventlet.GreenPile()
            for child in self.controller.children.values():
                p.spawn(self.collect_child_status, child)
            status_data['children'] = dict([pid_cd for pid_cd in p])
            
            # total concurrent connections
            status_data['concurrent_requests'] = sum([
                child.get('concurrent_requests', 0)
                for child in status_data['children'].values()])
        finally:
            # wipe out the waiter so that subsequent requests create new ones
            self.status_waiter = None
        return status_data

    def collect_child_status(self, child):
        self.child_events[child.pid] = event.Event()
        try:
            try:
                # tell the child to POST its status to us, we handle it in the
                # wsgi application below
                eventlet.hubs.trampoline(child.kill_pipe, write=True)
                os.write(child.kill_pipe, 's')
                t = eventlet.Timeout(1)
                results = self.child_events[child.pid].wait()
                t.cancel()
            except (OSError, IOError), e:
                results = {'error': "%s %s" % (type(e), e)}
            except eventlet.Timeout:
                results = {'error':'Timed out'}
        finally:
            self.child_events.pop(child.pid, None)
            
        results.update({
            'pid':child.pid, 
            'active':child.active,
            'uptime':format_timedelta(datetime.datetime.now() - child.forked_at),
            'forked_at':child.forked_at.ctime()})
        return child.pid, results

    def application(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'GET':
            status_data = self.get_status_data()
            if environ['PATH_INFO'] == '/status':
                start_response('200 OK', [('content-type', 'text/html')])
                return [fill_template(status_data)]
            elif environ['PATH_INFO'] == '/status.json':
                start_response('200 OK', [('content-type', 'application/json')])
                return [json.dumps(status_data, indent=2)]
                
        elif environ['REQUEST_METHOD'] == 'POST':
            # it's a client posting its stats to us
            body = environ['wsgi.input'].read()
            child_status = json.loads(body)
            pid = child_status['pid']
            if pid in self.child_events:
                self.child_events[pid].send(child_status)
                start_response('200 OK', [('content-type', 'application/json')])
            else:
                start_response('500 Internal Server Error', 
                               [('content-type', 'text/plain')])
                print "Don't know about child pid %s" % pid
            return [""]
        
        # fallthrough case
        start_response('404 Not Found', [('content-type', 'text/plain')])
        return [""]

def format_timedelta(t):
    """Based on how HAProxy's status page shows dates.
    10d 14h
    3h 20m
    1h 0m
    12m
    15s
    """
    seconds = t.seconds
    if t.days > 0:
        return "%sd %sh" % (t.days, int(seconds/3600))
    else:
        if seconds > 3600:
            hours = int(seconds/3600)
            seconds -= hours*3600
            return "%sh %sm" % (hours, int(seconds/60))
        else:
            if seconds > 60:
                return "%sm" % int(seconds/60)
            else:
                return "%ss" % seconds

class Tag(object):
    """Yeah, there's a templating DSL in this status module.  Deal with it."""
    def __init__(self, name, *children, **attrs):
        self.name = name
        self.attrs = attrs
        self.children = list(children)

    def __str__(self):
        al = []
        for name, val in self.attrs.iteritems():
            if name == 'cls':
                name = "class"
            if isinstance(val, (list, tuple)):
                val = " ".join(val)
            else:
                val = str(val)
            al.append('%s="%s"' % (name, val))
        if al:
            attrstr = " " + " ".join(al) + " "
        else:
            attrstr = ""
        cl = []
        for child in self.children:
            cl.append(str(child))
        if cl:
            childstr = "\n" + "\n".join(cl) + "\n"
        else:
            childstr = ""
        return "<%s%s>%s</%s>" % (self.name, attrstr, childstr, self.name)

def make_tag(name):
    return lambda *c, **a: Tag(name, *c, **a)
p = make_tag('p')
div = make_tag('div')
table = make_tag('table')
tr = make_tag('tr')
th = make_tag('th')
td = make_tag('td')
h2 = make_tag('h2')
span = make_tag('span')

def fill_template(status_data):
    # controller status
    cont_div = table(id='controller')
    cont_div.children.append(tr(th("PID:", title="Controller Process ID"), 
        td(status_data['pid'])))
    cont_div.children.append(tr(th("Uptime:", title="Time since launch"), 
        td(status_data['uptime'])))
    cont_div.children.append(tr(th("Host:", title="Host and port server is listening on, all means all interfaces."), 
        td("%s:%s" % (status_data['config']['host'] or "all",
            status_data['config']['port']))))
    cont_div.children.append(tr(th("Threads:", title="Threads per child"), 
        td(status_data['config']['threadpool_workers'])))
    cont_div = div(cont_div)
    
    # children headers and summaries
    child_div = div(h2("Child Processes"))
    count_td = td(status_data['active_children_count'], "/", 
                  status_data['configured_children_count'])
    if status_data['active_children_count'] < \
       status_data['configured_children_count']:
        count_td.attrs['cls'] = "error"
        count_td.children.append(
            span("(", status_data['killed_children_count'], ")"))
    children_table = table(
      tr(
        th('PID', title="Process ID"), 
        th('Active', title="Accepting New Requests"), 
        th('Uptime', title="Uptime"), 
        th('Concurrent', title="Concurrent Requests")),
      tr(
        td("Total"),
        count_td,
        td(),  # no way to "total" uptime
        td(status_data['concurrent_requests'])),
      id="children")
    child_div.children.append(children_table)
    
    # children themselves
    odd = True
    for pid in sorted(status_data['children'].keys()):
        child = status_data['children'][pid]
        row = tr(td(pid), cls=['child'])
        if odd:
            row.attrs['cls'].append('odd')
        odd = not odd
        
        # active handling
        row.children.append(td({True:'Y', False:'N'}[child['active']]))
        if not child['active']:
            row.attrs['cls'].append('dying')
            
        # errors
        if child.get('error'):
            row.attrs['cls'].append('error')
            row.children.append(td(child['error'], colspan=2))
        else:
            # no errors
            row.children.append(td(child['uptime']))
            row.children.append(td(child['concurrent_requests']))
            
        children_table.children.append(row)
        
    # config dump
    config_div = div(
        h2("Configuration"),
        table(*[tr(th(key),  td(status_data['config'][key]))
            for key in sorted(status_data['config'].keys())]), 
        id='config')
        
    to_format = {'cont_div': cont_div, 'child_div':child_div,
                 'config_div':config_div}
    to_format.update(status_data)
    return HTML_SHELL % to_format

HTML_SHELL = """
<!DOCTYPE html>
<html><head>
<title>Spawning Status</title>
<style type="text/css">
html, p, div, table, h1, h2, input, form {
	margin: 0;
	padding: 0;
	border: 0;
	outline: 0;
	font-size: 12px;
	font-family: Helvetica, Arial, sans-serif;
	vertical-align: baseline;
}
body {
	line-height: 1.2;
	color: black;
	background: white;
	margin: 3em;
}
table {
	border-collapse: separate;
	border-spacing: 0;
}
th, td {
	text-align: center;
	padding: .1em;
    padding-right: .4em;
}
#controller td, #controller th {
    text-align: left;
}
#config td, #config th {
    text-align: left;
}
#children {
    clear: both;
}
#options {
    float: right;
    border: 1px solid #dfdfdf;
    padding:.5em;
}
h1,h2 {
    margin: .5em;
    margin-left: 0em;
    font-size: 130%%;  
}
h2 {
    font-size: 115%%;  
}
tr.odd {
    background: #dfdfdf;
}
input {
    border: 1px solid grey;
}
#refresh form {
    display: inline;
}
tr.child.dying {
    font-style: italic;
    color: #444444;
}
.error {
    background: #ff4444;
}

/* Cut out the fat for mobile devices */
@media screen and (max-width: 400px) {
    body {
        margin-left: .2em;
        margin-right: .2em;
    }
    #options {
        float: none;
    }
}
</style>
</head><body>
<h1>Spawning Status</h1>
<div id="options">
<p>%(now)s</p>
<div id="refresh">
<a href="">Refresh</a> (<form>
  <input type="checkbox" /> every
  <input type="text" value="5" size=2 />s
</form>)
</div>
<a href="status.json">JSON</a>
</div>
%(cont_div)s
%(child_div)s
%(config_div)s
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"></script>
<script type="text/javascript">
$(document).ready(function() {
    var timer;
    var arrangeTimeout = function () {
        clearTimeout(timer);
        if($('#refresh input[type=checkbox]').attr('checked')) {
            timer = setTimeout(
                function() {window.location.reload();},
                $('#refresh input[type=text]').val() * 1000);
        }
        if($(this).is('form')) {
            return false;
        }
    };
    $('#refresh input[type=checkbox]').click(arrangeTimeout);
    $('#refresh form').submit(arrangeTimeout).submit();
});
</script>
</body></html>
"""
