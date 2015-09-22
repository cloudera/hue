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

#Please enter the base name of each file.  They will be called ${HUE_FILE_BASE}${count}.txt.  So hue_file_test_ = hue_file_test_1.txt ....  NOTE: this must match HUE_FILE_BASE in hue_file_tester.sh
HUE_FILE_BASE="hue_file_test_"

#Plase enter the directory in HDFS where the above files will be stored.  NOTE: this must match HDFS_LOCATION in hue_file_tester.sh.  I recommend a location in /tmp so that all of the test users can reach the file.  This script will set permissions to 777 on these files.
HDFS_LOCATION="/tmp/hue_file_test"

#Please enter the number of files that will be created in $HDFS_LOCATION.  NOTE: this must match or be less than the value of FILE_COUNT in hue_file_tester.sh.  This should be a large number to generate realistic load.  I used 300.
FILE_COUNT=10

#Please enter the temporary local file system location to store the files created above before they are put in HDFS.
OUTPUT_LOCATION="/tmp/hue_file_test"

#Please specify the size of the files to be created in MB below.  Just enter an integer.  8 will create 8MB files, 50 will create 50MB files.  Larger is better since your issues come from large files.
FILE_SIZE_MB=8

if [ ! -d ${OUTPUT_LOCATION} ]
then
   mkdir -p ${OUTPUT_LOCATION}
fi

for (( count=1; count<=${FILE_COUNT}; count++ )) 
do
   FILE_NAME="${HUE_FILE_BASE}${count}.txt"
   echo "Running Command:"
   echo "dd if=/dev/zero of=${OUTPUT_LOCATION}/${FILE_NAME} bs=1024 count=0 seek=$[1024*${FILE_SIZE_MB}]"
   dd if=/dev/zero of=${OUTPUT_LOCATION}/${FILE_NAME} bs=1024 count=0 seek=$[1024*${FILE_SIZE_MB}]
done

echo "Running Command:"
echo "hadoop fs -mkdir ${HDFS_LOCATION}"
hadoop fs -mkdir ${HDFS_LOCATION}
echo "Running Command:"
echo "hadoop fs -put ${OUTPUT_LOCATION}/* ${HDFS_LOCATION}"
hadoop fs -put ${OUTPUT_LOCATION}/* ${HDFS_LOCATION}
echo "Running Command:"
echo "hadoop fs -chmod -R 777 ${HDFS_LOCATION}"
hadoop fs -chmod -R 777 ${HDFS_LOCATION}
