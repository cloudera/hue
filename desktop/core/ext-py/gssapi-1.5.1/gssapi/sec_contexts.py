import six

from gssapi.raw import sec_contexts as rsec_contexts
from gssapi.raw import message as rmessage
from gssapi.raw import named_tuples as tuples
from gssapi.raw.types import RequirementFlag, IntEnumFlagSet

import gssapi.exceptions as excs
from gssapi import _utils
from gssapi.names import Name
from gssapi.creds import Credentials


@six.add_metaclass(_utils.CheckLastError)
class SecurityContext(rsec_contexts.SecurityContext):
    """A GSSAPI Security Context

    This class represents a GSSAPI security context that may be used
    with and/or returned by other GSSAPI methods.

    It inherits from the low-level GSSAPI
    :class:`~gssapi.raw.sec_contexts.SecurityContext` class,
    and thus may used with both low-level and high-level API methods.

    This class may be pickled and unpickled (the attached delegated
    credentials object will not be preserved, however).
    """

    def __new__(cls, base=None, token=None,
                name=None, creds=None, lifetime=None, flags=None,
                mech=None, channel_bindings=None, usage=None):

        if token is not None:
            base = rsec_contexts.import_sec_context(token)

        return super(SecurityContext, cls).__new__(cls, base)

    def __init__(self, base=None, token=None,
                 name=None, creds=None, lifetime=None, flags=None,
                 mech=None, channel_bindings=None, usage=None):
        """
        The constructor creates a new security context, but does not begin
        the initiate or accept process.

        If the `base` argument is used, an existing
        :class:`~gssapi.raw.sec_contexts.SecurityContext` object from
        the low-level API is converted into a high-level object.

        If the `token` argument is passed, the security context is imported
        using the token.

        Otherwise, a new security context is created.

        If the `usage` argument is not passed, the constructor will attempt
        to detect what the appropriate usage is based on either the existing
        security context (if `base` or `token` are used) or the argument set.

        For a security context of the `initiate` usage, the `name` argument
        must be used, and the `creds`, `mech`, `flags`,
        `lifetime`, and `channel_bindings` arguments may be
        used as well.

        For a security context of the `accept` usage, the `creds` and
        `channel_bindings` arguments may optionally be used.
        """

        # NB(directxman12): _last_err must be set first
        self._last_err = None

        # determine the usage ('initiate' vs 'accept')
        if base is None and token is None:
            # this will be a new context
            if usage is not None:
                if usage not in ('initiate', 'accept'):
                    msg = "Usage must be either 'initiate' or 'accept'"
                    raise excs.UnknownUsageError(msg, obj="security context")

                self.usage = usage
            elif creds is not None and creds.usage != 'both':
                self.usage = creds.usage
            elif name is not None:
                # if we pass a name, assume the usage is 'initiate'
                self.usage = 'initiate'
            else:
                # if we don't pass a name, assume the usage is 'accept'
                self.usage = 'accept'

            # check for appropriate arguments
            if self.usage == 'initiate':
                # takes: creds?, target_name, mech?, flags?,
                #        channel_bindings?
                if name is None:
                    raise TypeError("You must pass the 'name' argument when "
                                    "creating an initiating security context")
                self._target_name = name
                self._mech = mech
                self._desired_flags = IntEnumFlagSet(RequirementFlag, flags)
                self._desired_lifetime = lifetime
            else:
                # takes creds?
                if (name is not None or flags is not None or
                        mech is not None or lifetime is not None):
                    raise TypeError("You must pass at most the 'creds' "
                                    "argument when creating an accepting "
                                    "security context")

            self._channel_bindings = channel_bindings
            self._creds = creds

            self._delegated_creds = None

        else:
            # we already have a context in progress, just inspect it
            # NB(directxman12): MIT krb5 refuses to inquire about a context
            # if it's partially established, so we have to check here

            try:
                if self.locally_initiated:
                    self.usage = 'initiate'
                else:
                    self.usage = 'accept'
            except excs.MissingContextError:
                msg = ("Cannot extract usage from a partially completed "
                       "context")
                raise excs.UnknownUsageError(msg, obj="security context")

        # This is to work around an MIT krb5 bug (see the `complete` property)
        self._complete = None

    # NB(directxman12): DO NOT ADD AN __del__ TO THIS CLASS -- it screws up
    #                   the garbage collector if _last_tb is still defined

    # TODO(directxman12): implement flag properties

    def get_signature(self, message):
        """Calculate the signature for a message.

        This method calculates the signature (called a MIC) for
        the given message, which may be then used with
        :meth:`verify_signature` to confirm the validity of the
        signature.  This is useful if you wish to transmit the
        message signature and message in your own format.

        Args:
            message (bytes): the input message

        Returns:
            bytes: the message signature

        Raises:
            ExpiredContextError
            MissingContextError
            BadQoPError
        """

        # TODO(directxman12): check flags?
        return rmessage.get_mic(self, message)

    def verify_signature(self, message, mic):
        """Verify the signature for a message.

        This method verifies that a signature (generated by
        :meth:`get_signature` is valid for the given message.

        If the signature is valid, the method will return.
        Otherwise, it will raise an error.

        Args:
            message (bytes): the message
            mic (bytes): the signature to verify

        Raises:
            BadMICError: the signature was not valid
            InvalidTokenError
            DuplicateTokenError
            ExpiredTokenError
            TokenTooLateError
            TokenTooEarlyError
            ExpiredContextError
            MissingContextError
        """

        return rmessage.verify_mic(self, message, mic)

    def wrap(self, message, encrypt):
        """Wrap a message, optionally with encryption

        This wraps a message, signing it and optionally
        encrypting it.

        Args:
            message (bytes): the message to wrap
            encrypt (bool): whether or not to encrypt the message

        Returns:
            WrapResult: the wrapped message and details about it
                (e.g. whether encryption was used succesfully)

        Raises:
            ExpiredContextError
            MissingContextError
            BadQoPError
        """

        return rmessage.wrap(self, message, encrypt)

    def unwrap(self, message):
        """Unwrap a wrapped message.

        This method unwraps/unencrypts a wrapped message,
        verifying the signature along the way.

        Args:
            message (bytes): the message to unwrap/decrypt

        Returns:
            UnwrapResult: the unwrapped message and details about it
                (e.g. wheter encryption was used)

        Raises:
            InvalidTokenError
            BadMICError
            DuplicateTokenError
            ExpiredTokenError
            TokenTooLateError
            TokenTooEarlyError
            ExpiredContextError
            MissingContextError
        """

        return rmessage.unwrap(self, message)

    def encrypt(self, message):
        """Encrypt a message.

        This method wraps and encrypts a message, similarly to
        :meth:`wrap`.  The difference is that encryption is always
        used, and the method will raise an exception if this is
        not possible.  Additionally, this method simply returns
        the encrypted message directly.

        Args:
            message (bytes): the message to encrypt

        Returns:
            bytes: the encrypted message

        Raises:
            EncryptionNotUsed: the encryption could not be used
            ExpiredContextError
            MissingContextError
            BadQoPError
        """

        res = self.wrap(message, encrypt=True)

        if not res.encrypted:
            raise excs.EncryptionNotUsed("Wrapped message was not encrypted")

        return res.message

    def decrypt(self, message):
        """Decrypt a message.

        This method decrypts and unwraps a message, verifying the signature
        along the way, similarly to :meth:`unwrap`.  The difference is that
        this method will raise an exception if encryption was established
        by the context and not used, and simply returns the decrypted
        message directly.

        Args:
            message (bytes): the encrypted message

        Returns:
            bytes: the decrypted message

        Raises:
            EncryptionNotUsed: encryption was expected, but not used
            InvalidTokenError
            BadMICError
            DuplicateTokenError
            ExpiredTokenError
            TokenTooLateError
            TokenTooEarlyError
            ExpiredContextError
            MissingContextError
        """

        res = self.unwrap(message)

        if (not res.encrypted and
                self.actual_flags & RequirementFlag.confidentiality):
            raise excs.EncryptionNotUsed("The context was established with "
                                         "encryption, but unwrapped message "
                                         "was not encrypted",
                                         unwrapped_message=res.message)

        return res.message

    def get_wrap_size_limit(self, desired_output_size,
                            encrypted=True):
        """Calculate the maximum message size for a given wrapped message size.

        This method calculates the maximum input message size for a given
        maximum wrapped/encrypted message size.

        Args:
            desired_output_size (int): the maximum output message size
            encrypted (bool): whether or not encryption should be taken
                into account

        Returns:
            int: the maximum input message size

        Raises:
            MissingContextError
            ExpiredContextError
            BadQoPError
        """

        return rmessage.wrap_size_limit(self, desired_output_size,
                                        encrypted)

    def process_token(self, token):
        """Process an output token asynchronously.

        This method processes an output token even when the security context
        was not expecting it.

        Warning:
            This method is deprecated.

        Args:
            token (bytes): the token to process

        Raises:
            InvalidTokenError
            MissingContextError
        """

        rsec_contexts.process_context_token(self, token)

    def export(self):
        """Export a security context.

        This method exports a security context, allowing it to be passed
        between processes.

        Returns:
            bytes: the exported security context

        Raises:
            ExpiredContextError
            MissingContextError
            OperationUnavailableError
        """

        return rsec_contexts.export_sec_context(self)

    _INQUIRE_ARGS = ('initiator_name', 'target_name', 'lifetime',
                     'mech', 'flags', 'locally_init', 'complete')

    @_utils.check_last_err
    def _inquire(self, **kwargs):
        """Inspect the security context for information

        This method inspects the security context for information.

        If no keyword arguments are passed, all available information
        is returned.  Otherwise, only the keyword arguments that
        are passed and set to `True` are returned.

        Args:
            initiator_name (bool): get the initiator name for this context
            target_name (bool): get the target name for this context
            lifetime (bool): get the remaining lifetime for this context
            mech (bool): get the :class:`MechType` used by this context
            flags (bool): get the flags set on this context
            locally_init (bool): get whether this context was locally initiated
            complete (bool): get whether negotiation on this context has
                been completed

        Returns:
            InquireContextResult: the results of the inquiry, with unused
                fields set to None

        Raises:
            MissingContextError
        """
        if not kwargs:
            default_val = True
        else:
            default_val = False

        for arg in self._INQUIRE_ARGS:
            kwargs[arg] = kwargs.get(arg, default_val)

        res = rsec_contexts.inquire_context(self, **kwargs)

        if (kwargs.get('initiator_name', False) and
                res.initiator_name is not None):
            init_name = Name(res.initiator_name)
        else:
            init_name = None

        if (kwargs.get('target_name', False) and
                res.target_name is not None):
            target_name = Name(res.target_name)
        else:
            target_name = None

        return tuples.InquireContextResult(init_name, target_name,
                                           res.lifetime, res.mech,
                                           res.flags, res.locally_init,
                                           res.complete)

    @property
    def lifetime(self):
        """The amount of time for which this context remains valid"""
        return rsec_contexts.context_time(self)

    @property
    def delegated_creds(self):
        """The credentials delegated from the initiator to the acceptor

        .. warning::

            This value will not be preserved across picklings.  These should
            be separately exported and transfered.

        """
        return self._delegated_creds

    initiator_name = _utils.inquire_property(
        'initiator_name', 'The :class:`Name` of the initiator of this context')
    target_name = _utils.inquire_property(
        'target_name', 'The :class:`Name` of the target of this context')
    mech = _utils.inquire_property(
        'mech', 'The mechanism (:class:`MechType`) in use by this context')
    actual_flags = _utils.inquire_property(
        'flags', 'The flags set on this context')
    locally_initiated = _utils.inquire_property(
        'locally_init', 'Whether this context was locally intiated')

    @property
    @_utils.check_last_err
    def complete(self):
        """Whether negotiation for this context has been completed"""
        # NB(directxman12): MIT krb5 has a bug where it refuses to
        #                   inquire about partially completed contexts,
        #                   so we can't just use `self._inquire` generally
        if self._started:
            if self._complete is None:
                try:
                    res = self._inquire(complete=True).complete
                except excs.MissingContextError:
                    return False
                else:
                    self._complete = res

            return self._complete
        else:
            return False

    @_utils.catch_and_return_token
    def step(self, token=None):
        """Perform a negotation step.

        This method performs a negotiation step based on the usage type
        of this context.  If `__DEFER_STEP_ERRORS__` is set to True on
        the class, this method will return a token, even when exceptions
        would be thrown.  The generated exception will be thrown on the next
        method call or property lookup on the context.
        **This is the default behavior.**

        This method should be used in a while loop, as such:

        .. code-block:: python

           input_token = None
           try:
               while not ctx.complete:
                   output_token = ctx.step(input_token)
                   input_token = send_and_receive(output_token)
           except GSSError as e:
                handle_the_issue()

        .. tip::

            Disabling `__DEFER_STEP_ERRORS__` is rarely necessary.
            When this method is used in a loop (as above),
            `__DEFER_STEP_ERRORS__` will ensure that you always
            send an error token when it's available,
            keeping the other end of the security context updated
            with the status of the negotiation.

        Args:
            token (bytes): the input token from the other participant's step

        Returns:
            bytes: the output token to send to the other participant

        Raises:
            InvalidTokenError
            InvalidCredentialsError
            MissingCredentialsError
            ExpiredCredentialsError
            BadChannelBindingsError
            BadMICError
            ExpiredTokenError: (initiate only)
            DuplicateTokenError
            MissingContextError
            BadNameTypeError: (initiate only)
            BadNameError: (initiate only)
            BadMechanismError
        """

        if self.usage == 'accept':
            return self._acceptor_step(token=token)
        else:
            return self._initiator_step(token=token)

    def _acceptor_step(self, token):
        res = rsec_contexts.accept_sec_context(token, self._creds,
                                               self, self._channel_bindings)

        if res.delegated_creds is not None:
            self._delegated_creds = Credentials(res.delegated_creds)
        else:
            self._delegated_creds = None

        self._complete = not res.more_steps

        return res.token

    def _initiator_step(self, token=None):
        res = rsec_contexts.init_sec_context(self._target_name, self._creds,
                                             self, self._mech,
                                             self._desired_flags,
                                             self._desired_lifetime,
                                             self._channel_bindings,
                                             token)

        self._complete = not res.more_steps

        return res.token

    # pickle protocol support
    def __reduce__(self):
        # the unpickle arguments to new are (base=None, token=self.export())
        return (type(self), (None, self.export()))
