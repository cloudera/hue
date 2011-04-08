import os
import sys
from tests.patcher_test import ProcessBase
from tests import skip_with_pyevent
from eventlet.green import subprocess

class Subprocess(ProcessBase):
    def test_longoutput(self):
        new_mod = """
import time
for i in xrange(2):
    print "*" * 10000,
    time.sleep(0.2)
"""
        modname = "newmod"
        filename = modname + ".py"
        self.write_to_tempfile(modname, new_mod)
        python_path = os.pathsep.join(sys.path + [self.tempdir])
        new_env = os.environ.copy()
        new_env['PYTHONPATH'] = python_path
        p = subprocess.Popen([sys.executable, 
                              os.path.join(self.tempdir, filename)],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=new_env)
        output, _ = p.communicate()
        self.assertEqual(output, "*"*10000 + " " + "*"*10000 + "\n")
