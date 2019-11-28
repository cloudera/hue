#!/bin/sh
#
# This script runs all the t_*.py tests in the current directory,
# preparing PYTHONPATH to use the most recent local build
#
# Run with -v option for verbose
#

set -e
: ${PYTHON:="python"}
plat_specifier=`$PYTHON -c 'import sys,distutils.util; \
        print(distutils.util.get_platform()+"-"+sys.version[0:3])'`
failed=
for test in t_*.py;  do
    echo "$test:"
    PYTHONPATH="../build/lib.$plat_specifier" $PYTHON "$test" "$@" || 
        failed="$failed $test"
done

if test -n "$failed"; then
   echo "Tests that failed:$failed" >&2
   exit 1
else
   echo "All tests passed. Yay."
   exit 0
fi
