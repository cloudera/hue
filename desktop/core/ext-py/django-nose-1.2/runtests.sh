#!/bin/sh

export PYTHONPATH=.

django_test() {
    TEST="$1"
    $TEST 2>&1 | grep "Ran $2 test" > /dev/null
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
django_test 'django-admin.py test --settings=testapp.settings_with_south' '2' 'with south in installed apps'
django_test 'django-admin.py test --settings=testapp.settings_old_style' '2' 'django_nose.run_tests format'
django_test 'testapp/runtests.py testapp.test_only_this' '1' 'via run_tests API'
django_test 'django-admin.py test --settings=testapp.settings_with_plugins testapp/plugin_t' '1' 'with plugins'
django_test 'django-admin.py test --settings=testapp.settings unittests' '4' 'unittests'
