#!/bin/bash

# Source path of the precommit hook
SOURCE_HOOK="tools/git-hooks/pre-commit"

# Destination path of the pre-commit hook
DEST_HOOK=".git/hooks/pre-commit"

# Copy the precommit hook to .git/hooks directory
cp "$SOURCE_HOOK" "$DEST_HOOK"

# Make the pre-commit hook executable
chmod +x "$DEST_HOOK"

# Install ESLint and related dependencies
npm install eslint -g

echo "ESLint and related dependencies installed."
echo "Pre-commit hook copied and made executable successfully!"
