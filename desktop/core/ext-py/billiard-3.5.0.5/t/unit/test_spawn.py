from __future__ import absolute_import

from billiard import get_context

class test_spawn:
    def test_start(self):
        ctx = get_context('spawn')

        p = ctx.Process(target=task_from_process, args=('opa',))
        p.start()
        p.join()
        return p.exitcode

def task_from_process(name):
    print('proc:', name)

