#!/bin/bash

export PYTHONPATH=.

PYTHONVERSION=$(python --version 2>&1)
PYTHONVERSION=${PYTHONVERSION##Python }

function version { echo $@ | gawk -F. '{ printf("%d.%d.%d\n", $1,$2,$3); }'; }

django_test() {
    TEST="$1"
    OUTPUT=$($TEST 2>&1)
    if [ $? -gt 0 ]
    then
        echo FAIL: $3
        $TEST
        exit 1;
    fi
    echo $OUTPUT | grep "Ran $2 test" > /dev/null
    if [ $? -gt 0 ]
    then
        echo FAIL: $3
        $TEST
        exit 1;
    else
        echo PASS: $3
    fi

    # Check that we're hijacking the help correctly.
    $TEST --help 2>&1 | grep 'NOSE_DETAILED_ERRORS' > /dev/null
    if [ $? -gt 0 ]
    then
        echo FAIL: $3 '(--help)'
        exit 1;
    else
        echo PASS: $3 '(--help)'
    fi
}

django_test 'django-admin.py test --settings=testapp.settings' '2' 'normal settings'
if [ "$DJANGO" = "Django==1.4.1" -o "$DJANGO" = "Django==1.5" -o "$DJANGO" = "Django==1.6" ]
then
    django_test 'django-admin.py test --settings=testapp.settings_with_south' '2' 'with south in installed apps'
fi

django_test 'django-admin.py test --settings=testapp.settings_old_style' '2' 'django_nose.run_tests format'
django_test 'testapp/runtests.py testapp.test_only_this' '1' 'via run_tests API'
django_test 'django-admin.py test --settings=testapp.settings_with_plugins testapp/plugin_t' '1' 'with plugins'
django_test 'django-admin.py test --settings=testapp.settings unittests' '4' 'unittests'
if ! [ $(version $PYTHONVERSION) \> $(version 3.0.0) ]
then
# Python 3 doesn't support the hotshot profiler. See nose#842.
django_test 'django-admin.py test --settings=testapp.settings --with-profile' '2' 'with profile plugin'
fi
