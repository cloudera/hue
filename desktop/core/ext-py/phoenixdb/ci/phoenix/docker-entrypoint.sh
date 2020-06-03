#!/usr/bin/env bash

pids=()

/opt/hbase/bin/hbase-daemon.sh foreground_start master &
pids+=($!)

/opt/phoenix/bin/queryserver.py &
pids+=($!)

cleanup() {
    if [ ${#pids[@]} -ne 0 ]
    then
        pids=($(ps -o pid= -p "${pids[@]}"))
        if [ ${#pids[@]} -ne 0 ]
        then
            kill "${pids[@]}"
        fi
    fi
}

trap cleanup SIGCHLD SIGINT SIGTERM

wait
