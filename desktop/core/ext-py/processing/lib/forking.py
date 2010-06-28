#
# Module for starting a process object using os.fork() or CreateProcess()
#
# processing/forking.py
#
# Copyright (c) 2006-2008, R Oudkerk --- see COPYING.txt
#

import os
import sys
import signal
import processing

__all__ = ['Popen', 'assertSpawning', 'exit']

#
# Check that the current thread is spawining a child process
#

def assertSpawning(self):
    if not thisThreadIsSpawning():
        raise RuntimeError, \
              ('%s objects should only be shared between '
               'processes through inheritance' % type(self).__name__)

#
# Unix
#

if sys.platform != 'win32':
    import time
    import errno

    exit = os._exit

    def thisThreadIsSpawning():
        return False

    #
    # We define a Popen class similar to the one from subprocess, but
    # whose constructor takes a process object as its argument, and which
    # has terminate() and waitTimeout() methods.
    #

    class Popen(object):

        def __init__(self, process_obj):
            sys.stdout.flush()
            sys.stderr.flush()
            self.returncode = None

            self.pid = os.fork()
            if self.pid == 0:                
                if 'random' in sys.modules:
                    import random
                    random.seed()

                code = process_obj._bootstrap()

                sys.stdout.flush()
                sys.stderr.flush()
                os._exit(code)

        def wait(self):
            return self.poll(0)

        def poll(self, flag=os.WNOHANG):
            if self.returncode is None:
                pid, sts = os.waitpid(self.pid, flag)
                if pid == self.pid:
                    if os.WIFSIGNALED(sts):
                        self.returncode = -os.WTERMSIG(sts)
                    else:
                        assert os.WIFEXITED(sts)
                        self.returncode = os.WEXITSTATUS(sts)
            return self.returncode

        def waitTimeout(self, timeout):
            deadline = time.time() + timeout
            delay = 0.0005
            while 1:
                res = self.poll()
                if res is not None:
                    break
                remaining = deadline - time.time()
                if remaining <= 0:
                    break
                delay = min(delay * 2, remaining, 0.05)
                time.sleep(delay)
            return res

        def terminate(self):
            if self.returncode is None:
                try:
                    os.kill(self.pid, signal.SIGTERM)
                except OSError, e:
                    if self.waitTimeout(0.1) is None:
                        raise
                    
#
# Windows
#

else:
    import imp, thread, msvcrt, _subprocess
    from os.path import dirname, splitext, basename, abspath
    from cPickle import dump, load, HIGHEST_PROTOCOL
    from processing._processing import win32
    from processing._processing import _hInterruptEvent, _main_thread_ident
    from processing.finalize import Finalize

    TERMINATE = 0x10000
    WINEXE = (sys.platform == 'win32' and getattr(sys, 'frozen', False))

    exit = win32.ExitProcess
    tls = thread._local()

    def thisThreadIsSpawning():
        return getattr(tls, 'is_spawning', False)

    #
    # We define a Popen class similar to the one from subprocess, but
    # whose constructor takes a process object as its argument, and which
    # has terminate() and waitTimeout() methods.
    #

    class Popen(object):
        '''
        Start a subprocess to run the code of a process object
        '''
        def __init__(self, process_obj):
            # create pipe for communication with child
            r, w = os.pipe()

            # get handle for read end of the pipe and make it inheritable
            rhandle = msvcrt.get_osfhandle(r)
            win32.SetHandleInformation(
                rhandle, win32.HANDLE_FLAG_INHERIT, win32.HANDLE_FLAG_INHERIT
                )

            # start process
            cmd = getCommandLine() + [rhandle]
            cmd = ' '.join('"%s"' % x for x in cmd)
            hp, ht, pid, tid = _subprocess.CreateProcess(
                sys.executable, cmd, None, None, 1, 0, None, None, None
                )
            os.close(r)
            ht.Close()

            # set attributes of self
            self.pid = pid
            self.returncode = None
            self._handle = hp

            # send information to child
            prep_data = getPreparationData(process_obj._name)
            to_child = os.fdopen(w, 'wb')
            tls.is_spawning = True
            try:
                dump(prep_data, to_child, HIGHEST_PROTOCOL)
                dump(process_obj, to_child, HIGHEST_PROTOCOL)
            finally:
                tls.is_spawning = False
                to_child.close()

        def waitTimeout(self, timeout):            
            if self.returncode is None:
                if timeout is None:
                    msecs = win32.INFINITE
                else:
                    msecs = int(timeout * 1000 + 0.5)

                if _main_thread_ident == thread.get_ident():
                    win32.ResetEvent(_hInterruptEvent)
                    handles = (int(self._handle), _hInterruptEvent)
                else:
                    handles = (int(self._handle),)

                res = win32.WaitForMultipleObjects(
                    len(handles), handles, False, msecs
                    )

                if res == win32.WAIT_OBJECT_0:
                    code = win32.GetExitCodeProcess(int(self._handle))
                    if code == TERMINATE:
                        code = -signal.SIGTERM
                    self.returncode = code

            return self.returncode

        def wait(self):
            return self.waitTimeout(None)

        def poll(self):
            return self.waitTimeout(0)

        def terminate(self):
            if self.returncode is None:
                try:
                    win32.TerminateProcess(int(self._handle), TERMINATE)
                except WindowsError:
                    if self.waitTimeout(0.1) is None:
                        raise
        
    #
    #
    #

    def isForking(argv):
        '''
        Return whether commandline indicates we are forking
        '''
        if len(argv) >= 2 and argv[1] == '--processing-fork':
            assert len(argv) == 3
            return True
        else:
            return False


    def freezeSupport():
        '''
        Run code for process object if this in not the main process
        '''
        if isForking(sys.argv):
            main()
            sys.exit()


    def getCommandLine():
        '''
        Returns prefix of command line used for spawning a child process
        '''
        if processing.currentProcess()._identity==() and isForking(sys.argv):
            raise RuntimeError, '''
            Attempt to start a new process before the current process
            has finished its bootstrapping phase.

            This probably means that you are on Windows and you have
            forgotten to use the proper idiom in the main module:

                if __name__ == '__main__':
                    freezeSupport()
                    ...

            The "freezeSupport()" line can be omitted if the program
            is not going to be frozen to produce a Windows executable.'''

        prog = 'from processing.forking import main; main()'
        if getattr(sys, 'frozen', False):
            return [sys.executable, '--processing-fork']
        elif sys.executable.lower().endswith('pythonservice.exe'):
            exe = os.path.join(os.path.dirname(os.__file__),'..','python.exe')
            return [exe, '-c', prog, '--processing-fork']
        else:
            return [sys.executable, '-c', prog, '--processing-fork']


    def getPreparationData(name):
        '''
        Return info about parent needed by child to unpickle process object
        '''
        from processing.logger import _logger
        
        if _logger is not None:
            log_args = (_logger.getEffectiveLevel(),) + _logger._extra_args
        else:
            log_args = None

        if sys.argv[0] not in ('', '-c') and not WINEXE:
            mainpath = getattr(sys.modules['__main__'], '__file__', None)
            if mainpath is not None and not os.path.isabs(mainpath):
                # we will assume os.chdir() was not used between program
                # start up and the first import of processing
                mainpath = os.path.join(processing.ORIGINAL_DIR, mainpath)
        else:
            mainpath = None
        return [name, mainpath, sys.path, sys.argv,
                processing.currentProcess().getAuthKey(),
                None, processing.ORIGINAL_DIR, log_args]


    def prepare(name, mainpath, sys_path, sys_argv, authkey,
                cur_dir, orig_dir, log_args):
        '''
        Try to get this process ready to unpickle process object
        '''
        global original_main_module

        original_main_module = sys.modules['__main__']
        processing.currentProcess().setName(name)
        processing.currentProcess().setAuthKey(authkey)

        if log_args is not None:
            from processing.logger import enableLogging
            enableLogging(*log_args)

        if orig_dir is not None:
            processing.ORIGINAL_DIR = orig_dir

        if cur_dir is not None:
            try:
                os.chdir(cur_dir)
            except OSError:
                raise

        if sys_path is not None:
            sys.path = sys_path

        if mainpath is not None:
            mainname = splitext(basename(mainpath))[0]
            if mainname == '__init__':
                mainname = basename(dirname(mainpath))

            if not mainpath.lower().endswith('.exe') and mainname != 'ipython':
                if mainpath is None:
                    dirs = None
                elif basename(mainpath).startswith('__init__.py'):
                    dirs = [dirname(dirname(mainpath))]
                else:
                    dirs = [dirname(mainpath)]

                assert mainname not in sys.modules, mainname
                file, pathname, etc = imp.find_module(mainname, dirs)
                try:
                    # We would like to do "imp.load_module('__main__', ...)"
                    # here.  However, that would cause 'if __name__ ==
                    # "__main__"' clauses to be executed.
                    main_module = imp.load_module(
                        '__parents_main__', file, pathname, etc
                        )
                finally:
                    if file:
                        file.close()

                sys.modules['__main__'] = main_module
                main_module.__name__ = '__main__'

                # XXX Try to make the potentially picklable objects in
                # sys.modules['__main__'] realize they are in the main
                # module -- ugly
                for obj in main_module.__dict__.values():
                    try:
                        if obj.__module__ == '__parents_main__':
                            obj.__module__ = '__main__'
                    except (KeyboardInterrupt, SystemExit):
                        raise
                    except:
                        pass

        if sys_argv is not None:            # this needs to come last 
            sys.argv = sys_argv

    def main():
        '''
        Run code specifed by data received over pipe
        '''
        assert isForking(sys.argv)

        handle = int(sys.argv[-1])
        fd = msvcrt.open_osfhandle(handle, os.O_RDONLY)
        from_parent = os.fdopen(fd, 'rb')

        processing.currentProcess()._inheriting = True    
        preparation_data = load(from_parent)
        prepare(*preparation_data)
        self = load(from_parent)
        processing.currentProcess()._inheriting = False

        from_parent.close()

        exitcode = self._bootstrap()
        win32.ExitProcess(exitcode)
