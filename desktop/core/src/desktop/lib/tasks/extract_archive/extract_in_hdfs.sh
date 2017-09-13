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
FILE_NAME=
OUTPUT_PATH=

function usage()
{
    echo "Arguments '-u' and '-f' are mandatory."
    echo "Usage:"
    echo "\t-h --help"
    echo "\t[-u | --upload-path]=<PATH_IN_HDFS>"
    echo "\t[-f | --file-name]=<FILE_NAME>"
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
        -f | --file-name)
            FILE_NAME=$VALUE
            ;;
        -o | --output-path)
            OUTPUT_PATH=$VALUE
            ;;
        *)
            echo "ERROR: unknown parameter \"$PARAM\""
            usage
            exit 1
            ;;
    esac
    shift
done

if [ -z "$UPLOAD_PATH" ] || [ -z "$FILE_NAME" ] || [ -z "$OUTPUT_PATH" ]
then
	echo "ERROR: Missing Arguments"
	usage
	exit 1
fi

exit_status=0

temp_output_dir=`mktemp -d 2>/dev/null || mktemp -d -t 'mytmpdir'`
echo 'Created temporary output directory: '$temp_output_dir

set -x
if [[ "$FILE_NAME" =~ \.zip$ ]]
then
	unzip "$FILE_NAME" -d $temp_output_dir
	exit_status=$(echo $?)
elif [[ "$FILE_NAME" =~ \.tar\.gz$ ]] || [[ "$FILE_NAME" =~ \.tgz$ ]]
then
	tar -xvzf "$FILE_NAME" -C $temp_output_dir
	exit_status=$(echo $?)
elif [[ "$FILE_NAME" =~ \.bz2$ ]] || [[ "$FILE_NAME" =~ \.bzip2$ ]]
then
	filename_without_extension=$(echo "$FILE_NAME" | cut -f 1 -d '.')
	bzip2 -dc "$FILE_NAME" > $temp_output_dir/"$filename_without_extension"
	exit_status=$(echo $?)
else
	echo 'ERROR: Could not interpret archive type.'
	exit_status=1
fi

set +x
extracted_file_count=$(($(find $temp_output_dir/* -type d -maxdepth 0 | wc -l) + $(find $temp_output_dir/* -type f -maxdepth 0 | wc -l)))
if [ $extracted_file_count != 0 ] && [ $exit_status == 0 ]
then
    if ! $(hadoop fs -test -d $OUTPUT_PATH)
    then
        echo "Creating output directory '$OUTPUT_PATH' in HDFS"
        hadoop fs -mkdir $OUTPUT_PATH
    fi
	echo "Copying extracted files to '$OUTPUT_PATH' in HDFS"
	hadoop fs -put $temp_output_dir/* "$OUTPUT_PATH"
	exit_status=$(echo $?)
	if [ $exit_status != 0 ]
	then
	    echo "Failed to copy files to HDFS directory '$OUTPUT_PATH'."
	else
	    echo "Copy to HDFS directory '$OUTPUT_PATH' complete."
	fi
else
	exit_status=1
fi

rm -rf $temp_output_dir
echo 'Deleted temporary output directory: '$temp_output_dir

exit $exit_status