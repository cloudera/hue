from beaker.synchronization import *

# TODO: spawn threads, test locking.


def test_reentrant_file():
    sync1 = file_synchronizer('test', lock_dir='./')
    sync2 = file_synchronizer('test', lock_dir='./')
    sync1.acquire_write_lock()
    sync2.acquire_write_lock()
    sync2.release_write_lock()
    sync1.release_write_lock()

def test_null():
    sync = null_synchronizer()
    assert sync.acquire_write_lock()
    sync.release_write_lock()
    
def test_mutex():
    sync = mutex_synchronizer('someident')
    sync.acquire_write_lock()
    sync.release_write_lock()
        
