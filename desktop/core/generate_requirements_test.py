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

import os
import platform
import shutil
import sys
import tempfile
from unittest import mock

import pytest

# Workaround for import error: add current directory to Python path
# The package-style import (desktop.core.generate_requirements) fails,
# so we modify the path to enable direct module import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_requirements import RequirementsGenerator


class TestRequirementsGenerator:
  """Test cases for the RequirementsGenerator class."""

  def setup_method(self):
    """
    Setup test environment with temporary directory and mock requirement files.
    Stores original system values to restore after test.
    """
    # Store original system values to restore later
    self.original_arch = platform.machine
    self.original_version_info = sys.version_info
    self.temp_dir = tempfile.mkdtemp()

    # Create a temporary ext-py3 directory mimicking the structure used by RequirementsGenerator
    self.ext_py3_dir = os.path.join(self.temp_dir, "ext-py3")
    os.makedirs(self.ext_py3_dir)

    # Create empty placeholder files that simulate local requirement packages
    for req in ["boto-2.49.0", "django-axes-5.13.0", "django-babel", "pysaml2-7.3.1", "python-sasl-0.3.1"]:
      with open(os.path.join(self.ext_py3_dir, req), "w") as f:
        f.write("")

  def teardown_method(self):
    """Teardown after each test method."""
    shutil.rmtree(self.temp_dir)
    platform.machine = self.original_arch
    sys.version_info = self.original_version_info

  @mock.patch("generate_requirements.this_dir")
  @mock.patch("generate_requirements.platform.machine")
  @mock.patch("generate_requirements.sys.version_info")
  def test_init_sets_properties(self, mock_version_info, mock_machine, mock_this_dir):
    """Test that __init__ sets the class properties correctly."""

    mock_machine.return_value = "x86_64"
    mock_version_info.major = 3
    mock_version_info.minor = 9
    mock_this_dir.return_value = self.temp_dir

    generator = RequirementsGenerator()

    assert generator.arch == "x86_64"
    assert generator.python_version_string == "3.9"
    assert isinstance(generator.requirements, list)
    assert isinstance(generator.local_requirements, list)
    assert "x86_64" in generator.arch_requirements_map

    assert "aarch64" in generator.arch_requirements_map

  @mock.patch("generate_requirements.this_dir", create=True)
  @mock.patch("generate_requirements.shutil.copytree")
  def test_copy_local_requirements(self, mock_copytree, mock_this_dir):
    """Test that copy_local_requirements copies files and returns correct paths."""

    # Need to make this_dir return the string value directly, not a MagicMock
    mock_this_dir.__str__.return_value = self.temp_dir
    python_version_string = "3.9"

    with mock.patch.object(RequirementsGenerator, "__init__", return_value=None):
      generator = RequirementsGenerator()
      generator.local_requirements = ["boto-2.49.0", "django-axes-5.13.0"]

      result = generator.copy_local_requirements(python_version_string)

      mock_copytree.assert_called_once_with(f"{self.temp_dir}/ext-py3", f"{self.temp_dir}/{python_version_string}")

      assert len(result) == 2
      assert f"file://{self.temp_dir}/{python_version_string}/boto-2.49.0" in result
      assert f"file://{self.temp_dir}/{python_version_string}/django-axes-5.13.0" in result

  @mock.patch("generate_requirements.this_dir")
  @mock.patch("builtins.open", new_callable=mock.mock_open)
  def test_generate_requirements_x86_64(self, mock_open, mock_this_dir):
    """Test generating requirements for x86_64 architecture."""

    # Need to make this_dir return the string value directly, not a MagicMock
    mock_this_dir.__str__.return_value = self.temp_dir

    with mock.patch.object(RequirementsGenerator, "__init__", return_value=None):
      generator = RequirementsGenerator()
      generator.arch = "x86_64"
      generator.python_version_string = "3.9"
      generator.requirements = ["setuptools==70.0.0", "Django==4.1.13"]
      generator.local_requirements = []
      generator.arch_requirements_map = {"x86_64": {"default": ["cryptography==42.0.8"], "3.9": ["Markdown==3.8", "numpy==1.24.4"]}}

      # Mock copy_local_requirements for test isolation
      generator.copy_local_requirements = mock.MagicMock(return_value=[])

      generator.generate_requirements()

      # Verify file creation with correct path
      mock_open.assert_called_once_with(f"{self.temp_dir}/requirements-x86_64-3.9.txt", "w")

      # Verify correct requirements were written
      expected_requirements = "\n".join(["setuptools==70.0.0", "Django==4.1.13", "Markdown==3.8", "numpy==1.24.4"])
      mock_open().write.assert_called_once_with(expected_requirements)

  @mock.patch("generate_requirements.this_dir")
  def test_generate_requirements_unsupported_arch(self, mock_this_dir):
    """Test that generate_requirements raises an error for unsupported architectures."""

    # Need to make this_dir return the string value directly, not a MagicMock
    mock_this_dir.__str__.return_value = self.temp_dir

    with mock.patch.object(RequirementsGenerator, "__init__", return_value=None):
      generator = RequirementsGenerator()
      generator.arch = "unsupported_arch"
      generator.python_version_string = "3.9"
      generator.requirements = []
      generator.arch_requirements_map = {"x86_64": {"default": []}, "aarch64": {"default": []}}

      with pytest.raises(ValueError) as exc_info:
        generator.generate_requirements()

      assert "Unsupported architecture: unsupported_arch" in str(exc_info.value)

  @mock.patch("generate_requirements.this_dir")
  def test_get_file_name(self, mock_this_dir):
    """Test that get_file_name returns the correct file path."""

    # Need to make this_dir return the string value directly, not a MagicMock
    mock_this_dir.__str__.return_value = self.temp_dir

    with mock.patch.object(RequirementsGenerator, "__init__", return_value=None):
      generator = RequirementsGenerator()
      generator.arch = "x86_64"
      generator.python_version_string = "3.9"

      result = generator.get_file_name()

      assert result == f"{self.temp_dir}/requirements-x86_64-3.9.txt"

  @mock.patch("generate_requirements.this_dir")
  @mock.patch("builtins.open", new_callable=mock.mock_open)
  def test_generate_requirements_with_local_requirements(self, mock_open, mock_this_dir):
    """Test generating requirements including local requirements."""

    # Need to make this_dir return the string value directly, not a MagicMock
    mock_this_dir.__str__.return_value = self.temp_dir

    with mock.patch.object(RequirementsGenerator, "__init__", return_value=None):
      generator = RequirementsGenerator()
      generator.arch = "x86_64"
      generator.python_version_string = "3.9"
      generator.requirements = ["setuptools==70.0.0"]
      generator.local_requirements = ["boto-2.49.0", "django-axes-5.13.0"]
      generator.arch_requirements_map = {"x86_64": {"default": [], "3.9": ["Markdown==3.8"]}}

      # Mock copy_local_requirements to return file paths
      local_reqs = [f"file://{self.temp_dir}/3.9/boto-2.49.0", f"file://{self.temp_dir}/3.9/django-axes-5.13.0"]
      generator.copy_local_requirements = mock.MagicMock(return_value=local_reqs)

      generator.generate_requirements()

      mock_open.assert_called_once_with(f"{self.temp_dir}/requirements-x86_64-3.9.txt", "w")

      expected_requirements = "\n".join(
        ["setuptools==70.0.0", "Markdown==3.8", f"file://{self.temp_dir}/3.9/boto-2.49.0", f"file://{self.temp_dir}/3.9/django-axes-5.13.0"]
      )

      mock_open().write.assert_called_once_with(expected_requirements)
