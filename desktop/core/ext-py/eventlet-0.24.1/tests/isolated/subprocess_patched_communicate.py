__test__ = False

if __name__ == '__main__':
    import sys
    import eventlet
    import subprocess
    eventlet.monkey_patch(all=True)
    p = subprocess.Popen([sys.executable], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.communicate()

    print('pass')
