// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// Depends on create_scheduled_query.jison

DataDefinition
 : AlterScheduledQuery
 ;

DataDefinition_EDIT
 : AlterScheduledQuery_EDIT
   {
     if ($1 && $1.suggestKeywords) {
       parser.suggestKeywords($1.suggestKeywords);
     }
   }
 ;

AlterScheduledQuery
 : 'ALTER' 'SCHEDULED' 'QUERY' RegularOrBacktickedIdentifier AlterScheduledQueryRightPart
 ;

AlterScheduledQuery_EDIT
 : 'ALTER' 'SCHEDULED' 'CURSOR' -> { suggestKeywords: ['QUERY'] }
 | 'ALTER' 'SCHEDULED' 'QUERY' RegularOrBacktickedIdentifier 'CURSOR' -> { suggestKeywords: ['AS', 'CRON', 'DEFINED AS', 'DISABLE', 'DISABLED', 'ENABLE', 'ENABLED', 'EVERY', 'EXECUTE', 'EXECUTED AS' ] }
 | 'ALTER' 'SCHEDULED' 'QUERY' RegularOrBacktickedIdentifier AlterScheduledQueryRightPart_EDIT -> $5
 ;

AlterScheduledQueryRightPart
 : ScheduleSpecification
 | ExecutedAs
 | EnabledOrDisabled
 | DefinedAsSpecification
 | 'EXECUTE'
 ;

AlterScheduledQueryRightPart_EDIT
 : ScheduleSpecification_EDIT
 | ScheduleSpecification 'CURSOR' -> $1
 | ExecutedAs_EDIT
 | DefinedAsSpecification_EDIT
 ;
