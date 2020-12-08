#!/bin/bash
set -e
set -x

JAVA=$JAVA_HOME/bin/java

export JVM_PID="$$"

if [ "$EDWS_SERVICE_NAME" = "query-processor" ]; then
	BINARY=${DAS_HOME}/bin/qp
fi

exec $BINARY start
