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

let databaseReadsMocks = [

{
"tableId": 1,
"tableName": "Supplier",
"columns": [
{ "name": "SupplierId", "rows": 9321, "type": "primary", "specialCount": 34, "isPrimaryKey": true } ,
{ "name": "CompanyName", "rows": 9289, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 7133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 7133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 7133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 4133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 4133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 4133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 4133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 4133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 4133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 4133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 4133, "type": null, "specialCount": null  },
{ "name": "City", "rows": 12, "type": null, "specialCount": null } ,
{ "name": "Region", "rows": 453, "type": null, "specialCount": null  },
{ "name": "PostalCode", "rows": 954, "type": null, "specialCount": null  }],
"haveInactiveColumns": true,
"linkedTo": [2,3,4,5,6,7,8,9,10,11,12],
"bucket": "HDFS",
"metaInfo": [
             {"propertyName":"serde Library", "propertyValue": "org.apache.hadoop.hive.serde2.objectinspector"},
             {"propertyName":"input Format", "propertyValue":"org.apache.hadoop.hive.inputFormat.OrcInputFormat"},
             {"propertyName":"output Format", "propertyValue":"org.apache.hadoop.hive.outputFormat.OrcInputFormat"},
             {"propertyName":"compressed", "propertyValue":false},
             {"propertyName":"bucket Count", "propertyValue": 5},
             {"propertyName":"bucket Columns", "propertyValue" : ["host", "type"]},
             {"propertyName":"sort Column", "propertyValue": null},
             {"propertyName":"database", "propertyValue": "default"},
             {"propertyName":"owner", "propertyValue": "hcube"},
             {"propertyName":"create Time", "propertyValue": null},
             {"propertyName":"last Access Time", "propertyValue": null},
             {"propertyName":"retention", "propertyValue": 0}
             ]
},

{   "tableId": 2,
"tableName": "Order",
"columns": [
{ "name": "SupplierId", "rows": 9321, "type": "primary", "specialCount": 34, "isPrimaryKey": true } ,
{ "name": "PostalCode", "rows": 954, "type": null, "specialCount": null  }],
"linkedTo": [1,3,4,5,6,7,8,9,10,11],
"metaInfo": [
             {"propertyName":"serde Library", "propertyValue": "org.apache.hadoop.hive.serde2.objectinspector"},
             {"propertyName":"input Format", "propertyValue":"org.apache.hadoop.hive.inputFormat.OrcInputFormat"},
             {"propertyName":"output Format", "propertyValue":"org.apache.hadoop.hive.outputFormat.OrcInputFormat"},
             {"propertyName":"compressed", "propertyValue":false},
             {"propertyName":"bucket Count", "propertyValue": 5},
             {"propertyName":"bucket Columns", "propertyValue" : ["host", "type"]},
             {"propertyName":"sort Column", "propertyValue": null},
             {"propertyName":"database", "propertyValue": "default"},
             {"propertyName":"owner", "propertyValue": "hcube"},
             {"propertyName":"create Time", "propertyValue": null},
             {"propertyName":"last Access Time", "propertyValue": null},
             {"propertyName":"retention", "propertyValue": 0}
            ]
},

{   "tableId": 3,
 "tableName": "Product",
"columns": [
{ "name": "ProductId", "rows": 9321, "type": "primary", "specialCount": 34, "isPrimaryKey": true } ,
{ "name": "ProductName", "rows": 9289, "type": null, "specialCount": null  },
{ "name": "UnitsInStock", "rows": 9133, "type": null, "specialCount": null, "isAggregationKey": true  },
{ "name": "UnitsIfOrder", "rows": 9012, "type": null, "specialCount": null, "isAggregationKey": true  },
{ "name": "SupplierId", "rows": 8453, "type": null, "specialCount": null, "isJoinKey": true  },
{ "name": "CategoryId", "rows": 3954, "type": null, "specialCount": null, "isJoinKey": true },
{ "name": "QuanityPerUnit", "rows": 2653, "type": null, "specialCount": null, "isAggregationKey": true },
{ "name": "UnitPrice", "rows": 1435, "type": null, "specialCount": null, "isPartitionKey": true  },
{ "name": "ReorderLevel", "rows": 34, "type": null, "specialCount": null, "isFilterField": true  }],
 "linkedTo": [4,5,6,7],
 "metaInfo": [
             {"propertyName":"serde Library", "propertyValue": "org.apache.hadoop.hive.serde2.objectinspector"},
             {"propertyName":"input Format", "propertyValue":"org.apache.hadoop.hive.inputFormat.OrcInputFormat"},
             {"propertyName":"output Format", "propertyValue":"org.apache.hadoop.hive.outputFormat.OrcInputFormat"},
             {"propertyName":"compressed", "propertyValue":false},
             {"propertyName":"bucket Count", "propertyValue": 5},
             {"propertyName":"bucket Columns", "propertyValue" : ["host", "type"]},
             {"propertyName":"sort Column", "propertyValue": null},
             {"propertyName":"database", "propertyValue": "default"},
             {"propertyName":"owner", "propertyValue": "hcube"},
             {"propertyName":"create Time", "propertyValue": null},
             {"propertyName":"last Access Time", "propertyValue": null},
             {"propertyName":"retention", "propertyValue": 0}
             ]
 }
,
{   "tableId": 4,
"tableName": "Table 4",
"columns": [
{ "name": "SupplierId", "rows": 9321, "type": "primary", "specialCount": 34, "isPrimaryKey": true } ,
{ "name": "CompanyName", "rows": 9289, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 7133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 7133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 7133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 4133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 4133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 4133, "type": null, "specialCount": null  },
{ "name": "City", "rows": 12, "type": null, "specialCount": null } ,
{ "name": "Region", "rows": 453, "type": null, "specialCount": null  },
{ "name": "PostalCode", "rows": 954, "type": null, "specialCount": null  }],
"linkedTo": [5],
"metaInfo": []
}
,
{   "tableId": 5,
"tableName": "Table 5",
"columns": [
{ "name": "SupplierId", "rows": 9321, "type": "primary", "specialCount": 34, "isPrimaryKey": true } ,
{ "name": "CompanyName", "rows": 9289, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 7133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 7133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 7133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 4133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 4133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 4133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "City", "rows": 12, "type": null, "specialCount": null } ,
{ "name": "Region", "rows": 453, "type": null, "specialCount": null  },
{ "name": "PostalCode", "rows": 954, "type": null, "specialCount": null  }],
"linkedTo": [6,7],
"metaInfo": []
}
,
{   "tableId": 6,
"tableName": "Table 6",
"columns": [
{ "name": "SupplierId", "rows": 9321, "type": "primary", "specialCount": 34, "isPrimaryKey": true } ,
{ "name": "CompanyName", "rows": 9289, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null , "isPrimaryKey": true },
{ "name": "Address", "rows": 7133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 7133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 7133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 4133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 4133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 4133, "type": null, "specialCount": null  },
{ "name": "City", "rows": 12, "type": null, "specialCount": null } ,
{ "name": "Region", "rows": 453, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "PostalCode", "rows": 954, "type": null, "specialCount": null  }],
"linkedTo": [7,8,9],
"metaInfo": []
}
,
{   "tableId": 7,
"tableName": "Table 7",
"columns": [
{ "name": "SupplierId", "rows": 9321, "type": "primary", "specialCount": 34, "isPrimaryKey": true } ,
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "City", "rows": 9012, "type": null, "specialCount": null } ,
{ "name": "Region", "rows": 8453, "type": null, "specialCount": null  },
{ "name": "PostalCode", "rows": 3954, "type": null, "specialCount": null  },
{ "name": "Country", "rows": 2653, "type": null, "specialCount": null  },
{ "name": "Classifications" ,"rows": 34, "type": "secondary", "specialCount": null  }],
"linkedTo": [15, 14],
"metaInfo": []
}
,
{   "tableId": 8,
"tableName": "Table 8",
"columns": [
{ "name": "SupplierId", "rows": 9321, "type": "primary", "specialCount": 34, "isPrimaryKey": true } ,
{ "name": "CompanyName", "rows": 9289, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "City", "rows": 9012, "type": null, "specialCount": null } ,
{ "name": "Region", "rows": 8453, "type": null, "specialCount": null  },
{ "name": "PostalCode", "rows": 3954, "type": null, "specialCount": null  },
{ "name": "Country", "rows": 2653, "type": null, "specialCount": null  },
{ "name": "Phone", "rows": 1435, "type": null, "specialCount": null, "isPrimaryKey": true } ,
{ "name": "Classifications" ,"rows": 34, "type": "secondary", "specialCount": null  }],
"linkedTo": [13],
"metaInfo": []
}
,
{   "tableId": 9,
"tableName": "Table 9",
"columns": [
{ "name": "SupplierId", "rows": 9321, "type": "primary", "specialCount": 34, "isPrimaryKey": true } ,
{ "name": "CompanyName", "rows": 9289, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "City", "rows": 9012, "type": null, "specialCount": null } ,
{ "name": "Region", "rows": 8453, "type": null, "specialCount": null  },
{ "name": "PostalCode", "rows": 3954, "type": null, "specialCount": null  },
{ "name": "Country", "rows": 2653, "type": null, "specialCount": null  },
{ "name": "Phone", "rows": 1435, "type": null, "specialCount": null, "isPrimaryKey": true } ,
{ "name": "Classifications" ,"rows": 34, "type": "secondary", "specialCount": null  }],
"linkedTo": [10],
"metaInfo": []
}
,
{   "tableId": 10,
"tableName": "Table 10",
"columns": [
{ "name": "SupplierId", "rows": 9321, "type": "primary", "specialCount": 34, "isPrimaryKey": true } ,
{ "name": "CompanyName", "rows": 9289, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "City", "rows": 9012, "type": null, "specialCount": null } ,
{ "name": "Region", "rows": 8453, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "PostalCode", "rows": 3954, "type": null, "specialCount": null  },
{ "name": "Country", "rows": 2653, "type": null, "specialCount": null  },
{ "name": "Phone", "rows": 1435, "type": null, "specialCount": null } ,
{ "name": "Classifications" ,"rows": 34, "type": "secondary", "specialCount": null , "isPrimaryKey": true }],
"linkedTo": [11],
"metaInfo": []
},

{   "tableId": 11,
"tableName": "Table 11",
"columns": [
{ "name": "SupplierId", "rows": 9321, "type": "primary", "specialCount": 34, "isPrimaryKey": true } ,
{ "name": "CompanyName", "rows": 9289, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "City", "rows": 9012, "type": null, "specialCount": null } ,
{ "name": "Region", "rows": 8453, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "PostalCode", "rows": 3954, "type": null, "specialCount": null  },
{ "name": "Country", "rows": 2653, "type": null, "specialCount": null  },
{ "name": "Phone", "rows": 1435, "type": null, "specialCount": null } ,
{ "name": "Classifications" ,"rows": 34, "type": "secondary", "specialCount": null , "isPrimaryKey": true }],
"linkedTo": [11],
"metaInfo": []
},

{   "tableId": 12,
"tableName": "Table 12",
"columns": [
{ "name": "SupplierId", "rows": 9321, "type": "primary", "specialCount": 34, "isPrimaryKey": true } ,
{ "name": "CompanyName", "rows": 9289, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "City", "rows": 9012, "type": null, "specialCount": null } ,
{ "name": "Region", "rows": 8453, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "PostalCode", "rows": 3954, "type": null, "specialCount": null  },
{ "name": "Country", "rows": 2653, "type": null, "specialCount": null  },
{ "name": "Phone", "rows": 1435, "type": null, "specialCount": null } ,
{ "name": "Classifications" ,"rows": 34, "type": "secondary", "specialCount": null , "isPrimaryKey": true }],
"linkedTo": [11],
"metaInfo": []
},

{   "tableId": 13,
"tableName": "Table 13",
"columns": [
{ "name": "SupplierId", "rows": 9321, "type": "primary", "specialCount": 34, "isPrimaryKey": true } ,
{ "name": "CompanyName", "rows": 9289, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "City", "rows": 9012, "type": null, "specialCount": null } ,
{ "name": "Region", "rows": 8453, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "PostalCode", "rows": 3954, "type": null, "specialCount": null  },
{ "name": "Country", "rows": 2653, "type": null, "specialCount": null  },
{ "name": "Phone", "rows": 1435, "type": null, "specialCount": null } ,
{ "name": "Classifications" ,"rows": 34, "type": "secondary", "specialCount": null , "isPrimaryKey": true }],
"linkedTo": [11],
"metaInfo": []
},

{   "tableId": 14,
"tableName": "Table 14",
"columns": [
{ "name": "SupplierId", "rows": 9321, "type": "primary", "specialCount": 34, "isPrimaryKey": true } ,
{ "name": "CompanyName", "rows": 9289, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "City", "rows": 9012, "type": null, "specialCount": null } ,
{ "name": "Region", "rows": 8453, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "PostalCode", "rows": 3954, "type": null, "specialCount": null  },
{ "name": "Country", "rows": 2653, "type": null, "specialCount": null  },
{ "name": "Phone", "rows": 1435, "type": null, "specialCount": null } ,
{ "name": "Classifications" ,"rows": 34, "type": "secondary", "specialCount": null , "isPrimaryKey": true }],
"linkedTo": [11],
"metaInfo": []
},

{   "tableId": 15,
"tableName": "Table 15",
"columns": [
{ "name": "SupplierId", "rows": 9321, "type": "primary", "specialCount": 34, "isPrimaryKey": true } ,
{ "name": "CompanyName", "rows": 9289, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "City", "rows": 9012, "type": null, "specialCount": null } ,
{ "name": "Region", "rows": 8453, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "PostalCode", "rows": 3954, "type": null, "specialCount": null  },
{ "name": "Country", "rows": 2653, "type": null, "specialCount": null  },
{ "name": "Phone", "rows": 1435, "type": null, "specialCount": null } ,
{ "name": "Classifications" ,"rows": 34, "type": "secondary", "specialCount": null , "isPrimaryKey": true }],
"linkedTo": [11],
"metaInfo": []
},

{   "tableId": 16,
"tableName": "Table 16",
"columns": [
{ "name": "SupplierId", "rows": 9321, "type": "primary", "specialCount": 34, "isPrimaryKey": true } ,
{ "name": "CompanyName", "rows": 9289, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "Address", "rows": 9133, "type": null, "specialCount": null  },
{ "name": "City", "rows": 9012, "type": null, "specialCount": null } ,
{ "name": "Region", "rows": 8453, "type": null, "specialCount": null, "isPrimaryKey": true  },
{ "name": "PostalCode", "rows": 3954, "type": null, "specialCount": null  },
{ "name": "Country", "rows": 2653, "type": null, "specialCount": null  },
{ "name": "Phone", "rows": 1435, "type": null, "specialCount": null } ,
{ "name": "Classifications" ,"rows": 34, "type": "secondary", "specialCount": null , "isPrimaryKey": true }],
"linkedTo": [11],
"metaInfo": []
}

];

export default databaseReadsMocks;