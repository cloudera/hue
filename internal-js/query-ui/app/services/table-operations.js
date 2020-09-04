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

import Ember from 'ember';

export default Ember.Service.extend({
  store: Ember.inject.service(),

  submitCreateTable(database, settings) {
    let detailedInfo = this._getDetailedInfo(settings);
    let storageInfo = this._getStorageInfo(settings);
    let columns = this._getColumns(settings);
    let partitionColumns = this._getPartitionColumns(settings);

    let tableInfo = Ember.Object.create({
      database: database,
      table: settings.name,
      columns: columns,
      partitionInfo: { columns: partitionColumns },
      detailedInfo: detailedInfo,
      storageInfo: storageInfo
    });
    return new Ember.RSVP.Promise((resolve, reject) => {
      this.get('store').adapterFor('table').createTable(tableInfo).then((data) => {
        this.get('store').pushPayload(data);
        resolve(this.get('store').peekRecord('job', data.job.id));
      }, (err) => {
        reject(err);
      });
    });
  },

  editTable(settings) {
    let detailedInfo = this._getDetailedInfo(settings);
    let storageInfo = this._getStorageInfo(settings);
    let columns = this._getColumns(settings);
    let partitionColumns = this._getPartitionColumns(settings);

    let tableInfo = Ember.Object.create({
      database: settings.database,
      table: settings.table,
      columns: columns,
      partitionInfo: { columns: partitionColumns },
      detailedInfo: detailedInfo,
      storageInfo: storageInfo
    });
    return new Ember.RSVP.Promise((resolve, reject) => {
      this.get('store').adapterFor('table').editTable(tableInfo).then((data) => {
        this.get('store').pushPayload(data);
        resolve(this.get('store').peekRecord('job', data.job.id));
      }, (err) => {
        reject(err);
      });
    });
  },

  deleteTable(database, table) {
    return new Ember.RSVP.Promise((resolve, reject) => {
      this.get('store').adapterFor('table').deleteTable(database, table).then((data) => {
        this.get('store').pushPayload(data);
        resolve(this.get('store').peekRecord('job', data.job.id));
      }, (err) => {
        reject(err);
      });
    });
  },

  renameTable(databaseName, newTableName, oldTableName ) {
    return new Ember.RSVP.Promise((resolve, reject) => {
      this.get('store').adapterFor('table').renameTable(databaseName, newTableName, oldTableName).then((data) => {
        this.get('store').pushPayload(data);
        resolve(this.get('store').peekRecord('job', data.job.id));
      }, (err) => {
        reject(err);
      });
    });
  },

  deleteDatabase(database) {
    return new Ember.RSVP.Promise((resolve, reject) => {
      this.get('store').adapterFor('database').deleteDatabase(database.get('name')).then((data) => {
        this.get('store').pushPayload(data);
        resolve(this.get('store').peekRecord('job', data.job.id));
      }, (err) => {
        reject(err);
      });
    });
  },

  createDatabase(database) {
    return new Ember.RSVP.Promise((resolve, reject) => {
      this.get('store').adapterFor('database').createDatabase(database).then((data) => {
        this.get('store').pushPayload(data);
        resolve(this.get('store').peekRecord('job', data.job.id));
      }, (err) => {
        reject(err);
      });
    });
  },

  waitForJobToComplete(jobId, after) {
    return new Ember.RSVP.Promise((resolve, reject) => {
      Ember.run.later(() => {
        this.get('store').findRecord('job', jobId, {reload: true})
          .then((job) => {
            let status = job.get('status').toLowerCase();
            if (status === 'succeeded') {
              this._fetchDummyResult(jobId);
              resolve();
            } else if (status === 'error') {
              reject();
            } else {
              resolve(this.waitForJobToComplete(jobId, after));
            }
          }, (error) => {
            reject(error);
          });
      }, after);
    });
  },

  _fetchDummyResult(jobId) {
    this.get('store').adapterFor('job').fetchResult(jobId);
  },

  _getDetailedInfo(settings) {
    let detailedInfo = {};
    detailedInfo['parameters'] = this._getTableProperties(settings);

    if (!Ember.isEmpty(settings.settings.location)) {
      detailedInfo['location'] = settings.settings.location;
    }

    return detailedInfo;

  },

  _getStorageInfo(settings) {
    const storageSettings = settings.settings;
    let storageInfo = {};
    let parameters = {};



    if (!(Ember.isEmpty(storageSettings.fileFormat) || Ember.isEmpty(storageSettings.fileFormat.type))) {
      storageInfo.fileFormat = storageSettings.fileFormat.type;
      if (storageSettings.fileFormat.type === 'CUSTOM Serde') {
        storageInfo.inputFormat = storageSettings.inputFormat;
        storageInfo.outputFormat = storageSettings.outputFormat;
      }
    }

    if (!Ember.isEmpty(storageSettings.rowFormat)) {
      let addParameters = false;
      if (!Ember.isEmpty(storageSettings.rowFormat.fieldTerminatedBy)) {
        parameters['field.delim'] = String.fromCharCode(storageSettings.rowFormat.fieldTerminatedBy.id);
        addParameters = true;
      }

      if (!Ember.isEmpty(storageSettings.rowFormat.linesTerminatedBy)) {
        parameters['line.delim'] = String.fromCharCode(storageSettings.rowFormat.linesTerminatedBy.id);
        addParameters = true;
      }

      if (!Ember.isEmpty(storageSettings.rowFormat.nullDefinedAs)) {
        parameters['serialization.null.format'] = String.fromCharCode(storageSettings.rowFormat.nullDefinedAs.id);
        addParameters = true;
      }

      if (!Ember.isEmpty(storageSettings.rowFormat.escapeDefinedAs)) {
        parameters['escape.delim'] = String.fromCharCode(storageSettings.rowFormat.escapeDefinedAs.id);
        addParameters = true;
      }

      if (addParameters) {
        storageInfo.parameters = parameters;
      }
    }

    if (!Ember.isEmpty(settings.settings.numBuckets)) {
      storageInfo['numBuckets'] = settings.settings.numBuckets;
    }

    let clusteredColumnNames =  settings.columns.filterBy('isClustered', true).map((column) => {
      return column.get('name');
    });

    if (clusteredColumnNames.length > 0) {
      storageInfo['bucketCols'] = clusteredColumnNames;
    }

    return storageInfo;
  },

  _getColumns(settings) {
    return settings.columns.filterBy('isPartitioned', false).map((column) => {
      return {
        name: column.get('name'),
        type: column.get('type.label'),
        comment: column.get('comment'),
        precision: column.get('precision'),
        scale: column.get('scale')
      };
    });
  },

  _getPartitionColumns(settings) {
    return settings.columns.filterBy('isPartitioned', true).map((column) => {
      return {
        name: column.get('name'),
        type: column.get('type.label'),
        comment: column.get('comment'),
        precision: column.get('precision'),
        scale: column.get('scale')
      };
    });
  },

  _getTableProperties(settings) {
    let properties = {};
    settings.properties.forEach(function (property) {
      properties[property.key] = property.value;
    });

    if (settings.settings.transactional) {
      if (Ember.isEmpty(properties['transactional'])) {
        properties['transactional'] = true;
      }
    }

    return properties;
  }


});
