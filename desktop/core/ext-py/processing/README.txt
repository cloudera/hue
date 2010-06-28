.. default-role:: literal
.. include:: doc/version.txt

===================
 Python processing
===================

:Author:        R Oudkerk
:Contact:       roudkerk at users.berlios.de
:Url:           http://developer.berlios.de/projects/pyprocessing
:Version:       |version|
:Licence:       BSD Licence

`processing` is a package for the Python language which supports the
spawning of processes using the API of the standard library's
`threading` module.  It runs on both Unix and Windows.

Features:

* Objects can be transferred between processes using pipes or 
  multi-producer/multi-consumer queues.

* Objects can be shared between processes using a server process or
  (for simple data) shared memory.

* Equivalents of all the synchronization primitives in `threading` 
  are available.  

* A `Pool` class makes it easy to submit tasks to a pool of worker
  processes.


Links
=====

* `Documentation <./doc/index.html>`_
* `Installation instructions <./doc/INSTALL.html>`_
* `Changelog <./doc/CHANGES.html>`_
* `Acknowledgments <./doc/THANKS.html>`_
* `BSD Licence <./doc/COPYING.html>`_

The project is hosted at

*    http://developer.berlios.de/projects/pyprocessing

The package can be downloaded from

*    http://developer.berlios.de/project/filelist.php?group_id=9001 or
*    http://pypi.python.org/pypi/processing


Examples
========

The `processing.Process` class follows the API of `threading.Thread`.
For example ::

    from processing import Process, Queue

    def f(q):
        q.put('hello world')

    if __name__ == '__main__':
        q = Queue()
        p = Process(target=f, args=[q])
        p.start()
        print q.get()
        p.join()

Synchronization primitives like locks, semaphores and conditions are
available, for example ::

    >>> from processing import Condition
    >>> c = Condition()
    >>> print c
    <Condition(<RLock(None, 0)>), 0>
    >>> c.acquire()
    True
    >>> print c
    <Condition(<RLock(MainProcess, 1)>), 0>

One can also use a manager to create shared objects either in shared
memory or in a server process, for example ::

    >>> from processing import Manager
    >>> manager = Manager()
    >>> l = manager.list(range(10))
    >>> l.reverse()
    >>> print l
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    >>> print repr(l)
    <Proxy[list] object at 0x00E1B3B0>

Tasks can be offloaded to a pool of worker processes in various ways, 
for example ::

    >>> from processing import Pool
    >>> def f(x): return x*x
    ...
    >>> p = Pool(4)
    >>> result = p.mapAsync(f, range(10))
    >>> print result.get(timeout=1)
    [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]


.. raw:: html

    <a href="http://developer.berlios.de" title="BerliOS Developer"> 
    <img src="http://developer.berlios.de/bslogo.php?group_id=9001" 
    width="124px" height="32px" border="0" alt="BerliOS Developer Logo"></a>
