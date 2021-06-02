#!/bin/bash
############################################################################
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
############################################################################
set -e

echo "Script that assembles all you need to make an RC."
echo "It generates source tar in release directory"
echo "Presumes that you can sign a release as described at https://www.apache.org/dev/release-signing.html"
echo ""
echo "Continuing will overwrite all uncommitted changes under the phoenix-queryserver repository."

read -p "Y to continue or any other key to quit" prompt
if [[ ! $prompt =~ [yY](es)* ]]
then
  echo "Aborting."
  exit
 fi

echo "Starting...";sleep 2s

# Set directory variables
DIR_ROOT="$(cd $(dirname $0);pwd)/.."
cd $DIR_ROOT

VERSION=$(grep '^version = ".*"$' setup.py | grep -o '".*"' | sed 's/"//g')

DIR_REL_BASE=$DIR_ROOT/release
DIR_REL_ROOT=$DIR_REL_BASE/python-phoenixdb-$VERSION
REL_SRC=python-phoenixdb-$VERSION-src
DIR_REL_SRC_TAR_PATH=$DIR_REL_ROOT/src

git clean -fx .

# Generate src tar
ln -s . $REL_SRC; tar cvzf $REL_SRC.tar.gz --exclude="$REL_SRC/$REL_SRC" $REL_SRC/*; rm $REL_SRC;

# Generate directory structure
mkdir $DIR_REL_BASE;
mkdir $DIR_REL_ROOT;
mkdir $DIR_REL_SRC_TAR_PATH;

# Move src tar
mv $REL_SRC.tar.gz $DIR_REL_SRC_TAR_PATH;

echo "DONE generating  source tar in release directory."
echo "Now signing source  tar"

# Sign
function_sign() {
  phoenix_tar=$(find python-phoenixdb-*.gz);

  # if on MAC OS
  if [[ "$OSTYPE" == "darwin"* ]]; then
    gpg --armor --output $phoenix_tar.asc --detach-sig $phoenix_tar;
    openssl dgst -sha512 $phoenix_tar > $phoenix_tar.sha512;
    openssl dgst -sha256 $phoenix_tar >> $phoenix_tar.sha256;
  # all other OS
  else
    gpg --armor --output $phoenix_tar.asc --detach-sig $phoenix_tar;
    sha512sum -b $phoenix_tar > $phoenix_tar.sha512;
    sha256sum -b $phoenix_tar >> $phoenix_tar.sha256;
  fi
}

cd $DIR_REL_SRC_TAR_PATH; function_sign;

# Tag
read -p "Do you want add tag for this RC in GIT? (Y for yes or any other key to continue)" prompt
if [[ $prompt =~ [yY](es)* ]]
then
  echo "Tagging..."
  read -p "Enter tag (Example python-phoenixdb-1.0.0.rc0):" prompt
  echo "Setting tag: $prompt";sleep 5s
  git tag -a $prompt -m "$prompt"; git push origin $prompt
  mv $DIR_REL_ROOT $DIR_REL_BASE/$prompt
fi

echo "DONE."
echo "If all looks good in release directory then commit RC at https://dist.apache.org/repos/dist/dev/phoenix/python-phoenixdb"
