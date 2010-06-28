# coding: utf-8
import os
import shutil
import tarfile
import tempfile
import time
from beaker.middleware import CacheMiddleware
from beaker.cache import Cache
from webtest import TestApp

# Tarballs of the output of:
# >>> from beaker.cache import Cache
# >>> c = Cache('test', data_dir='db', type='dbm')
# >>> c['foo'] = 'bar'
# in the old format, Beaker @ revision: 24f57102d310
dbm_cache_tar = """\
eJzt3EtOwkAAgOEBjTHEBDfu2ekKZ6bTTnsBL+ABzPRB4osSRBMXHsNruXDl3nMYLaEbpYRAaIn6
f8kwhFcn/APLSeNTUTdZsL4/m4Pg21wSqiCt9D1PC6mUZ7Xo+bWvrHB/N3HjXk+MrrLhQ/a48HXL
nv+l0vg0yYcTdznMxhdpfFvHbpj1lyv0N8oq+jdhrr/b/A5Yo79R9G9ERX8XbXgLrNHfav7/G1Hd
30XGhYPMT5JYRbELVGISGVov9SKVRaGNQj2I49TrF+8oxpJrTAMHxizob+b7ay+Y/v5lE1/AP+8v
9o5ccdsWYvdViMPpIwdCtMRsiP3yTrucd8r5pJxbz8On9/KT2uVo3H5rG1cFAAAAAOD3aIuP7lv3
pRjbXgkAAAAAAFjVyc1Idc6U1lYGgbSmL0Mjpe248+PYjY87I91x/UGeb3udAAAAAACgfh+fAAAA
AADgr/t5/sPFTZ5cb/38D19Lzn9pRHX/zR4CtEZ/o+nfiEX9N3kI0Gr9vWl/W0z0BwAAAAAAAAAA
AAAAAAAAqPAFyOvcKA==
""".decode('base64').decode('zlib')

# dumbdbm format
dumbdbm_cache_tar = """\
eJzt191qgzAYBmCPvYqc2UGx+ZKY6A3scCe7gJKoha6binOD3f2yn5Ouf3TTlNH3AQlEJcE3nyGV
W0RT457Jsq9W6632W0Se0JI49/1E0vCIZZPPzHt5HmzPWNQ91M1r/XbwuVP3/6nKLcq2Gey6qftl
5Z6mWA3n56/IKOQfwk7+dvwV8Iv8FSH/IPbkb4uRl8BZ+fvg/WUE8g9if/62UDZf1VlZOiqc1VSq
kudGVrKgushNkYuVc5VM/Rups5vjY3wErJU6nD+Z7fyFNFpEjIf4AFeef7Jq22TOZnzOpLiJLz0d
CGyE+q/scHyMk/Wv+E79G0L9hzC7JSFMpv0PN0+J4rv7xNk+iTuKh07E6aXnB9Mao/7X/fExzt//
FecS9R8C9v/r9rP+l49tubnk+e/z/J8JjvMfAAAAAAAAAADAn70DFJAAwQ==
""".decode('base64').decode('zlib')

def simple_app(environ, start_response):
    clear = False
    if environ.get('beaker.clear'):
        clear = True
    cache = environ['beaker.cache'].get_cache('testcache')
    if clear:
        cache.clear()
    try:
        value = cache.get_value('value')
    except:
        value = 0
    cache.set_value('value', value+1)
    start_response('200 OK', [('Content-type', 'text/plain')])
    return ['The current value is: %s' % cache.get_value('value')]

def cache_manager_app(environ, start_response):
    cm = environ['beaker.cache']
    cm.get_cache('test')['test_key'] = 'test value'

    start_response('200 OK', [('Content-type', 'text/plain')])
    yield "test_key is: %s\n" % cm.get_cache('test')['test_key']
    cm.get_cache('test').clear()

    try:
        test_value = cm.get_cache('test')['test_key']
    except KeyError:
        yield "test_key cleared"
    else:
        yield "test_key wasn't cleared, is: %s\n" % \
            cm.get_cache('test')['test_key']

def test_has_key():
    cache = Cache('test', data_dir='./cache', type='dbm')
    o = object()
    cache.set_value("test", o)
    assert cache.has_key("test")
    assert "test" in cache
    assert not cache.has_key("foo")
    assert "foo" not in cache
    cache.remove_value("test")
    assert not cache.has_key("test")

def test_expire_changes():
    cache = Cache('test_bar', data_dir='./cache', type='dbm')
    cache.set_value('test', 10)
    assert cache.has_key('test')
    assert cache['test'] == 10
    
    # ensure that we can change a never-expiring value
    cache.set_value('test', 20, expiretime=1)
    assert cache.has_key('test')
    assert cache['test'] == 20
    time.sleep(1)
    assert not cache.has_key('test')
    
    # test that we can change it before its expired
    cache.set_value('test', 30, expiretime=50)
    assert cache.has_key('test')
    assert cache['test'] == 30
    
    cache.set_value('test', 40, expiretime=3)
    assert cache.has_key('test')
    assert cache['test'] == 40
    time.sleep(3)
    assert not cache.has_key('test')

def test_fresh_createfunc():
    cache = Cache('test_foo', data_dir='./cache', type='dbm')
    x = cache.get_value('test', createfunc=lambda: 10, expiretime=2)
    assert x == 10
    x = cache.get_value('test', createfunc=lambda: 12, expiretime=2)
    assert x == 10
    x = cache.get_value('test', createfunc=lambda: 14, expiretime=2)
    assert x == 10
    time.sleep(2)
    x = cache.get_value('test', createfunc=lambda: 16, expiretime=2)
    assert x == 16
    x = cache.get_value('test', createfunc=lambda: 18, expiretime=2)
    assert x == 16
    
    cache.remove_value('test')
    assert not cache.has_key('test')
    x = cache.get_value('test', createfunc=lambda: 20, expiretime=2)
    assert x == 20
    
    
    
def test_has_key_multicache():
    cache = Cache('test', data_dir='./cache', type='dbm')
    o = object()
    cache.set_value("test", o)
    assert cache.has_key("test")
    assert "test" in cache
    cache = Cache('test', data_dir='./cache', type='dbm')
    assert cache.has_key("test")

def test_unicode_keys():    
    cache = Cache('test', data_dir='./cache', type='dbm')
    o = object()
    cache.set_value(u'hiŏ', o)
    assert u'hiŏ' in cache
    assert u'hŏa' not in cache
    cache.remove_value(u'hiŏ')
    assert u'hiŏ' not in cache

def test_multi_keys():
    cache = Cache('newtests', data_dir='./cache', type='dbm')
    cache.clear()
    called = {}
    def create_func():
        called['here'] = True
        return 'howdy'
    
    try:
        cache.get_value('key1')
    except KeyError:
        pass
    else:
        raise Exception("Failed to keyerror on nonexistent key")

    assert 'howdy' == cache.get_value('key2', createfunc=create_func)
    assert called['here'] == True
    del called['here']

    try:
        cache.get_value('key3')
    except KeyError:
        pass
    else:
        raise Exception("Failed to keyerror on nonexistent key")
    try:
        cache.get_value('key1')
    except KeyError:
        pass
    else:
        raise Exception("Failed to keyerror on nonexistent key")
    
    assert 'howdy' == cache.get_value('key2', createfunc=create_func)
    assert called == {}

def test_increment():
    app = TestApp(CacheMiddleware(simple_app))
    res = app.get('/', extra_environ={'beaker.type':type, 'beaker.clear':True})
    assert 'current value is: 1' in res
    res = app.get('/')
    assert 'current value is: 2' in res
    res = app.get('/')
    assert 'current value is: 3' in res

def test_cache_manager():
    app = TestApp(CacheMiddleware(cache_manager_app))
    res = app.get('/')
    assert 'test_key is: test value' in res
    assert 'test_key cleared' in res
    
def test_legacy_cache():
    cache = Cache('newtests', data_dir='./cache', type='dbm')
    
    cache.set_value('x', '1')
    assert cache.get_value('x') == '1'
    
    cache.set_value('x', '2', type='file', data_dir='./cache')
    assert cache.get_value('x') == '1'
    assert cache.get_value('x', type='file', data_dir='./cache') == '2'
    
    cache.remove_value('x')
    cache.remove_value('x', type='file', data_dir='./cache')
    
    assert cache.get_value('x', expiretime=1, createfunc=lambda: '5') == '5'
    assert cache.get_value('x', expiretime=1, createfunc=lambda: '6', type='file', data_dir='./cache') == '6'
    assert cache.get_value('x', expiretime=1, createfunc=lambda: '7') == '5'
    assert cache.get_value('x', expiretime=1, createfunc=lambda: '8', type='file', data_dir='./cache') == '6'
    time.sleep(1)
    assert cache.get_value('x', expiretime=1, createfunc=lambda: '9') == '9'
    assert cache.get_value('x', expiretime=1, createfunc=lambda: '10', type='file', data_dir='./cache') == '10'
    assert cache.get_value('x', expiretime=1, createfunc=lambda: '11') == '9'
    assert cache.get_value('x', expiretime=1, createfunc=lambda: '12', type='file', data_dir='./cache') == '10'
    

def test_upgrade():
    for test in _test_upgrade_has_key, _test_upgrade_in, _test_upgrade_setitem:
        for mod, tar in (('dbm', dbm_cache_tar),
                         ('dumbdbm', dumbdbm_cache_tar)):
            try:
                __import__(mod)
            except ImportError:
                continue
            dir = tempfile.mkdtemp()
            fd, name = tempfile.mkstemp(dir=dir)
            fp = os.fdopen(fd, 'w')
            fp.write(tar)
            fp.close()
            tar = tarfile.open(name)
            for member in tar.getmembers():
                tar.extract(member, dir)
            tar.close()
            try:
                test(os.path.join(dir, 'db'))
            finally:
                shutil.rmtree(dir)

def _test_upgrade_has_key(dir):
    cache = Cache('test', data_dir=dir, type='dbm')
    assert cache.has_key('foo')
    assert cache.has_key('foo')

def _test_upgrade_in(dir):
    cache = Cache('test', data_dir=dir, type='dbm')
    assert 'foo' in cache
    assert 'foo' in cache

def _test_upgrade_setitem(dir):
    cache = Cache('test', data_dir=dir, type='dbm')
    assert cache['foo'] == 'bar'
    assert cache['foo'] == 'bar'
