/*
 * This file was originally copied from Apache Ambari and has been modified. The modifications are subject to the
 * following provisions.
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

export default {
  "hive": {
    "ui": {
      "fileSource": {
        'uploadFromLocal': "Upload from Local",
        'uploadFromHdfs': "Upload from HDFS",
        'selectFileType': "Select File Type",
        'fileType': "File type",
        "selectHdfsLocation": "Select HDFS Directory",
        "enterHdfsPathLabel": "Enter Hdfs Path",
        "selectLocalFileLabel": "Select Local File",
      },
      "csvFormatParams": {
        'columnDelimterField': "Field Delimiter",
        'columnDelimiterTooltip': "Delimiter for the column values. Default is comman (,).",
        'escapeCharacterField': "Escape Character",
        'escapeCharacterTooltip': "Escape character. Default is backslash (\).",
        'quoteCharacterTooltip': 'Quote character. Default is double quote (").',
        'quoteCharacterField': "Quote Character",
        'isFirstRowHeader': "Is first row header?",
        'fieldsTerminatedByTooltip': "Fields Terminated By character for Hive table.",
        'isFirstRowHeaderTooltip': "Check if the first row of CSV is a header.",
        'containsEndlines': "Contains endlines?",
      },
      "uploadTable": {
        'uploadProgress': "Upload Progress",
        'uploading': "Uploading..",
        'selectFromLocal': "Select from local",
        'hdfsPath': "HDFS Path",
        'tableName': "Table name",
        'tableNameErrorMessage': "Only alphanumeric and underscore characters are allowed in table name.",
        'tableNameTooltip': "Enter valid (alphanumeric + underscore) table name.",
        'columnNameErrorMessage': "Only alphanumeric and underscore characters are allowed in column names.",
        'hdfsFieldTooltip': "Enter full HDFS path",
        'hdfsFieldPlaceholder': "Enter full HDFS path",
        'hdfsFieldErrorMessage': "Please enter complete path of hdfs file to upload.",
        'showPreview': "Preview"
      }
    },
    words :{
      temporary : "Temporary",
      actual : "Actual",
      database : "Database"
    },
    errors: {
      'no.query': "No query to process.",
      'emptyDatabase': "Please select {{ database }}.",
      'emptyTableName': "Please enter {{ tableNameField }}.",
      'illegalTableName': "Illegal {{ tableNameField }} : '{{ tableName }}'",
      'emptyIsFirstRow': "{{isFirstRowHeaderField}} cannot be null.",
      'emptyHeaders': "Headers (containing column names) cannot be null.",
      'emptyColumnName': "Column name cannot be null.",
      'illegalColumnName': "Illegal column name : '{{columnName}}' in column number {{index}}",
      'emptyHdfsPath': "HdfsPath Name cannot be null or empty.",
      'illegalHdfPath': "Illegal hdfs path : {{hdfsPath}}"
    },
    messages: {
      'generatingPreview': "Generating Preview.",
      'startingToCreateActualTable': "Creating Actual table",
      'waitingToCreateActualTable': "Waiting for creation of Actual table",
      'successfullyCreatedActualTable': "Successfully created Actual table.",
      'failedToCreateActualTable': "Failed to create Actual table.",
      'startingToCreateTemporaryTable': "Creating Temporary table.",
      'waitingToCreateTemporaryTable': "Waiting for creation of Temporary table.",
      'successfullyCreatedTemporaryTable': "Successfully created Temporary table.",
      'failedToCreateTemporaryTable': " Failed to create temporary table.",
      'deletingTable': "Deleting {{table}} table.",
      'succesfullyDeletedTable': "Successfully deleted {{ table}} table.",
      'failedToDeleteTable': "Failed to delete {{table}} table.",
      'startingToUploadFile': "Uploading file.",
      'waitingToUploadFile': "Waiting for uploading file.",
      'successfullyUploadedFile': "Successfully uploaded file.",
      'failedToUploadFile': "Failed to upload file.",
      'startingToInsertRows': "Inserting rows from temporary table to actual table.",
      'waitingToInsertRows': "Waiting for insertion of rows from temporary table to actual table.",
      'successfullyInsertedRows': "Successfully inserted rows from temporary table to actual table.",
      'failedToInsertRows': "Failed to insert rows from temporary table to actual table.",
      'startingToDeleteTemporaryTable': "Deleting temporary table.",
      'waitingToDeleteTemporaryTable': "Waiting for deletion of temporary table.",
      'successfullyDeletedTemporaryTable': "Successfully deleted temporary table",
      'manuallyDeleteTable': "You will have to manually delete the table {{databaseName}}.{{tableName}}",
      'uploadingFromHdfs': "Uploading file from HDFS ",
      'successfullyUploadedTableMessage': "Table {{tableName}} created in database {{databaseName}}",
      'successfullyUploadedTableHeader': "Uploaded Successfully"
    },
  }
};
