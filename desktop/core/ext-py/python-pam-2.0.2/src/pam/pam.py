# Now owned and maintained by David Ford, <david.ford@blue-labs.org>
#
# (c) 2007 Chris AtLee <chris@atlee.ca>
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php
#
# Original author: Chris AtLee
#
# Modified by David Ford, 2011-12-6
# added py3 support and encoding
# added pam_end
# added pam_setcred to reset credentials after seeing Leon Walker's remarks
# added byref as well
# use readline to prestuff the getuser input
#
# Modified by Laurie Reeves, 2020-02-14
# added opening and closing the pam session
# added setting and reading the pam environment variables
# added setting the "misc" pam environment
# added saving the messages passed back in the conversation function

'''
PAM module for python

This is a legacy file, it is not used. Here for example.

Provides an authenticate function that will allow the caller to authenticate
a user against the Pluggable Authentication Modules (PAM) on the system.

Implemented using ctypes, so no compilation is necessary.
'''

import six
import __internals

if __name__ == "__main__":  # pragma: no cover
    import readline
    import getpass

    def input_with_prefill(prompt, text):
        def hook():
            readline.insert_text(text)
            readline.redisplay()

        readline.set_pre_input_hook(hook)
        result = six.moves.input(prompt)  # nosec (bandit; python2)

        readline.set_pre_input_hook()

        return result

    __pam = __internals.PamAuthenticator()

    username = input_with_prefill('Username: ', getpass.getuser())

    # enter a valid username and an invalid/valid password, to verify both
    # failure and success
    result = __pam.authenticate(username, getpass.getpass(),
                                env={"XDG_SEAT": "seat0"},
                                call_end=False)
    print('Auth result: {} ({})'.format(__pam.reason, __pam.code))

    env_list = __pam.getenvlist()
    for key, value in env_list.items():
        print("Pam Environment List item: {}={}".format(key, value))

    key = "XDG_SEAT"
    value = __pam.getenv(key)
    print("Pam Environment item: {}={}".format(key, value))

    if __pam.code == __internals.PAM_SUCCESS:
        result = __pam.open_session()
        print('Open session: {} ({})'.format(__pam.reason, __pam.code))

        if __pam.code == __internals.PAM_SUCCESS:
            result = __pam.close_session()
            print('Close session: {} ({})'.format(__pam.reason, __pam.code))

        else:
            __pam.end()
    else:
        __pam.end()
