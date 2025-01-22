#!/usr/bin/env python

import fileinput
from subprocess import call


for line in fileinput.input():
    cmd = f"./run_oper.sh {line.rstrip()}"
    print(f"executing {cmd}")
    call(cmd, shell=True)
