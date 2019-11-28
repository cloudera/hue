#!/bin/bash

# Parse command line
VERBOSE=0
HELP=0
ERR=0
NOINPUT=""
while [[ $# > 0 ]]
do
    key="$1"
    case $key in
        -h|--help)
            HELP=1
            ;;
        -v|--verbose)
            VERBOSE=1
            ;;
        --noinput)
            NOINPUT="--noinput"
            ;;
        *)
            echo "Unknown option '$key'"
            ERR=1
            HELP=1
            ;;
    esac
    shift
done

if [ $HELP -eq 1 ]
then
    echo "$0 [-vh] - Run django-nose integration tests."
    echo " -v/--verbose - Print output of test commands."
    echo " -h/--help    - Print this help message."
    exit $ERR
fi

export PYTHONPATH=.

HAS_HOTSHOT=$(python -c "\
try:
  import hotshot
except ImportError:
  print('0')
else:
  print('1')
")

reset_env() {
    unset TEST_RUNNER
    unset NOSE_PLUGINS
    unset REUSE_DB
}

echo_output() {
    STDOUT=$1
    STDERR=$2
    if [ $VERBOSE -ne 1 ]
    then
        echo "stdout"
        echo "======"
        cat $STDOUT
        echo
        echo "stderr"
        echo "======"
        cat $STDERR
    fi
    rm $STDOUT $STDERR
}

django_test() {
    COMMAND=$1
    TEST_COUNT=$2
    DESCRIPTION=$3
    CAN_FAIL=${4:-0}

    if [ $VERBOSE -eq 1 ]
    then
        echo "================"
        echo "Django settings:"
        ./manage.py diffsettings
        echo "================"
    fi

    if [ -n "$COVERAGE" ]
    then
        TEST="coverage run -p $COMMAND"
    else
        TEST="$COMMAND"
    fi
    # Temp files on Linux / OSX
    TMP_OUT=`mktemp 2>/dev/null || mktemp -t 'django-nose-runtests'`
    TMP_ERR=`mktemp 2>/dev/null || mktemp -t 'django-nose-runtests'`
    RETURN=0
    if [ $VERBOSE -eq 1 ]
    then
        echo $TEST
        $TEST > >(tee $TMP_OUT) 2> >(tee $TMP_ERR >&2)
    else
        $TEST >$TMP_OUT 2>$TMP_ERR
    fi
    if [ $? -gt 0 ]
    then
        echo "FAIL (test failure): $DESCRIPTION"
        echo_output $TMP_OUT $TMP_ERR
        if [ "$CAN_FAIL" == "0" ]
        then
            exit 1
        else
            return
        fi
    fi
    OUTPUT=`cat $TMP_OUT $TMP_ERR`
    echo $OUTPUT | grep "Ran $TEST_COUNT test" > /dev/null
    if [ $? -gt 0 ]
    then
        echo "FAIL (count!=$TEST_COUNT): $DESCRIPTION"
        echo_output $TMP_OUT $TMP_ERR
        if [ "$CAN_FAIL" == "0" ]
        then
            exit 1
        else
            return
        fi
    else
        echo "PASS (count==$TEST_COUNT): $DESCRIPTION"
    fi
    rm $TMP_OUT $TMP_ERR

    # Check that we're hijacking the help correctly.
    $TEST --help 2>&1 | grep 'NOSE_DETAILED_ERRORS' > /dev/null
    if [ $? -gt 0 ]
    then
        echo "FAIL (--help): $DESCRIPTION"
        if [ "$CAN_FAIL" == 0 ]
        then
            exit 1;
        else
            return
        fi
    else
        echo "PASS (  --help): $DESCRIPTION"
    fi
}

TESTAPP_COUNT=6

reset_env
django_test "./manage.py test $NOINPUT" $TESTAPP_COUNT 'normal settings'

reset_env
export TEST_RUNNER="django_nose.NoseTestSuiteRunner"
django_test "./manage.py test $NOINPUT" $TESTAPP_COUNT 'test runner from environment'

reset_env
django_test "testapp/runtests.py testapp.test_only_this" 1 'via run_tests API'

reset_env
export NOSE_PLUGINS="testapp.plugins.SanityCheckPlugin"
django_test "./manage.py test testapp/plugin_t $NOINPUT" 1 'with plugins'

reset_env
django_test "./manage.py test unittests $NOINPUT" 4 'unittests'

reset_env
django_test "./manage.py test unittests --verbosity 1 $NOINPUT" 4 'argument option without equals'

reset_env
django_test "./manage.py test unittests --nose-verbosity=2 $NOINPUT" 4 'argument with equals'

reset_env
django_test "./manage.py test unittests --testrunner=testapp.custom_runner.CustomNoseTestSuiteRunner $NOINPUT" 4 'unittests with testrunner'

reset_env
django_test "./manage.py test unittests --attr special $NOINPUT" 1 'select by attribute'

reset_env
export REUSE_DB=1
# For the many issues with REUSE_DB=1, see:
# https://github.com/django-nose/django-nose/milestones/Fix%20REUSE_DB=1
django_test "./manage.py test $NOINPUT" $TESTAPP_COUNT 'with REUSE_DB=1, call #1' 'can fail'
django_test "./manage.py test $NOINPUT" $TESTAPP_COUNT 'with REUSE_DB=1, call #2' 'can fail'


if [ "$HAS_HOTSHOT" = "1" ]
then
    # Python 3 doesn't support the hotshot profiler. See nose#842.
    reset_env
    django_test "./manage.py test $NOINPUT --with-profile --profile-restrict less_output" $TESTAPP_COUNT 'with profile plugin'
fi
