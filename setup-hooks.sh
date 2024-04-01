#!/bin/bash

# Function to install a git hook
install_hook() {
  local hook_name=$1

  # Source and destination paths
  local source_hook="tools/git-hooks/${hook_name}"
  local dest_hook=".git/hooks/${hook_name}"

  # Copy the hook and make it executable
  if [[ -e "${source_hook}" ]]; then
    cp "${source_hook}" "${dest_hook}" && chmod +x "${dest_hook}"
    echo "${hook_name} hook installed successfully."
  else
    echo "Error: The hook '${source_hook}' does not exist."
    exit 1
  fi
}

# Select the hook to install based on argument or use default (pre-commit)
hook_to_install=${1:-pre-commit}

# Install the selected hook
install_hook "${hook_to_install}"

# Install ESLint and related dependencies globally if pre-commit is the selected hook
if ! npm list -g eslint --depth=0 >/dev/null 2>&1; then
  npm install eslint -g
  echo "ESLint and related dependencies installed."
fi
