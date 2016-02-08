
===========================
Grant Proposal for CFFI 1.0
===========================

*Accepted by the PSF board on April 4, 2015*

This Grant Proposal is to give a boost towards "CFFI 1.0".  Two main
issues with the current CFFI need to be solved: the difficulties of
installation, and the potentially large time taken at import.

1. The difficulties of installation can be seen from outside by looking
at various workarounds and 3rd-party documentation that have grown into
existence.  For example, the `setup.py` of projects like cryptography,
PyNaCl and bcrypt deploys workarounds that are explicitly documented in
https://caremad.io/2014/11/distributing-a-cffi-project/.

2. The time taken at import is excessive in some cases.  For example,
importing `pygame-cffi` on a Raspberry Pi ARM board takes on the order
of 10 to 20 seconds (and this is the "fast" case where the compiler
doesn't need to be invoked any more).


Technical Overview
------------------

"CFFI" is an existing Python project which complements the ctypes,
SWIG and Cython approaches to ease writing C Extension Modules for
Python.  It has several advantages over the previous approaches, which
are presented at the start of the documentation at
http://cffi.readthedocs.org/en/latest/ .  It has been very successful
so far: http://pypi-ranking.info/alltime records almost 7 million
downloads (for comparison, the #1 of all packages has almost 36
million downloads).  CFFI works on any Python >= 2.6, including 3.x,
as well as on PyPy.

One problem is that while getting started with CFFI is very easy, the
installation process of a package that uses CFFI has got its rough
edges.  CFFI (at least in its "verify()" mode) is based on calling the
C compiler to get information about the exact C types, structures,
argument types to functions, and so on.  The C compiler is invoked
transparently at run-time, and the results cached.  A
correctly-installed package using CFFI should cache the results at
installation time, but it can be difficult to ensure that no more
run-time compiler invocation is needed; doing so requires following
some extra guidelines or understanding some internal details.  (The
problem is particularly acute on Windows where a typical user might
not have a proper C compiler installed.)

To fix this, we have in mind adding a different CFFI mode (replacing
"verify()"), while keeping the access to the underlying C library
unmodified.  In this mode, the code containing the cdef() and verify()
invocations would be moved to a separate Python source file.  Running
that Python file would produce a dynamically-linked library.  There
would be no caching logic involved; you would need to run it
explicitly during development whenever you made changes to it, to
re-generate and re-compile the dynamically-linked library.

When distributed, the same file would be run (once) during
installation.  This can be fully automated in setuptools-based
setup.py files; alternatively, it can be done in distutils-based
setup.py files by requiring prior manual installation of CFFI itself.

A major difference with the existing verify() approach would be that
the ``.so/.dll/.dylib`` file would not be immediately loaded into the
process; you would load it only from the installed program at
run-time, and get the ``ffi`` and ``lib`` objects in this way (these
are the two objects that you use so far to access a C library with
verify()).

Additionally, this would solve another issue: every import of a large
CFFI-using package takes a while so far.  This is caused by CFFI
needing to parse again the C source code given in the cdef() (adding a
run-time dependency to the ``pycparser`` and ``ply`` packages).  CFFI
also computes a CRC to know if it can reuse its cache.  In the
proposed change, all the cdef() code would be pre-parsed and stored in
the dynamically-linked library, and no CRC would be needed.  This
would massively reduce the import times.


Grant objective
---------------

The objective is to give a boost towards "CFFI 1.0", which needs to have
the functionalities described above in order to solve the two main
issues with the current CFFI: the difficulties of installation, and the
time taken at import.

Included in the objective: the internal refactorings of CFFI that are
needed to get it done cleanly.  The goal is to avoid simply adding
another layer on top of the old unchanged CFFI.

This work may happen eventually in any case, but support from the PSF
would help make it happen sooner rather than later.


Grant size
----------

2'500 US$ for supporting the development time.  This would cover 2.5
weeks of full-time work at the part-time cost of 25 US$ per hour.

The estimated work time until the CFFI 1.0 release is a bit larger
than that (I estimate it at roughly 4 weeks), but 2.5 weeks should
cover all the basics.  An extended grant size of 4'000 US$ would be
appreciated but not required ``:-)``


Grant beneficiaries
-------------------

Armin Rigo, main author of CFFI, committing 2.5 weeks of full-time
work.


Grant follow-up
---------------

I will report on the success of the grant on the CFFI mailing list and
on the blog I usually post to (the PyPy blog) and mention the PSF as
providing the grant.  The PSF will receive an email pointing to these
postings once they are out.  Moreover a full CFFI 1.0 release should
follow (likely starting with beta versions); the PSF will receive
another email pointing to it.
