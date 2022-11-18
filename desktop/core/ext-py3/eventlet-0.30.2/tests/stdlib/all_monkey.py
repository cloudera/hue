import eventlet
eventlet.sleep(0)
from eventlet import patcher
patcher.monkey_patch()


def assimilate_real(name):
    print("Assimilating", name)
    try:
        modobj = __import__('test.' + name, globals(), locals(), ['test_main'])
    except ImportError:
        print("Not importing %s, it doesn't exist in this installation/version of Python" % name)
        return
    else:
        method_name = name + "_test_main"
        try:
            globals()[method_name] = modobj.test_main
            modobj.test_main.__name__ = name + '.test_main'
        except AttributeError:
            print("No test_main for %s, assuming it tests on import" % name)

import all_modules

for m in all_modules.get_modules():
    assimilate_real(m)
