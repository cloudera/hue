Security
========

We take the security of ``cryptography`` seriously. The following are a set of
policies we have adopted to ensure that security issues are addressed in a
timely fashion.

What is a security issue?
-------------------------

Anytime it's possible to write code using ``cryptography``'s public API which
does not provide the guarantees that a reasonable developer would expect it to
based on our documentation.

That's a bit academic, but basically it means the scope of what we consider a
vulnerability is broad, and we do not require a proof of concept or even a
specific exploit, merely a reasonable threat model under which ``cryptography``
could be attacked.

To give a few examples of things we would consider security issues:

* If a recipe, such as Fernet, made it easy for a user to bypass
  confidentiality or integrity with the public API (e.g. if the API let a user
  reuse nonces).
* If, under any circumstances, we used a CSPRNG which wasn't fork-safe.
* If ``cryptography`` used an API in an underlying C library and failed to
  handle error conditions safely.

Examples of things we wouldn't consider security issues:

* Offering ECB mode for symmetric encryption in the *Hazmat* layer. Though ECB
  is critically weak, it is documented as being weak in our documentation.
* Using a variable time comparison somewhere, if it's not possible to
  articulate any particular program in which this would result in problematic
  information disclosure.

In general, if you're unsure, we request that you to default to treating things
as security issues and handling them sensitively, the worst thing that can
happen is that we'll ask you to file a bug issue.

Reporting a security issue
--------------------------

We ask that you do not report security issues to our normal GitHub issue
tracker.

If you believe you've identified a security issue with ``cryptography``, please
report it to ``alex.gaynor@gmail.com``. Messages may be optionally encrypted
with PGP using key fingerprint
``F7FC 698F AAE2 D2EF BECD  E98E D1B3 ADC0 E023 8CA6`` (this public key is
available from most commonly-used key servers).

Once you've submitted an issue via email, you should receive an acknowledgment
within 48 hours, and depending on the action to be taken, you may receive
further follow-up emails.

Supported Versions
------------------

At any given time, we will provide security support for the `master`_ branch
as well as the most recent release.

New releases for OpenSSL updates
--------------------------------

As of version 0.5, ``cryptography`` statically links OpenSSL on Windows, and as
of version 1.0.1 on OS X, to ease installation. Due to this, ``cryptography``
will release a new version whenever OpenSSL has a security or bug fix release to
avoid shipping insecure software.

Like all our other releases, this will be announced on the mailing list and we
strongly recommend that you upgrade as soon as possible.

Disclosure Process
------------------

Our process for taking a security issue from private discussion to public
disclosure involves multiple steps.

Approximately one week before full public disclosure, we will send advance
notification of the issue to a list of people and organizations, primarily
composed of operating-system vendors and other distributors of
``cryptography``.  This notification will consist of an email message
containing:

* A full description of the issue and the affected versions of
  ``cryptography``.
* The steps we will be taking to remedy the issue.
* The patches, if any, that will be applied to ``cryptography``.
* The date on which the ``cryptography`` team will apply these patches, issue
  new releases, and publicly disclose the issue.

Simultaneously, the reporter of the issue will receive notification of the date
on which we plan to take the issue public.

On the day of disclosure, we will take the following steps:

* Apply the relevant patches to the ``cryptography`` repository. The commit
  messages for these patches will indicate that they are for security issues,
  but will not describe the issue in any detail; instead, they will warn of
  upcoming disclosure.
* Issue the relevant releases.
* Post a notice to the cryptography mailing list that describes the issue in
  detail, point to the new release and crediting the reporter of the issue.

If a reported issue is believed to be particularly time-sensitive – due to a
known exploit in the wild, for example – the time between advance notification
and public disclosure may be shortened considerably.

The list of people and organizations who receives advanced notification of
security issues is not and will not be made public. This list generally
consists of high-profile downstream distributors and is entirely at the
discretion of the ``cryptography`` team.

.. _`master`: https://github.com/pyca/cryptography
