#!/usr/bin/env bash
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

UPLOAD_PATH=
FILE_NAMES=
ARCHIVE_NAME=

function usage()
{
    echo "Arguments '-u', '-f' and '-n' are mandatory."
    echo "Usage:"
    echo "\t-h --help"
    echo "\t[-u | --upload-path]=<PATH_IN_HDFS>"
    echo "\t[-f | --file-names]=<FILE_NAMES>"
    echo "\t[-n | --archive_name]=<ARCHIVE_NAME>"
    echo ""
}

while [ "$1" != "" ]; do
    PARAM=`echo $1 | awk -F= '{print $1}'`
    VALUE=`echo $1 | awk -F= '{print $2}'`
    case $PARAM in
        -h | --help)
            usage
            exit
            ;;
        -u | --upload-path)
            UPLOAD_PATH=$VALUE
            ;;
        -f | --file-names)
            FILE_NAMES=$VALUE
            ;;
        -n | --archive-name)
            ARCHIVE_NAME=$VALUE
            ;;
        *)
            echo "ERROR: unknown parameter \"$PARAM\""
            usage
            exit 1
            ;;
    esac
    shift
done

if [ -z $UPLOAD_PATH ] || [ -z $FILE_NAMES ] || [ -z $ARCHIVE_NAME ]
then
	echo "ERROR: Missing Arguments"
	usage
	exit 1
fi

FILE_NAMES=(${FILE_NAMES//,/ })
exit_status=0

temp_output_dir=`mktemp -d 2>/dev/null || mktemp -d -t 'mytmpdir'`
echo 'Created temporary output directory: '$temp_output_dir

set -x
zip -r $temp_output_dir/$ARCHIVE_NAME ${FILE_NAMES[@]}
exit_status=$(echo $?)

set +x
if [ $exit_status == 0 ]
then
	echo "Copying hue_compressed.zip to '$UPLOAD_PATH' in HDFS"
	hadoop fs -put -f $temp_output_dir/$ARCHIVE_NAME $UPLOAD_PATH
	exit_status=$(echo $?)
	if [ $exit_status == 0 ]
	then
	    echo "Copy to HDFS directory '$UPLOAD_PATH' complete!!!"
	else
	    echo "ERROR: Copy to HDFS directory '$UPLOAD_PATH' FAILED!!!"
	fi
else
	exit_status=1
fi

rm -rf $temp_output_dir
echo 'Deleted temporary output directory: '$temp_output_dir

exit $exit_status