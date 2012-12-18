django-moxy
============


### What it is

"Moxy" is a Django database backend for MySQL. Built on top of MySQLdb [0]
and Eventlet [1], it uses eventlet.db_pool to provide a greenthread-safe 
means of accessing MySQL via MySQLdb's blocking calls.


### Why Moxy?

Another member of the `#eventlet` channel on Freenode was soliciting for names
of a reverse proxying HTTP server he wrote built off of Eventlet. I suggested
the name "Moxy" which was well received until everybody started listing examples
of other projects named "Moxy".

Since then it's become a kind of lame inside joke to suggest "Moxy" as the name for
any new project.




[0] http://sourceforge.net/projects/mysql-python/
[1] http://eventlet.net
