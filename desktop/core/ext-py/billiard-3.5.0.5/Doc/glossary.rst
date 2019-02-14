.. _glossary:

********
Glossary
********

.. glossary::

   bytecode
      Python source code is compiled into bytecode, the internal representation
      of a Python program in the interpreter.  The bytecode is also cached in
      ``.pyc`` and ``.pyo`` files so that executing the same file is faster the
      second time (recompilation from source to bytecode can be avoided).  This
      "intermediate language" is said to run on a :term:`virtual machine`
      that executes the machine code corresponding to each bytecode.

   CPython
      The canonical implementation of the Python programming language.  The
      term "CPython" is used in contexts when necessary to distinguish this
      implementation from others such as Jython or IronPython.

   GIL
      See :term:`global interpreter lock`.
    
   global interpreter lock
      The lock used by Python threads to assure that only one thread
      executes in the :term:`CPython` :term:`virtual machine` at a time.
      This simplifies the CPython implementation by assuring that no two
      processes can access the same memory at the same time.  Locking the
      entire interpreter makes it easier for the interpreter to be
      multi-threaded, at the expense of much of the parallelism afforded by
      multi-processor machines.  Efforts have been made in the past to
      create a "free-threaded" interpreter (one which locks shared data at a
      much finer granularity), but so far none have been successful because
      performance suffered in the common single-processor case.

   virtual machine
      A computer defined entirely in software.  Python's virtual machine
      executes the :term:`bytecode` emitted by the bytecode compiler.
    
