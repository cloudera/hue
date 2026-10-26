#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Contract and invariant tests for ``validate_local_file_path``.

Design principles applied:
  - Test the contract (what the function promises), not the implementation
    (how it achieves that promise).  Every test answers: "What regression
    would this catch?"
  - Test what must happen AND what must not happen (negative contracts and
    invariants around side effects).
  - Use domain-aware generators (``secrets.token_hex``) instead of canned
    magic values like "alice" or "foo".  Generated values expose hidden
    assumptions about the input space without introducing new packages.
  - Cover meaningful boundaries: the exact tmpdir boundary, the username-prefix
    boundary, and the symlink-escape vector — not every permutation.
  - A small set of high-value tests rather than exhaustive permutations.
"""

import os
import secrets
import tempfile

import pytest

from desktop.lib.importer.utils import validate_local_file_path

# ---------------------------------------------------------------------------
# Domain-aware generators
#
# Use secrets.token_hex to produce unpredictable but valid values whose TYPE
# communicates intent.  A test that calls _username() says "this is a valid
# user identity", not "this happens to be the string 'alice'."
# Failures print the exact generated value, so they remain fully reproducible.
# ---------------------------------------------------------------------------


def _username() -> str:
  """An unpredictable but valid Hue username, unique per call."""
  return f"user_{secrets.token_hex(5)}"


def _uploaded_filename(username: str) -> str:
  """A filename matching the pattern stamped by ``local_file_upload``.

  ``local_file_upload`` uses ``NamedTemporaryFile(prefix=f"{username}_", ...)``,
  which produces ``{username}_{random_chars}_{original_filename}``.  We
  replicate that prefix here so the tests exercise the real contract boundary.
  """
  return f"{username}_{secrets.token_hex(8)}_data.csv"


# ---------------------------------------------------------------------------
# CONTRACT: Legitimately uploaded file is accepted
# ---------------------------------------------------------------------------


def test_legitimately_uploaded_file_is_accepted(tmp_path):
  """A file created inside tmpdir with the correct ``{username}_`` prefix must
  be accepted and its resolved real path returned.

  This is the positive contract: the guard must not block files that were
  genuinely produced by ``local_file_upload`` for the requesting user."""
  username = _username()
  f = tmp_path / _uploaded_filename(username)
  f.write_text("col1,col2\n1,2")

  result = validate_local_file_path(str(f), username)

  assert result == str(f.resolve()), "Must return the resolved real path of a valid upload"


def test_accepted_path_is_resolved_and_absolute(tmp_path):
  """The returned path must always be the fully-resolved absolute path.

  Contract: callers rely on the return value to open the file; it must not
  contain any symlink components or relative segments."""
  username = _username()
  f = tmp_path / _uploaded_filename(username)
  f.write_text("data")

  result = validate_local_file_path(str(f), username)

  assert os.path.isabs(result), "Returned path must be absolute"
  assert result == os.path.realpath(result), "Returned path must be fully resolved (no symlink components)"


# ---------------------------------------------------------------------------
# CONTRACT: Paths outside tmpdir are always rejected
#
# Each parametrized case represents a distinct real-world attack class, not
# an arbitrary permutation.  The set is intentionally small — the goal is to
# establish that the confinement boundary holds, not to enumerate every path
# on the filesystem.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
  "path",
  [
    "/proc/self/environ",  # pod environment variables (Kubernetes SA token, DB passwords)
    "/proc/self/cmdline",  # process command line
    "/etc/passwd",  # local user database
    "/etc/shadow",  # password hashes
    "/var/run/secrets/kubernetes.io/serviceaccount/token",  # Kubernetes SA token
  ],
)
def test_sensitive_system_path_is_rejected(path):
  """System paths outside tmpdir must always be rejected, regardless of username.

  These are the exact paths confirmed as exploitable in the vulnerability
  report.  Each represents a different attack-class boundary."""
  with pytest.raises(ValueError, match="not within the expected upload directory"):
    validate_local_file_path(path, _username())


def test_path_traversal_resolving_outside_tmpdir_is_rejected(tmp_path, monkeypatch):
  """A ``..``-traversal that resolves outside tmpdir must be rejected.

  ``os.path.realpath`` collapses traversal before the confinement check, so a
  path like ``{tmpdir}/../sensitive`` is caught even though it starts with
  ``{tmpdir}``.

  We monkeypatch ``tempfile.gettempdir`` to return a controlled sub-directory
  of ``tmp_path`` so the test does not depend on the real OS filesystem
  layout — making it deterministic regardless of macOS / Linux ``TMPDIR``
  settings."""
  # Establish a controlled tmpdir that is a SUB-directory of tmp_path.
  # tmp_path itself therefore acts as "outside" relative to controlled_tmpdir.
  controlled_tmpdir = tmp_path / "controlled_tmp"
  controlled_tmpdir.mkdir()
  monkeypatch.setattr(tempfile, "gettempdir", lambda: str(controlled_tmpdir))

  username = _username()
  # Traversal: starts inside controlled_tmpdir but ``..`` escapes it.
  # Resolves to tmp_path / "etc" / "passwd" — outside controlled_tmpdir.
  traversal = str(controlled_tmpdir / ".." / "etc" / "passwd")

  with pytest.raises(ValueError, match="not within the expected upload directory"):
    validate_local_file_path(traversal, username)


def test_sibling_directory_of_tmpdir_is_rejected():
  """A path whose prefix matches tmpdir (e.g. /tmp2) but is not inside it must
  be rejected.

  This verifies that the confinement check uses ``startswith(tmp_dir + os.sep)``
  rather than the weaker ``startswith(tmp_dir)``, which would be fooled by
  directory names that share a prefix with tmpdir."""
  tmp_dir = os.path.realpath(tempfile.gettempdir())
  # Construct a sibling: if tmpdir is /tmp, this produces /tmp2/file
  username = _username()
  sibling_path = tmp_dir + "2" + os.sep + _uploaded_filename(username)

  with pytest.raises(ValueError, match="not within the expected upload directory"):
    validate_local_file_path(sibling_path, username)


# ---------------------------------------------------------------------------
# CONTRACT: Symlink escape is blocked
# ---------------------------------------------------------------------------


def test_symlink_pointing_outside_tmpdir_is_rejected(tmp_path, monkeypatch):
  """A symlink that lives inside the guarded tmpdir but resolves to a path
  outside it must be rejected.

  Symlink chasing is a standard traversal technique: an attacker places a
  symlink inside ``/tmp`` (where they have write access) pointing to a
  sensitive file elsewhere.  ``os.path.realpath`` follows all symlink
  components before the confinement check, so this attack is blocked.

  We monkeypatch ``tempfile.gettempdir`` to return a controlled sub-directory
  of ``tmp_path`` so the "outside" target is simply ``tmp_path`` itself —
  deterministic and cross-platform."""
  # controlled_tmpdir is the guarded sandbox; tmp_path is "outside" relative
  # to it (it is the parent directory).
  controlled_tmpdir = tmp_path / "controlled_tmp"
  controlled_tmpdir.mkdir()
  monkeypatch.setattr(tempfile, "gettempdir", lambda: str(controlled_tmpdir))

  # The sensitive file lives in tmp_path — OUTSIDE controlled_tmpdir.
  sensitive = tmp_path / "secret.txt"
  sensitive.write_text("sensitive data")

  username = _username()
  # The symlink lives inside controlled_tmpdir (correct prefix), but resolves
  # outside it — realpath follows the link and Layer 1 fires.
  link = controlled_tmpdir / _uploaded_filename(username)
  link.symlink_to(sensitive)

  with pytest.raises(ValueError, match="not within the expected upload directory"):
    validate_local_file_path(str(link), username)


# ---------------------------------------------------------------------------
# CONTRACT: Cross-user isolation
# ---------------------------------------------------------------------------


def test_another_users_file_is_rejected(tmp_path):
  """A file uploaded by one user must be rejected when a different user requests it.

  Both the owner and the requester are generated independently, so the test
  confirms the isolation holds for any pair of distinct identities — not just
  the specific strings 'alice' and 'bob'."""
  owner = _username()
  requester = _username()
  # token_hex(5) collision probability is negligible; treat as always distinct
  assert owner != requester, "token_hex generator produced a collision — retry"

  f = tmp_path / _uploaded_filename(owner)
  f.write_text("owner's data")

  with pytest.raises(ValueError, match="not uploaded by the current user"):
    validate_local_file_path(str(f), requester)


def test_username_prefix_must_be_exact(tmp_path):
  """The username-prefix check is exact: a file whose name merely contains the
  username but does not start with ``{username}_`` must be rejected.

  Boundary: ``startswith`` is the correct operation, not ``in``."""
  username = _username()

  # Filename contains the username but as a suffix, not a prefix
  f = tmp_path / f"prefix_{username}_data.csv"
  f.write_text("data")

  with pytest.raises(ValueError, match="not uploaded by the current user"):
    validate_local_file_path(str(f), username)


# ---------------------------------------------------------------------------
# CONTRACT: Empty username is rejected before any filesystem check
# ---------------------------------------------------------------------------


def test_empty_username_is_rejected_before_filesystem_access(tmp_path):
  """An empty username must be rejected immediately, before any filesystem check.

  If the username guard were absent, ``startswith("_")`` (empty prefix + "_")
  would be trivially true for any file whose name begins with an underscore,
  silently bypassing Layer 3 for callers that forget to validate the username
  themselves.  The function must be safe in isolation, not just when called
  from already-guarded callers."""
  # Create a legitimately-looking file so we reach Layer 3 if the guard fails
  f = tmp_path / f"_{secrets.token_hex(8)}_data.csv"
  f.write_text("data")

  with pytest.raises(ValueError, match="Username is required"):
    validate_local_file_path(str(f), username="")


# ---------------------------------------------------------------------------
# CONTRACT: Non-existent file in tmpdir is rejected
# ---------------------------------------------------------------------------


def test_nonexistent_file_in_tmpdir_is_rejected(tmp_path):
  """A path inside tmpdir with the correct prefix that does not exist must be
  rejected with a clear error.

  Contract: validation must not succeed for a path that was never written —
  this prevents probing for file existence via successful validation."""
  username = _username()
  nonexistent = tmp_path / _uploaded_filename(username)
  # Deliberately do not create the file

  with pytest.raises(ValueError, match="Uploaded file not found"):
    validate_local_file_path(str(nonexistent), username)


# ---------------------------------------------------------------------------
# INVARIANT: Error messages do not leak the supplied path
#
# Error text must be static so that an attacker cannot use the error response
# as an oracle to distinguish "path outside tmpdir" from "path belongs to
# another user", and cannot confirm whether a given path exists.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
  "path",
  [
    "/proc/self/environ",
    "/etc/passwd",
    "/var/run/secrets/kubernetes.io/serviceaccount/token",
  ],
)
def test_error_message_does_not_echo_supplied_path(path):
  """Error messages must not echo back the attacker-supplied path.

  An error that includes the path (e.g. "File not found: /etc/passwd") would
  let an attacker confirm which paths exist on the server by reading 404 vs
  403 style messages.  Errors must use static, non-leaking text only."""
  with pytest.raises(ValueError) as exc_info:
    validate_local_file_path(path, _username())

  assert path not in str(exc_info.value), f"Error message must not echo the supplied path.  Got: {exc_info.value}"
