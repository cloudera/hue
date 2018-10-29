#!/usr/bin/env python

import fileinput
from subprocess import call

for line in fileinput.input():
    cmd = "./run_oper.sh " + line.rstrip()
    print("executing " + cmd)
    call(cmd, shell=True)

