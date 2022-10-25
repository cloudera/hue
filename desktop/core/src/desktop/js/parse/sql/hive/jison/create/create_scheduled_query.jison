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

// Depends on sql_extract.jison, sql_main.jison

DataDefinition
 : CreateScheduledQuery
 ;

DataDefinition_EDIT
 : CreateScheduledQuery_EDIT
   {
     if ($1 && $1.suggestKeywords) {
       parser.suggestKeywords($1.suggestKeywords);
     }
   }
 ;

CreateScheduledQuery
 : 'CREATE' 'SCHEDULED' 'QUERY' RegularOrBacktickedIdentifier ScheduleSpecification OptionalExecutedAs OptionalEnabledOrDisabled DefinedAsSpecification
 ;

CreateScheduledQuery_EDIT
 : 'CREATE' 'SCHEDULED' 'CURSOR' -> { suggestKeywords: ['QUERY'] }
 | 'CREATE' 'SCHEDULED' 'QUERY' 'CURSOR'
 | 'CREATE' 'SCHEDULED' 'QUERY' RegularOrBacktickedIdentifier 'CURSOR' -> { suggestKeywords: ['CRON', 'EVERY'] }
 | 'CREATE' 'SCHEDULED' 'QUERY' RegularOrBacktickedIdentifier ScheduleSpecification_EDIT OptionalExecutedAs OptionalEnabledOrDisabled -> $5
 | 'CREATE' 'SCHEDULED' 'QUERY' RegularOrBacktickedIdentifier ScheduleSpecification OptionalExecutedAs OptionalEnabledOrDisabled 'CURSOR'
   {
     var keywords = [{ value: 'DEFINED AS', weight: 1 }, { value: 'AS', weight: 1 }]
     if (!$7) {
       keywords = keywords.concat([{ value: 'ENABLE', weight: 2 }, { value: 'ENABLED', weight: 2 },
         { value: 'DISABLE', weight: 2 }, { value: 'DISABLED', weight: 2 }]);
     }
     if (!$6 && !$7) {
       keywords.push({value: 'EXECUTED AS', weight: 3 });
       if ($5 && $5.suggestKeywords) {
         keywords = keywords.concat($5.suggestKeywords);
       }
     }
     $$ = { suggestKeywords: keywords };
   }
 | 'CREATE' 'SCHEDULED' 'QUERY' RegularOrBacktickedIdentifier ScheduleSpecification ExecutedAs_EDIT OptionalEnabledOrDisabled -> $6
 | 'CREATE' 'SCHEDULED' 'QUERY' RegularOrBacktickedIdentifier ScheduleSpecification OptionalExecutedAs OptionalEnabledOrDisabled DefinedAsSpecification_EDIT -> $8
 ;

ScheduleSpecification
 : 'CRON' QuotedValue
 | 'EVERY' 'UNSIGNED_INTEGER' DateField OptionalOffset -> !$4 ? { suggestKeywords: [{ value: 'OFFSET', weight: 4 }] } : {}
 ;

ScheduleSpecification_EDIT
 : 'EVERY' 'UNSIGNED_INTEGER' 'CURSOR' -> { suggestKeywords: ['DAY', 'DAYOFWEEK', 'HOUR', 'MINUTE', 'MONTH', 'QUARTER', 'SECOND', 'WEEK', 'YEAR'] }
 | 'EVERY' 'UNSIGNED_INTEGER' DateField Offset_EDIT -> $4
 ;

OptionalExecutedAs
 :
 | ExecutedAs
 ;

ExecutedAs
 : 'EXECUTED' 'AS' QuotedValue
 | 'EXECUTED' 'AS' RegularOrBacktickedIdentifier
 ;

ExecutedAs_EDIT
 : 'EXECUTED' 'CURSOR' -> { suggestKeywords: ['AS'] }
 ;

OptionalEnabledOrDisabled
 :
 | EnabledOrDisabled
 ;

EnabledOrDisabled
 : 'ENABLE'
 | 'ENABLED'
 | 'DISABLE'
 | 'DISABLED'
 ;

DefinedAsSpecification
 : 'DEFINED' 'AS' QuerySpecification
 | 'AS' QuerySpecification
 ;

DefinedAsSpecification_EDIT
 : 'DEFINED' 'CURSOR' -> { suggestKeywords: ['AS'] }
 | 'DEFINED' 'AS' 'CURSOR' -> { suggestKeywords: parser.DDL_AND_DML_KEYWORDS }
 | 'DEFINED' 'AS' QuerySpecification_EDIT
 | 'AS' 'CURSOR' -> { suggestKeywords: parser.DDL_AND_DML_KEYWORDS }
 | 'AS' QuerySpecification_EDIT
 ;

OptionalOffset
 :
 | 'OFFSET' ByOrAt QuotedValue
 ;

Offset_EDIT
 : 'OFFSET' 'CURSOR'
   {
     $$ = { suggestKeywords: ['AT', 'BY'] };
   }
 ;

ByOrAt
 : 'BY'
 | 'AT'
 ;
