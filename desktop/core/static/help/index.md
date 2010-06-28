Welcome to Hue!
===============

<img src='/static/art/help/logo.png' class="help-logo">

Hue is a browser based environment for interacting with your
Hadoop cluster.  You or your system administrator has already
installed the system (excellent!); this document will help get you oriented.

## Starting Applications

The icons at the bottom of your screen, when clicked, will open
different applications (e.g., the file browser or the health dashboard).
Double-click to open a second instance of an application.
<img src="/static/help/images/dock.gif"/>

## Logging in and out

The logout link is in the top left of your screen, right after your
username.  When you log out, Hue will restore the 
application windows you had open.

## Keyboard Shortcuts

To see what keyboard shortcuts are available, type "Ctrl-/" or 
click on the "command" clover in the top right corner of the screen.  
<img src="/static/help/images/shortcuts.gif"/>

## Changing your password

If authentication is managed by Desktop (i.e., it is not configured
to authenticate via some other mechanism), the 
<a href="/help/useradmin/index.md">User Manager</a> application
allows you to change your password.

## Seeking Help, Reporting Bugs, and Providing Feedback

The Hue team strongly values your feedback!
The "feedback" link in the bottom right of your screen
is the best way to reach us.

If you're experiencing transient errors (typically
an error message saying a service is down), you may
wish to run them by your system administrator first.

Every window that's rendered in Hue
is typically backed by an HTTP GET or POST request 
sent to the server via AJAX.  If you're familiar with
web development, and you're reporting a problem or bug,
it's very useful to use Firebug (or similar) to figure out
what request is failing, and include that in
your bug report.

## Browser Compatibility

Hue works best in Firefox, and works well in Chrome
and Safari as well.

## Extending Desktop

Hue has an SDK to build new applications within
the framework.  Contact us (again, via the feedback link)
if you're interested in building new applications within the
framework.

## Help for the Applications

Each application installed within Hue
may have its own help page(s).  The index below
directs you there.
