#!/usr/bin/env bash

set -e

if [ -z "$SPARK_HOME" ]; then
	echo "\$SPARK_HOME is not set" 1>&2
	exit 1
fi

source "$SPARK_HOME"/bin/utils.sh
source "$SPARK_HOME"/bin/load-spark-env.sh

export PYTHONPATH="$SPARK_HOME/python/:$PYTHONPATH"

for path in $(ls $SPARK_HOME/python/lib/*.zip); do
	export PYTHONPATH="$path:$PYTHONPATH"
done

export OLD_PYTHONSTARTUP="$PYTHONSTARTUP"
export PYTHONSTARTUP="$SPARK_HOME/python/pyspark/shell.py"

exec python livy-repl/src/main/resources/fake_shell.py
