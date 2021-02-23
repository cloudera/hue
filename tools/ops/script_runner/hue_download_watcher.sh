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
 
#parse command line arguments
parse_arguments()
{
  # Test that we're using compatible getopt version.
  getopt -T > /dev/null
  if [[ $? -ne 4 ]]; then
    echo "Incompatible getopt version."
    exit 1
  fi

  # Parse short and long option parameters.
  ROTATE_SIZE=10
  SPAWN_WATCHER=

  GETOPT=`getopt -n $0 -o d:,s:,w,h \
      -l hue-log-dir:,max-log-size:,watcher,help \
      -- "$@"`
  eval set -- "$GETOPT"
  while true;
  do
    case "$1" in
    -d|--hue-log-dir)
      DESKTOP_LOG_DIR=$2
      shift 2
      ;;
    -s|--max-log-size)
      ROTATE_SIZE=$2
      shift 2
      ;;
    -w|--watcher)
      SPAWN_WATCHER=$1
      shift 1
      ;;
    --)
      shift
      break
      ;;
    *)
      usage
      exit 1
      ;;
    esac
  done
}

usage() {
cat << EOF
usage: $0

Watches Hue log for downloads and queries:

OPTIONS
   -d|--hue-log-dir </log/path Path to Hue logs if not in /var/log/hue.
   -s|--max-log-size <MB>      Max log size before rotating.
   -w|--watcher                Spawns the watcher daemon.  DO NOT RUN FLAG YOURSELF
   -h|--help                   Show this message.
EOF
}
  
main() {
  INITIAL_ARGS=("$@")
  parse_arguments "$@"
  
  if [[ -z ${DESKTOP_LOG_DIR} ]]
  then
    DESKTOP_LOG_DIR=/var/log/hue
  fi
 
  ENDFILE=${DESKTOP_LOG_DIR}/$(basename "$0" | awk -F\. '{print $1}').finish
  RUNCPSERVER=${DESKTOP_LOG_DIR}/runcpserver.log
  LOG_FILE=${DESKTOP_LOG_DIR}/$(basename "$0" | awk -F\. '{print $1}').log


  if [[ ! ${USER} =~ .*root* ]]
  then
    echo "Script must be run as root: exiting"
    exit 1
  fi
  
  if [[ -f ${ENDFILE} ]] && [[ -z ${SPAWN_WATCHER} ]]
  then
    echo "$0 already running.  Please run:"
    echo "rm -f ${ENDFILE}"
    echo "to exit the previous running version."
    exit 1
  fi
 
  if [[ ! -z ${SPAWN_WATCHER} ]] && [[ ! -f ${ENDFILE} ]]
  then
    echo "$0 must not be run manually with -w or --watcher flags"
    exit 1
  fi 

  if [[ ! -f ${RUNCPSERVER} ]]
  then
    echo "${RUNCPSERVER} does not exist"
    echo "Please run command with correct log directory for Hue"
    usage
    exit 1
  fi
 
  if [[ ! "${ROTATE_SIZE}"  =~ ^[0-9]+$ ]]
  then
    echo "--max-log-size or -s must be a number"
    exit 1
  fi
 
  OLDTIME=1800
  # Get current and file times
  CURTIME=$(date +%s)
  FILETIME=$(stat ${RUNCPSERVER} -c %Y)
  TIMEDIFF=$(expr ${CURTIME} - ${FILETIME})
  
  # Check if file older
  if [ ${TIMEDIFF} -gt ${OLDTIME} ]; then
    echo "${RUNCPSERVER} has not been written to in 30 mins"
    echo "Be sure that ${DEKSTOP_LOG_DIR} is the correct log path"
    echo "If it is then run:"
    echo "touch ${RUNCPSERVER}"
    echo "And run this command again"
    echo "Otherwise run command with correct log directory for Hue"
    echo "$0 --hue-log-dir /path/to/hue/logs"
    echo "For example:"
    echo "$0 --hue-log-dir /var/log/hue"
    exit 1
  fi
  
  if [[ ! -z ${SPAWN_WATCHER} ]]
  then   
    tail -F ${RUNCPSERVER} | egrep --line-buffered "\/download|downloaded|TExecuteStatementResp\(|[[:digit:]]{5,9}ms" >> ${LOG_FILE} &
    PID=$!
    while [[ -f ${ENDFILE} ]]
    do
      sleep 10
      if [[ -f ${LOG_FILE} ]]
      then
        LOG_SIZE=$(du -sm ${LOG_FILE} | awk '{print $1}')
        if [[ ${LOG_SIZE} -gt ${ROTATE_SIZE} ]]
        then
          cat ${LOG_FILE} > ${LOG_FILE}.1
          cat /dev/null > ${LOG_FILE}
        fi
      fi
    done
    kill -9 ${PID}
    rm ${ENDFILE}
  else
    echo "Launching watcher daemon.  To end process run:"
    echo "rm ${ENDFILE}"
    touch ${ENDFILE}
    exec nohup "${BASH_SOURCE[0]}" --watcher "${INITIAL_ARGS[@]}" 0<&- &> /dev/null &     
  fi
  
  exit
}
  
main "$@"
  
