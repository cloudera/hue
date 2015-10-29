#!/bin/bash
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

set -ex

echo "This build slave is $HOSTNAME"
echo "WORKSPACE is $WORKSPACE"

# make the build tools available
[ -f /opt/toolchain/toolchain.sh ] && . /opt/toolchain/toolchain.sh

export PATH=${JAVA_HOME}/bin:${PATH}

export TEST_BASE_DIR=tests
export DEPLOY_DIR=deploy
export HUE_LIVE_CLUSTER_DIR=hue-live-cluster-tests

cd "$WORKSPACE"

# Create tests dir
if ! [ -d "$TEST_BASE_DIR" ]; then
	echo "Creating base test directory"
	mkdir $TEST_BASE_DIR
fi

cd "$WORKSPACE/$TEST_BASE_DIR"

# Clone or update the deploy repo
if [ -d "$DEPLOY_DIR" ]; then
	cd $DEPLOY_DIR
	git pull
else
	echo "Cloning deploy repo"
	git clone http://github.mtv.cloudera.com/QE/deploy.git
	cd $DEPLOY_DIR
	make
fi

cd "$WORKSPACE/$TEST_BASE_DIR"

# Clone or update the Hue Live Cluster Tests repo
if [ -d "$HUE_LIVE_CLUSTER_DIR" ]; then
	cd $HUE_LIVE_CLUSTER_DIR
	git pull
else
	echo "Cloning hue-live-cluster-tests repo"
	git clone git@github.mtv.cloudera.com:erickt/hue-live-cluster-tests.git
fi

cd "$WORKSPACE/$TEST_BASE_DIR"

export CLUSTERS='nightly-{1..4}.vpc.cloudera.com'
export DATABASE=mysql
export LIVE_CLUSTER=true

echo "Setting environment variables for Hue configurations at path: ${WORKSPACE}/${TEST_BASE_DIR}/${HUE_LIVE_CLUSTER_DIR}/test-conf"
export HUE_CONF_PATH=${WORKSPACE}/${TEST_BASE_DIR}/${HUE_LIVE_CLUSTER_DIR}/test-conf/HUE_SERVER
export KRB5_CONFIG=${WORKSPACE}/${TEST_BASE_DIR}/${HUE_LIVE_CLUSTER_DIR}/test-conf/krb5.conf

echo "Fetching Hue configuration for cluster: ${CLUSTERS} and database type: ${DATABASE}"
python $WORKSPACE/$TEST_BASE_DIR/$HUE_LIVE_CLUSTER_DIR/fetch-hue-config.py --no-locks --agents $CLUSTERS --database $DATABASE

echo "Running Hue test suite"
$WORKSPACE/build/env/bin/hue test all