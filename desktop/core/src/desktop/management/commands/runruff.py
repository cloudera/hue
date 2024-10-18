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

import sys
import logging
import os.path
import argparse
import subprocess

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from desktop.lib import paths

LOG = logging.getLogger()


class Command(BaseCommand):
  help = _("""
    Run Ruff code quality checks on Python files.

    This command runs Ruff on a set of Python files, either specified explicitly or
    determined by comparing the current branch with a specified diff branch.

    Options:
      --diff-branch=<branch>  Compare the current branch with the specified branch
                              and check only the files that have changed.
      All original Ruff commands are supported, including --fix to automatically fix errors.

    Examples:
      Run Ruff linting on specific Python files:
        ./build/env/bin/hue runruff check file1.py file2.py

      Run Ruff linting on files changed between the current branch and a specified diff branch:
        ./build/env/bin/hue runruff --diff-branch=origin/master check

      Automatically fix all Ruff errors on files changed between the current branch and a specified diff branch:
        ./build/env/bin/hue runruff --diff-branch=origin/master check --fix

    Note:
      Make sure to install Ruff first by running `./build/env/bin/pip install ruff` in your environment.
      This command passes all additional arguments to Ruff, so you can use any Ruff option or flag.
  """)

  def __init__(self):
    super().__init__()

  def diff_files(self, diff_branch):
    """
    Returns a list of files that have changed between the current branch and the specified diff_branch.

    Args:
      diff_branch (str): The branch to compare with.

    Returns:
      list: A list of files that have changed.
    """
    git_cmd = ["git", "diff", "--name-only", diff_branch, "--diff-filter=bd"]
    egrep_cmd = ["egrep", ".py$"]

    try:
      # Run the git command first and capture it's output
      git_process = subprocess.run(git_cmd, stdout=subprocess.PIPE, check=True)
      git_output, _ = git_process.stdout, git_process.stderr

      # Next, run the egrep command on git output and capture final output to return as list of files
      egrep_process = subprocess.run(egrep_cmd, input=git_output, stdout=subprocess.PIPE, check=True)
      egrep_output, _ = egrep_process.stdout, egrep_process.stderr

      # Decode the egrep output, strip trailing newline, split into a list of files, and return it
      # Otherwise, return an empty list
      return egrep_output.decode().strip('\n').split('\n') if egrep_output else []

    except subprocess.CalledProcessError as e:
      LOG.error(f"Error running git or egrep command: {e}")
      return []

  def add_arguments(self, parser):
    parser.add_argument('ruff_args', nargs=argparse.REMAINDER, help='Additional Ruff arguments, e.g. check, format, --fix etc.')
    parser.add_argument(
      '--diff-branch',
      action='store',
      dest='diff_branch',
      default='origin/master',
      help='Compare with this branch to check only changed files',
    )

  def handle(self, *args, **options):
    """
    Handles the command.

    Args:
      *args: Variable arguments.
      **options: Keyword arguments.
    """
    ruff_package = paths.get_build_dir('env', 'bin', 'ruff')

    if not os.path.exists(ruff_package):
      msg = _(
        "Ruff is not installed. Please run `./build/env/bin/pip install ruff` and try again. Make sure you are in the correct virtualenv."
      )
      self.stderr.write(msg + '\n')
      sys.exit(1)

    ruff_cmd = [ruff_package] + options.get('ruff_args')

    if options.get('diff_branch'):
      diff_files = self.diff_files(options['diff_branch'])

      if not diff_files:
        self.stdout.write(_("No Python code files changes present.") + '\n')
        return None

      ruff_cmd += diff_files

    try:
      ret = subprocess.run(ruff_cmd, check=True)
      if ret.returncode != 0:
        sys.exit(1)
    except subprocess.CalledProcessError:
      sys.exit(1)
