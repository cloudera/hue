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

# NOTE: This script requires curl to be installed.  Also, it does not have to run on the Hue server, it can run anywhere that curl is installed.  As long as that host can reach the Hue server.

# Please change USERS to contain a list of users that you would like to use to generate load

#USERS="cconner test1 test2 test3 test4 test5 test6 test7 test8 test9 test10"

#Please enter the Hue server name below
HUE_SERVER="cdh412-1"

#Please enter the Hue server port below
HUE_PORT="8888"

#Plase enter the query to be run in beeswax
#QUERY="select+*+from+movies+where+name+like+'D%'%3B"
#QUERY="select+t1.id%2C%0D%0A+t1.name%2C+t2.movie_date%2C+t3.movie_url%2C%0D%0A+CASE+WHEN+t1.id+%3C+500+THEN+%270%27%0D%0A+WHEN+t1.id+%3C+1000+THEN+%27500%27%0D%0A+WHEN+t1.id+%3C+1500+THEN+%271000%27%0D%0A+else+%271500%27+END+as+id_number%0D%0A+from+rc_movies+t1%0D%0A+join+movie2.movie_date+t2+on+%28t1.id+%3D+t2.id%29%0D%0A+join+movie3.movie_url+t3+on+%28t1.id+%3D+t3.id%29%0D%0A+where+t2.movie_date+like+%27%251993%25%27%0D%0A+or+t2.movie_date+like+%27%251994%25%27%3B"
#QUERY="select+t1.id,+t1.name,+t2.movie_date,+t3.movie_url+from+rc_movies+t1+join+movie2.movie_date+t2+on+(t1.id+=+t2.id)+join+movie3.movie_url+t3+on+(t1.id+=+t3.id)+where+t2.movie_date+like+'%1993%'+or+t2.movie_date+like+'%1994%'%3B"


#Please create an entry below for every user that you added to USERS above.  After the = replace "password" with the correct password for each user.  If you have more or less than the number of entries below, add or delete rows as necessary.
#declare -A password_hash
#password_hash[cconner]="password"
#password_hash[test1]="password"
#password_hash[test2]="password"
#password_hash[test3]="password"
#password_hash[test4]="password"
#password_hash[test5]="password"
#password_hash[test6]="password"
#password_hash[test7]="password"
#password_hash[test8]="password"
#password_hash[test9]="password"
#password_hash[test10]="password"

declare -A query_hash
query_hash[1]="blah"

HUE_PASS_URL="${HUE_SERVER}:${HUE_PORT}/accounts/login/"
HUE_BEES_URL="${HUE_SERVER}:${HUE_PORT}/beeswax/execute"
HUE_USERS=60

rm -f /tmp/test*.txt

#for user in $USERS
for ((x=1;x<=${HUE_USERS};x++))
do
    user="test$x"
    echo "Running Command:"
#    echo "curl -i -c /tmp/${user}_cookie.txt -d \"username=${user}&password=${password_hash[${user}]}\" \"${HUE_PASS_URL}\""
#    curl -i -c /tmp/${user}_cookie.txt -d "username=${user}&password=${password_hash[${user}]}" "${HUE_PASS_URL}" > /dev/null
    echo "curl -i -c /tmp/${user}_cookie.txt -d \"username=${user}&password=password\" \"${HUE_PASS_URL}\""
    curl -i -c /tmp/${user}_cookie.txt -d "username=${user}&password=password" "${HUE_PASS_URL}" > /dev/null
done


while [ 1 ]
do

#   for ((x=1;x<=${HUE_USERS};x++))
#   do
#      user="test$x"
#      QUERY_CREATE_DB="create+database+if+not+exists+${user}%3B"
#      echo "running Command:"
#      echo "curl --data \"query-is_parameterized=on&query-query=${QUERY_CREATE_DB}&settings-next_form_id=0&file_resources-next_form_id=0&functions-next_form_id=0&button-submit=Execute\" --dump-header /tmp/${user}_headers.txt -i -b /tmp/${user}_cookie.txt \"${HUE_BEES_URL}\""
#      curl --data "query-is_parameterized=on&query-query=${QUERY_CREATE_DB}&settings-next_form_id=0&file_resources-next_form_id=0&functions-next_form_id=0&button-submit=Execute" --dump-header /tmp/${user}_headers.txt -i -b /tmp/${user}_cookie.txt "${HUE_BEES_URL}" 2>&1 > /dev/null
#      rand_sleep=$((RANDOM%10+1))
##      sleep ${rand_sleep}
#      sleep 2
#   done
#   for ((x=1;x<=${HUE_USERS};x++))
#   do
#      user="test$x"
#      echo "Gathering Location from /tmp/${user}_headers.txt"
#      DESIGN=`grep "Location: " /tmp/${user}_headers.txt  | awk '{print $2}'`
#      RESULTS=""
#      while [ "$RESULTS" == "" ]
#      do
#         sleep 2 
#         echo "Running Command:"
#         echo "curl --dump-header /tmp/${user}_headers.txt -i -b /tmp/${user}_cookie.txt ${DESIGN}"
#         curl --dump-header /tmp/${user}_headers.txt -i -b /tmp/${user}_cookie.txt ${DESIGN} 2>&1 > /dev/null
#         echo "Gathering Location from /tmp/${user}_headers.txt"
#         RESULTS=`grep "Location: " /tmp/${user}_headers.txt | awk '{print$2}'`
#      done
#      echo "Running Command:"
#      echo "curl -i -b /tmp/${user}_cookie.txt ${RESULTS}"
#      curl -i -b /tmp/${user}_cookie.txt ${RESULTS} > /tmp/${user}_results.txt
#    done

#   for ((x=1;x<=${HUE_USERS};x++))
#   do
#      user="test$x"
#      QUERY_DROP="drop+table+if+exists+${user}.students%3B"
#      echo "running Command:"
#      echo "curl --data \"query-is_parameterized=on&query-query=${QUERY_DROP}&settings-next_form_id=0&file_resources-next_form_id=0&functions-next_form_id=0&button-submit=Execute\" --dump-header /tmp/${user}_headers.txt -i -b /tmp/${user}_cookie.txt \"${HUE_BEES_URL}\""
#      curl --data "query-is_parameterized=on&query-query=${QUERY_DROP}&settings-next_form_id=0&file_resources-next_form_id=0&functions-next_form_id=0&button-submit=Execute" --dump-header /tmp/${user}_headers.txt -i -b /tmp/${user}_cookie.txt "${HUE_BEES_URL}" 2>&1 > /dev/null
#      rand_sleep=$((RANDOM%10+1))
##      sleep ${rand_sleep}
#      sleep 2
#   done
#   for ((x=1;x<=${HUE_USERS};x++))
#   do
#      user="test$x"
#      echo "Gathering Location from /tmp/${user}_headers.txt"
#      DESIGN=`grep "Location: " /tmp/${user}_headers.txt  | awk '{print $2}'`
##      RESULTS=""
#      while [ "$RESULTS" == "" ]
#      do
#         sleep 2 
#         echo "Running Command:"
#         echo "curl --dump-header /tmp/${user}_headers.txt -i -b /tmp/${user}_cookie.txt ${DESIGN}"
#         curl --dump-header /tmp/${user}_headers.txt -i -b /tmp/${user}_cookie.txt ${DESIGN} 2>&1 > /dev/null
#         echo "Gathering Location from /tmp/${user}_headers.txt"
#         RESULTS=`grep "Location: " /tmp/${user}_headers.txt | awk '{print$2}'`
#      done
#      echo "Running Command:"
#      echo "curl -i -b /tmp/${user}_cookie.txt ${RESULTS}"
#      curl -i -b /tmp/${user}_cookie.txt ${RESULTS} > /tmp/${user}_results.txt
#    done
#
#   for ((x=1;x<=${HUE_USERS};x++))
#   do
#      user="test$x"
#      QUERY_CREATE_TABLE="create+table+${user}.students(name+String,+age+Int,+gpa+Int,+date1+Timestamp)+ROW+FORMAT+DELIMITED+FIELDS+TERMINATED+BY+','%3B"
#      echo "running Command:"
#      echo "curl --data \"query-is_parameterized=on&query-query=${QUERY_CREATE_TABLE}&settings-next_form_id=0&file_resources-next_form_id=0&functions-next_form_id=0&button-submit=Execute\" --dump-header /tmp/${user}_headers.txt -i -b /tmp/${user}_cookie.txt \"${HUE_BEES_URL}\""
#      curl --data "query-is_parameterized=on&query-query=${QUERY_CREATE_TABLE}&settings-next_form_id=0&file_resources-next_form_id=0&functions-next_form_id=0&button-submit=Execute" --dump-header /tmp/${user}_headers.txt -i -b /tmp/${user}_cookie.txt "${HUE_BEES_URL}" 2>&1 > /dev/null
#      rand_sleep=$((RANDOM%10+1))
##      sleep ${rand_sleep}
#      sleep 2
#   done
#   for ((x=1;x<=${HUE_USERS};x++))
#   do
#      user="test$x"
#      echo "Gathering Location from /tmp/${user}_headers.txt"
#      DESIGN=`grep "Location: " /tmp/${user}_headers.txt  | awk '{print $2}'`
#      RESULTS=""
#      while [ "$RESULTS" == "" ]
#      do
#         sleep 2 
#         echo "Running Command:"
#         echo "curl --dump-header /tmp/${user}_headers.txt -i -b /tmp/${user}_cookie.txt ${DESIGN}"
#         curl --dump-header /tmp/${user}_headers.txt -i -b /tmp/${user}_cookie.txt ${DESIGN} 2>&1 > /dev/null
#         echo "Gathering Location from /tmp/${user}_headers.txt"
#         RESULTS=`grep "Location: " /tmp/${user}_headers.txt | awk '{print$2}'`
#      done
#      echo "Running Command:"
#      echo "curl -i -b /tmp/${user}_cookie.txt ${RESULTS}"
#      curl -i -b /tmp/${user}_cookie.txt ${RESULTS} > /tmp/${user}_results.txt
#    done
#
   for ((x=1;x<=${HUE_USERS};x++))
   do
      user="test$x"
      QUERY_LOAD_DATA="LOAD+DATA+INPATH+'/user/cconner/data/random_names2/blah.txt'+INTO+TABLE+${user}.students%3B"
      echo "running Command:"
      echo "curl --data \"query-is_parameterized=on&query-query=${QUERY_LOAD_DATA}&settings-next_form_id=0&file_resources-next_form_id=0&functions-next_form_id=0&button-submit=Execute\" --dump-header /tmp/${user}_headers.txt -i -b /tmp/${user}_cookie.txt \"${HUE_BEES_URL}\""
      curl --data "query-is_parameterized=on&query-query=${QUERY_LOAD_DATA}&settings-next_form_id=0&file_resources-next_form_id=0&functions-next_form_id=0&button-submit=Execute" --dump-header /tmp/${user}_headers.txt -i -b /tmp/${user}_cookie.txt "${HUE_BEES_URL}" 2>&1 > /dev/null
      rand_sleep=$((RANDOM%10+1))
#      sleep ${rand_sleep}
      sleep 2
   done
   for ((x=1;x<=${HUE_USERS};x++))
   do
      user="test$x"
      echo "Gathering Location from /tmp/${user}_headers.txt"
      DESIGN=`grep "Location: " /tmp/${user}_headers.txt  | awk '{print $2}'`
      RESULTS=""
      while [ "$RESULTS" == "" ]
      do
         sleep 2 
         echo "Running Command:"
         echo "curl --dump-header /tmp/${user}_headers.txt -i -b /tmp/${user}_cookie.txt ${DESIGN}"
         curl --dump-header /tmp/${user}_headers.txt -i -b /tmp/${user}_cookie.txt ${DESIGN} 2>&1 > /dev/null
         echo "Gathering Location from /tmp/${user}_headers.txt"
         RESULTS=`grep "Location: " /tmp/${user}_headers.txt | awk '{print$2}'`
      done
      echo "Running Command:"
      echo "curl -i -b /tmp/${user}_cookie.txt ${RESULTS}"
      curl -i -b /tmp/${user}_cookie.txt ${RESULTS} > /tmp/${user}_results.txt
    done

   for ((x=1;x<=${HUE_USERS};x++))
   do
      user="test$x"
      QUERY_SELECT="select+count(*)+from+${user}.students1+where+name+like+'D%'%3B"
      echo "running Command:"
      echo "curl --data \"query-is_parameterized=on&query-query=${QUERY_SELECT}&settings-next_form_id=0&file_resources-next_form_id=0&functions-next_form_id=0&button-submit=Execute\" --dump-header /tmp/${user}_headers.txt -i -b /tmp/${user}_cookie.txt \"${HUE_BEES_URL}\""
      curl --data "query-is_parameterized=on&query-query=${QUERY_SELECT}&settings-next_form_id=0&file_resources-next_form_id=0&functions-next_form_id=0&button-submit=Execute" --dump-header /tmp/${user}_headers.txt -i -b /tmp/${user}_cookie.txt "${HUE_BEES_URL}" 2>&1 > /dev/null
      rand_sleep=$((RANDOM%10+1))
#      sleep ${rand_sleep}
      sleep 2
   done
   for ((x=1;x<=${HUE_USERS};x++))
   do
      user="test$x"
      echo "Gathering Location from /tmp/${user}_headers.txt"
      DESIGN=`grep "Location: " /tmp/${user}_headers.txt  | awk '{print $2}'`
      RESULTS=""
      while [ "$RESULTS" == "" ]
      do
         sleep 2 
         echo "Running Command:"
         echo "curl --dump-header /tmp/${user}_headers.txt -i -b /tmp/${user}_cookie.txt ${DESIGN}"
         curl --dump-header /tmp/${user}_headers.txt -i -b /tmp/${user}_cookie.txt ${DESIGN} 2>&1 > /dev/null
         echo "Gathering Location from /tmp/${user}_headers.txt"
         RESULTS=`grep "Location: " /tmp/${user}_headers.txt | awk '{print$2}'`
      done
      echo "Running Command:"
      echo "curl -i -b /tmp/${user}_cookie.txt ${RESULTS}"
      curl -i -b /tmp/${user}_cookie.txt ${RESULTS} > /tmp/${user}_results.txt
    done

done
