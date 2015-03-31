#!/bin/bash

#Cron script designed to kill Hue instances that are utilizing too much memory.
#If using CM, then configure CM to restart the Hue process when it dies and
#then Hue will restart after this script kills it.  Otherwise, modify this script
#to start Hue again.

KILL_ME=5000  #This is the number of MB at which it will kill.
             #Starting with 5000(5gb)
VERBOSE=true #true then this writes out the proc info each time it runs, leave blank
             #to only write out when we kill the process
LOG_FILE=/var/log/hue_mem_cron.log
ROTATE_SIZE=10 #MB before rotating, size in MB before rotating log to .1, we only keep
               #2 log files, so 20MB max

main()
{
#  Command to get memory usage.  This will handle multiple Hue instances per server, so 
#  this command grabs the highest memory Hue process at the time of running and 
#  kills it.  Then the next run it'll get the next process.
PS_COMMAND=`ps aux | grep [r]uncherrypyserver | awk '{print $6" "$2" "$3" "$12}'`
MEM=`echo ${PS_COMMAND} | awk '{print $1}'`
MEM_MB=`expr ${MEM} / 1024`
PID=`echo ${PS_COMMAND} | awk '{print $2}'`
CPU=`echo ${PS_COMMAND} | awk '{print $3}'`
PROC=`echo ${PS_COMMAND} | awk '{print $4}'`
DATE=`date '+%Y%m%d-%H%M'`

if [[ -f ${LOG_FILE} ]]
then
   LOG_SIZE=`du -sm ${LOG_FILE} | awk '{print $1}'`
   if [ ${LOG_SIZE} -gt ${ROTATE_SIZE} ]
   then
      mv ${LOG_FILE} ${LOG_FILE}.1
   fi
fi

debug "${DATE} - PID: ${PID} - CPU: ${CPU} - MEM: ${MEM} - MEM_MB: ${MEM_MB} - PROC: ${PROC}"

if [ ${MEM_MB} -gt ${KILL_ME} ]
then
   echo "${DATE} - Killing Hue Process: Too much memory: ${MEM_MB} : PID: ${PID}" >> ${LOG_FILE}
   kill ${PID}
   sleep 30
   PID2=`ps aux | grep [r]uncherrypyserver | awk '{print $2}'`
   if [[ ${PID} == ${PID2} ]]
   then
      kill -9 ${PID}
   fi
fi
}

debug()
{

  if [[ ! -z $VERBOSE ]]
  then
    echo "$1" >> ${LOG_FILE}
  fi

}

main "$@"
