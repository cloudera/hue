import os
import six
import sys
from ctypes import cdll
from ctypes import CFUNCTYPE
from ctypes import CDLL
from ctypes import POINTER
from ctypes import Structure
from ctypes import byref
from ctypes import cast
from ctypes import sizeof
from ctypes import py_object
from ctypes import c_char
from ctypes import c_char_p
from ctypes import c_int
from ctypes import c_size_t
from ctypes import c_void_p
from ctypes import memmove
from ctypes.util import find_library
from typing import Union

PAM_ABORT = 26
PAM_ACCT_EXPIRED = 13
PAM_AUTHINFO_UNAVAIL = 9
PAM_AUTHTOK_DISABLE_AGING = 23
PAM_AUTHTOK_ERR = 20
PAM_AUTHTOK_EXPIRED = 27
PAM_AUTHTOK_LOCK_BUSY = 22
PAM_AUTHTOK_RECOVER_ERR = 21
PAM_AUTH_ERR = 7
PAM_BAD_ITEM = 29
PAM_BUF_ERR = 5
PAM_CHANGE_EXPIRED_AUTHTOK = 32
PAM_CONV = 5
PAM_CONV_ERR = 19
PAM_CRED_ERR = 17
PAM_CRED_EXPIRED = 16
PAM_CRED_INSUFFICIENT = 8
PAM_CRED_UNAVAIL = 15
PAM_DATA_SILENT = 1073741824
PAM_DELETE_CRED = 4
PAM_DISALLOW_NULL_AUTHTOK = 1
PAM_ERROR_MSG = 3
PAM_ESTABLISH_CRED = 2
PAM_IGNORE = 25
PAM_MAXTRIES = 11
PAM_MODULE_UNKNOWN = 28
PAM_NEW_AUTHTOK_REQD = 12
PAM_NO_MODULE_DATA = 18
PAM_OPEN_ERR = 1
PAM_PERM_DENIED = 6
PAM_PROMPT_ECHO_OFF = 1
PAM_PROMPT_ECHO_ON = 2
PAM_REFRESH_CRED = 16
PAM_REINITIALIZE_CRED = 8
PAM_RHOST = 4
PAM_RUSER = 8
PAM_SERVICE = 1
PAM_SERVICE_ERR = 3
PAM_SESSION_ERR = 14
PAM_SILENT = 32768
PAM_SUCCESS = 0
PAM_SYMBOL_ERR = 2
PAM_SYSTEM_ERR = 4
PAM_TEXT_INFO = 4
PAM_TRY_AGAIN = 24
PAM_TTY = 3
PAM_USER = 2
PAM_USER_PROMPT = 9
PAM_USER_UNKNOWN = 10
PAM_XDISPLAY = 11


__all__ = ('PAM_ABORT', 'PAM_ACCT_EXPIRED', 'PAM_AUTHINFO_UNAVAIL',
           'PAM_AUTHTOK_DISABLE_AGING', 'PAM_AUTHTOK_ERR',
           'PAM_AUTHTOK_EXPIRED', 'PAM_AUTHTOK_LOCK_BUSY',
           'PAM_AUTHTOK_RECOVER_ERR', 'PAM_AUTH_ERR', 'PAM_BAD_ITEM',
           'PAM_BUF_ERR', 'PAM_CHANGE_EXPIRED_AUTHTOK', 'PAM_CONV',
           'PAM_CONV_ERR', 'PAM_CRED_ERR', 'PAM_CRED_EXPIRED',
           'PAM_CRED_INSUFFICIENT', 'PAM_CRED_UNAVAIL', 'PAM_DATA_SILENT',
           'PAM_DELETE_CRED', 'PAM_DISALLOW_NULL_AUTHTOK', 'PAM_ERROR_MSG',
           'PAM_ESTABLISH_CRED', 'PAM_IGNORE', 'PAM_MAXTRIES',
           'PAM_MODULE_UNKNOWN', 'PAM_NEW_AUTHTOK_REQD', 'PAM_NO_MODULE_DATA',
           'PAM_OPEN_ERR', 'PAM_PERM_DENIED', 'PAM_PROMPT_ECHO_OFF',
           'PAM_PROMPT_ECHO_ON', 'PAM_REFRESH_CRED', 'PAM_REINITIALIZE_CRED',
           'PAM_RHOST', 'PAM_RUSER', 'PAM_SERVICE', 'PAM_SERVICE_ERR',
           'PAM_SESSION_ERR', 'PAM_SILENT', 'PAM_SUCCESS', 'PAM_SYMBOL_ERR',
           'PAM_SYSTEM_ERR', 'PAM_TEXT_INFO', 'PAM_TRY_AGAIN', 'PAM_TTY',
           'PAM_USER', 'PAM_USER_PROMPT', 'PAM_USER_UNKNOWN',
           'PamAuthenticator')


class PamHandle(Structure):
    """wrapper class for pam_handle_t pointer"""
    _fields_ = [("handle", c_void_p)]

    def __init__(self):
        super().__init__()
        self.handle = 0

    def __repr__(self):
        return f"<PamHandle {self.handle}>"


class PamMessage(Structure):
    """wrapper class for pam_message structure"""
    _fields_ = [("msg_style", c_int), ("msg", c_char_p)]

    def __repr__(self):
        return "<PamMessage style: %i, content: %s >" % (self.msg_style, self.msg)


class PamResponse(Structure):
    """wrapper class for pam_response structure"""
    _fields_ = [("resp", c_char_p), ("resp_retcode", c_int)]

    def __repr__(self):
        return "<PamResponse code: %i, content: %s >" % (self.resp_retcode, self.resp)


conv_func = CFUNCTYPE(c_int,
                      c_int,
                      POINTER(POINTER(PamMessage)),
                      POINTER(POINTER(PamResponse)),
                      c_void_p)


def my_conv(n_messages, messages, p_response, libc, msg_list: list, password: bytes, encoding: str):
    """Simple conversation function that responds to any
       prompt where the echo is off with the supplied password"""
    # Create an array of n_messages response objects
    calloc = libc.calloc
    calloc.restype = c_void_p
    calloc.argtypes = [c_size_t, c_size_t]

    cpassword = c_char_p(password)

    '''
    PAM_PROMPT_ECHO_OFF = 1
    PAM_PROMPT_ECHO_ON = 2
    PAM_ERROR_MSG = 3
    PAM_TEXT_INFO = 4
    '''

    addr = calloc(n_messages, sizeof(PamResponse))
    response = cast(addr, POINTER(PamResponse))
    p_response[0] = response

    for i in range(n_messages):
        message = messages[i].contents.msg
        if sys.version_info >= (3,):  # pragma: no branch
            message = message.decode(encoding)

        msg_list.append(message)

        if messages[i].contents.msg_style == PAM_PROMPT_ECHO_OFF:
            if i == 0:
                dst = calloc(len(password)+1, sizeof(c_char))
                memmove(dst, cpassword, len(password))
                response[i].resp = dst
            else:
                # void out the message
                response[i].resp = None

            response[i].resp_retcode = 0

    return PAM_SUCCESS


class PamConv(Structure):
    """wrapper class for pam_conv structure"""
    _fields_ = [("conv", conv_func), ("appdata_ptr", c_void_p)]


class PamAuthenticator:
    code = 0
    reason = None  # type: Union[str, bytes, None]

    def __init__(self):
        # use a trick of dlopen(), this effectively becomes
        # dlopen("", ...) which opens our own executable. since 'python' has
        # a libc dependency, this means libc symbols are already available
        # to us

        # libc = CDLL(find_library("c"))
        libc = cdll.LoadLibrary(None)
        self.libc = libc

        libpam = CDLL(find_library("pam"))
        libpam_misc = CDLL(find_library("pam_misc"))

        self.handle = None
        self.messages = []

        self.calloc = libc.calloc
        self.calloc.restype = c_void_p
        self.calloc.argtypes = [c_size_t, c_size_t]

        # bug #6 (@NIPE-SYSTEMS), some libpam versions don't include this
        # function
        if hasattr(libpam, 'pam_end'):  # pragma: no branch
            self.pam_end = libpam.pam_end
            self.pam_end.restype = c_int
            self.pam_end.argtypes = [PamHandle, c_int]

        self.pam_start = libpam.pam_start
        self.pam_start.restype = c_int
        self.pam_start.argtypes = [c_char_p, c_char_p, POINTER(PamConv),
                                   POINTER(PamHandle)]

        self.pam_acct_mgmt = libpam.pam_acct_mgmt
        self.pam_acct_mgmt.restype = c_int
        self.pam_acct_mgmt.argtypes = [PamHandle, c_int]

        self.pam_set_item = libpam.pam_set_item
        self.pam_set_item.restype = c_int
        self.pam_set_item.argtypes = [PamHandle, c_int, c_void_p]

        self.pam_setcred = libpam.pam_setcred
        self.pam_strerror = libpam.pam_strerror
        self.pam_strerror.restype = c_char_p
        self.pam_strerror.argtypes = [PamHandle, c_int]

        self.pam_authenticate = libpam.pam_authenticate
        self.pam_authenticate.restype = c_int
        self.pam_authenticate.argtypes = [PamHandle, c_int]

        self.pam_open_session = libpam.pam_open_session
        self.pam_open_session.restype = c_int
        self.pam_open_session.argtypes = [PamHandle, c_int]

        self.pam_close_session = libpam.pam_close_session
        self.pam_close_session.restype = c_int
        self.pam_close_session.argtypes = [PamHandle, c_int]

        self.pam_putenv = libpam.pam_putenv
        self.pam_putenv.restype = c_int
        self.pam_putenv.argtypes = [PamHandle, c_char_p]

        if libpam_misc._name:  # pragma: no branch
            self.pam_misc_setenv = libpam_misc.pam_misc_setenv
            self.pam_misc_setenv.restype = c_int
            self.pam_misc_setenv.argtypes = [PamHandle, c_char_p, c_char_p,
                                             c_int]

        self.pam_getenv = libpam.pam_getenv
        self.pam_getenv.restype = c_char_p
        self.pam_getenv.argtypes = [PamHandle, c_char_p]

        self.pam_getenvlist = libpam.pam_getenvlist
        self.pam_getenvlist.restype = POINTER(c_char_p)
        self.pam_getenvlist.argtypes = [PamHandle]

    def authenticate(
                self,
                username,                       # type: Union[str, bytes]
                password,                       # type: Union[str, bytes]
                service='login',                # type: Union[str, bytes]
                env=None,                       # type: dict
                call_end=True,                  # type: bool
                encoding='utf-8',               # type: str
                resetcreds=True,                # type: bool
                print_failure_messages=False    # type: bool
                ):                              # type: (...) -> bool
        """username and password authentication for the given service.

        Returns True for success, or False for failure.

        self.code (integer) and self.reason (string) are always stored and may
        be referenced for the reason why authentication failed. 0/'Success'
        will be stored for success.

        Python3 expects bytes() for ctypes inputs.  This function will make
        necessary conversions using the supplied encoding.

        Args:
          username (str): username to authenticate
          password (str): password in plain text
          service (str):  PAM service to authenticate against, defaults to 'login'
          env (dict):      Pam environment variables
          call_end (bool): call the pam_end() function after (default true)
          print_failure_messages (bool): Print messages on failure

        Returns:
          success:  PAM_SUCCESS
          failure:  False
        """

        @conv_func
        def __conv(n_messages, messages, p_response, app_data):
            pyob = cast(app_data, py_object).value

            msg_list = pyob.get('msgs')
            password = pyob.get('password')
            encoding = pyob.get('encoding')

            return my_conv(n_messages, messages, p_response, self.libc, msg_list, password, encoding)

        if isinstance(username, six.text_type):
            username = username.encode(encoding)
        if isinstance(password, six.text_type):
            password = password.encode(encoding)
        if isinstance(service, six.text_type):
            service = service.encode(encoding)

        if b'\x00' in username or b'\x00' in password or b'\x00' in service:
            self.code = PAM_SYSTEM_ERR
            self.reason = ('none of username, password, or service may contain'
                           ' NUL')
            raise ValueError(self.reason)

        # do this up front so we can safely throw an exception if there's
        # anything wrong with it
        app_data = {'msgs': self.messages, 'password': password, 'encoding': encoding}
        conv = PamConv(__conv, c_void_p.from_buffer(py_object(app_data)))

        self.handle = PamHandle()
        retval = self.pam_start(service, username, byref(conv),
                                byref(self.handle))

        if retval != PAM_SUCCESS:  # pragma: no cover
            # This is not an authentication error, something has gone wrong
            # starting up PAM
            self.code = retval
            self.reason = ("pam_start() failed: %s" %
                           self.pam_strerror(self.handle, retval))
            return False

        # set the TTY, required when pam_securetty is used and the username
        # root is used note: this is only needed WHEN the pam_securetty.so
        # module is used; for checking /etc/securetty for allowing root
        # logins.  if your application doesn't use a TTY or your pam setup
        # doesn't involve pam_securetty for this auth path, don't worry
        # about it
        #
        # if your app isn't authenticating root with the right password, you
        # may not have the appropriate list of TTYs in /etc/securetty and/or
        # the correct configuration in /etc/pam.d/*
        #
        # if X $DISPLAY is set, use it - otherwise if we have a STDIN tty,
        # get it

        ctty = os.environ.get('DISPLAY')
        if not ctty and os.isatty(0):
            ctty = os.ttyname(0)

        # ctty can be invalid if no tty is being used
        if ctty:  # pragma: no branch (we don't test a void tty yet)
            ctty_p = c_char_p(ctty.encode(encoding))

            retval = self.pam_set_item(self.handle, PAM_TTY, ctty_p)
            retval = self.pam_set_item(self.handle, PAM_XDISPLAY, ctty_p)

        # Set the environment variables if they were supplied
        if env:
            if not isinstance(env, dict):
                raise TypeError('"env" must be a dict')

            for key, value in env.items():
                if isinstance(key, bytes) and b'\x00' in key:
                    raise ValueError('"env{}" key cannot contain NULLs')
                if isinstance(value, bytes) and b'\x00' in value:
                    raise ValueError('"env{}" value cannot contain NULLs')

                name_value = "{}={}".format(key, value)
                retval = self.putenv(name_value, encoding)

        auth_success = self.pam_authenticate(self.handle, 0)

        if auth_success == PAM_SUCCESS:
            auth_success = self.pam_acct_mgmt(self.handle, 0)

        if auth_success == PAM_SUCCESS and resetcreds:
            auth_success = self.pam_setcred(self.handle, PAM_REINITIALIZE_CRED)

        # store information to inform the caller why we failed
        self.code = auth_success
        self.reason = self.pam_strerror(self.handle, auth_success)

        if sys.version_info >= (3,):  # pragma: no branch (we don't test non-py3 versions)
            self.reason = self.reason.decode(encoding)  # type: ignore

        if call_end and hasattr(self, 'pam_end'):  # pragma: no branch
            self.pam_end(self.handle, auth_success)
            self.handle = None

        if print_failure_messages and self.code != PAM_SUCCESS:  # pragma: no cover
            print(f"Failure: {self.reason}")

        return auth_success == PAM_SUCCESS

    def end(self):
        """A direct call to pam_end()
        Returns:
          Linux-PAM return value as int
        """
        if not self.handle or not hasattr(self, 'pam_end'):
            return PAM_SYSTEM_ERR

        retval = self.pam_end(self.handle, self.code)
        self.handle = None

        return retval

    def open_session(self, encoding='utf-8'):
        """Call pam_open_session as required by the pam_api
        Returns:
          Linux-PAM return value as int
        """
        if not self.handle:
            return PAM_SYSTEM_ERR

        retval = self.pam_open_session(self.handle, 0)
        self.code = retval
        self.reason = self.pam_strerror(self.handle, retval)

        if sys.version_info >= (3,):  # pragma: no branch
            self.reason = self.reason.decode(encoding)

        return retval

    def close_session(self, encoding='utf-8'):
        """Call pam_close_session as required by the pam_api
        Returns:
          Linux-PAM return value as int
        """
        if not self.handle:
            return PAM_SYSTEM_ERR

        retval = self.pam_close_session(self.handle, 0)
        self.code = retval
        self.reason = self.pam_strerror(self.handle, retval)

        if sys.version_info >= (3,):  # pragma: no branch
            self.reason = self.reason.decode(encoding)

        return retval

    def misc_setenv(self, name, value, readonly, encoding='utf-8'):
        """A wrapper for the pam_misc_setenv function
        Args:
          name: key name of the environment variable
          value: the value of the environment variable
        Returns:
          Linux-PAM return value as int
        """
        if not self.handle or not hasattr(self, "pam_misc_setenv"):
            return PAM_SYSTEM_ERR

        return self.pam_misc_setenv(self.handle,
                                    name.encode(encoding),
                                    value.encode(encoding),
                                    readonly)

    def putenv(self, name_value, encoding='utf-8'):
        """A wrapper for the pam_putenv function
        Args:
          name_value: environment variable in the format KEY=VALUE
                      Without an '=' delete the corresponding variable
        Returns:
          Linux-PAM return value as int
        """
        if not self.handle:
            return PAM_SYSTEM_ERR

        name_value = name_value.encode(encoding)

        retval = self.pam_putenv(self.handle, name_value)
        if retval != PAM_SUCCESS:
            raise Exception(self.pam_strerror(self.handle, retval))

        return retval

    def getenv(self, key, encoding='utf-8'):
        """A wrapper for the pam_getenv function
        Args:
          key name of the environment variable
        Returns:
          value of the environment variable or None on error
        """
        if not self.handle:
            return PAM_SYSTEM_ERR

        #  can't happen unless someone is using internals directly
        if sys.version_info >= (3, ):  # pragma: no branch
            if isinstance(key, six.text_type):  # pragma: no branch
                key = key.encode(encoding)

        value = self.pam_getenv(self.handle, key)

        if isinstance(value, type(None)):
            return

        if isinstance(value, int):  # pragma: no cover
            raise Exception(self.pam_strerror(self.handle, value))

        if sys.version_info >= (3,):  # pragma: no branch
            value = value.decode(encoding)

        return value

    def getenvlist(self, encoding='utf-8'):
        """A wrapper for the pam_getenvlist function
        Returns:
          environment as python dictionary
        """
        if not self.handle:
            return PAM_SYSTEM_ERR

        env_list = self.pam_getenvlist(self.handle)

        env_count = 0
        pam_env_items = {}

        while True:
            try:
                item = env_list[env_count]
            except IndexError:  # pragma: no cover
                break

            if not item:
                # end of the list
                break

            env_item = item
            if sys.version_info >= (3,):  # pragma: no branch
                env_item = env_item.decode(encoding)

            try:
                pam_key, pam_value = env_item.split("=", 1)
            except ValueError:  # pragma: no cover
                # Incorrectly formatted envlist item
                pass
            else:
                pam_env_items[pam_key] = pam_value

            env_count += 1

        return pam_env_items
