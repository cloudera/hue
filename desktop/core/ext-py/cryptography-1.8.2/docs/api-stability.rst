API stability
=============

From its first release, ``cryptography`` will have a strong API stability
policy.

What does this policy cover?
----------------------------

This policy includes any API or behavior that is documented in this
documentation.

What does "stable" mean?
------------------------

* Public APIs will not be removed or renamed without providing a compatibility
  alias.
* The behavior of existing APIs will not change.

What doesn't this policy cover?
-------------------------------

* We may add new features, things like the result of ``dir(obj))`` or the
  contents of ``obj.__dict__`` may change.
* Objects are not guaranteed to be pickleable, and pickled objects from one
  version of ``cryptography`` may not be loadable in future versions.
* Development versions of ``cryptography``. Before a feature is in a release,
  it is not covered by this policy and may change.

Security
~~~~~~~~

One exception to our API stability policy is for security. We will violate this
policy as necessary in order to resolve a security issue or harden
``cryptography`` against a possible attack.

Deprecation
-----------

From time to time we will want to change the behavior of an API or remove it
entirely. In that case, here's how the process will work:

* In ``cryptography X.Y`` the feature exists.
* In ``cryptography X.Y+1`` using that feature will emit a
  ``PendingDeprecationWarning``.
* In ``cryptography X.Y+2`` using that feature will emit a
  ``DeprecationWarning``.
* In ``cryptography X.Y+3`` the feature will be removed or changed.

In short, code that runs without warnings will always continue to work for a
period of two releases.
