#!/bin/sh
# run all tests that are availabe in sp_test
/usr/bin/env python ./tt_config.py > tt_config.json
mkdir -p log
sp_testdrv.py -l | ./filter_testcase_ids.py | sort | ./run_list_of_tests.py
