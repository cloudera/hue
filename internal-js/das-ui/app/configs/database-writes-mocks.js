/*
 *
 * HORTONWORKS DATAPLANE SERVICE AND ITS CONSTITUENT SERVICES
 *
 * (c) 2016-2018 Hortonworks, Inc. All rights reserved.
 *
 * This code is provided to you pursuant to your written agreement with Hortonworks, which may be the terms of the
 * Affero General Public License version 3 (AGPLv3), or pursuant to a written agreement with a third party authorized
 * to distribute this code.  If you do not have a written agreement with Hortonworks or with an authorized and
 * properly licensed third party, you do not have any rights to this code.
 *
 * If this code is provided to you under the terms of the AGPLv3:
 * (A) HORTONWORKS PROVIDES THIS CODE TO YOU WITHOUT WARRANTIES OF ANY KIND;
 * (B) HORTONWORKS DISCLAIMS ANY AND ALL EXPRESS AND IMPLIED WARRANTIES WITH RESPECT TO THIS CODE, INCLUDING BUT NOT
 *   LIMITED TO IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE;
 * (C) HORTONWORKS IS NOT LIABLE TO YOU, AND WILL NOT DEFEND, INDEMNIFY, OR HOLD YOU HARMLESS FOR ANY CLAIMS ARISING
 *   FROM OR RELATED TO THE CODE; AND
 * (D) WITH RESPECT TO YOUR EXERCISE OF ANY RIGHTS GRANTED TO YOU FOR THE CODE, HORTONWORKS IS NOT LIABLE FOR ANY
 *   DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, PUNITIVE OR CONSEQUENTIAL DAMAGES INCLUDING, BUT NOT LIMITED TO,
 *   DAMAGES RELATED TO LOST REVENUE, LOST PROFITS, LOSS OF INCOME, LOSS OF BUSINESS ADVANTAGE OR UNAVAILABILITY,
 *   OR LOSS OR CORRUPTION OF DATA.
 *
 */
import Ember from 'ember';

let databaseWritesMocks = [

{
"tableId": 1,
"tableName": "Supplier",
"writeCount" : 9953,
"bucket": "HDFS",
"columns": [
{ "name": "SupplierId", "isPrimaryKey": true } ,
{ "name": "CompanyName" },
{ "name": "Address" }]
},


{
"tableId": 2,
"tableName": "Table 2",
"writeCount" : 7500,
"bucket": "HDFS",
"columns": [
{ "name": "SupplierId", "isPrimaryKey": true } ,
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "Address" }]
},

{
"tableId": 3,
"tableName": "Table 3",
"writeCount" : 6443,
"bucket": "HDFS",
"columns": [
{ "name": "SupplierId", "isPrimaryKey": true } ,
{ "name": "CompanyName" },
{ "name": "Address" }]
},

{
"tableId": 4,
"tableName": "Table 4",
"writeCount" : 3765,
"bucket": "HDFS",
"columns": [
{ "name": "SupplierId", "isPrimaryKey": true } ,
{ "name": "CompanyName" },
{ "name": "Address" }]
},
{
"tableId": 5,
"tableName": "Table 5",
"writeCount" : 9953,
"bucket": "HDFS",
"columns": [
{ "name": "SupplierId", "isPrimaryKey": true } ,
{ "name": "CompanyName" },
{ "name": "Address" }]
},


{
"tableId": 6,
"tableName": "Table 6",
"writeCount" : 7500,
"bucket": "HDFS",
"columns": [
{ "name": "SupplierId", "isPrimaryKey": true } ,
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "Address" }]
},

{
"tableId": 7,
"tableName": "Table 7",
"writeCount" : 6443,
"bucket": "HDFS",
"columns": [
{ "name": "SupplierId", "isPrimaryKey": true } ,
{ "name": "CompanyName" },
{ "name": "Address" }]
},

{
"tableId": 8,
"tableName": "Table 8",
"writeCount" : 3765,
"bucket": "HDFS",
"columns": [
{ "name": "SupplierId", "isPrimaryKey": true } ,
{ "name": "CompanyName" },
{ "name": "Address" }]
},

{
"tableId": 9,
"tableName": "Table 9",
"writeCount" : 9953,
"bucket": "HDFS",
"columns": [
{ "name": "SupplierId", "isPrimaryKey": true } ,
{ "name": "CompanyName" },
{ "name": "Address" }]
},


{
"tableId": 10,
"tableName": "Table 10",
"writeCount" : 7500,
"bucket": "HDFS",
"columns": [
{ "name": "SupplierId", "isPrimaryKey": true } ,
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "CompanyName" },
{ "name": "Address" }]
},

{
"tableId": 11,
"tableName": "Table 11",
"writeCount" : 6443,
"bucket": "HDFS",
"columns": [
{ "name": "SupplierId", "isPrimaryKey": true } ,
{ "name": "CompanyName" },
{ "name": "Address" }]
},

{
"tableId": 12,
"tableName": "Table 12",
"writeCount" : 3765,
"bucket": "HDFS",
"columns": [
{ "name": "SupplierId", "isPrimaryKey": true } ,
{ "name": "CompanyName" },
{ "name": "Address" }]
}

];


export default databaseWritesMocks;