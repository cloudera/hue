#!/usr/bin/env python
# extract test case IDs from json-formatted list (`sp_testdrv.py -l` or `idp_testdrv.py -l`)
# usage:
#  sp_testdrv.py -l | filter_testcase_ids.py
__author__ = 'rhoerbe'

import json, sys
jdata = json.load(sys.stdin)
for k in jdata:
    print(k["id"])
