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

import $ from 'jquery';
import 'jasmine-ajax';

import AutocompleteResults from '../autocompleteResults';
import dataCatalog from 'catalog/dataCatalog';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import LOTS_OF_PARSE_RESULTS from './lotsOfParseResults';

describe('AutocompleteResults.js', () => {
  const subject = new AutocompleteResults({
    snippet: {
      autocompleteSettings: {
        temporaryOnly: false
      },
      type: function() {
        return 'hive';
      },
      database: function() {
        return 'default';
      },
      namespace: function() {
        return { id: 'defaultNamespace' };
      },
      compute: function() {
        return { id: 'defaultCompute' };
      },
      whenContextSet: function() {
        return $.Deferred().resolve();
      }
    },
    editor: function() {
      return {
        getTextBeforeCursor: function() {
          return 'foo';
        },
        getTextAfterCursor: function() {
          return 'bar';
        }
      };
    }
  });

  describe('Test a whole lot of different parse results', () => {
    beforeEach(() => {
      dataCatalog.disableCache();
      window.AUTOCOMPLETE_TIMEOUT = 1;
      global.AUTOCOMPLETE_TIMEOUT = 1;
      jasmine.Ajax.install();

      const failResponse = {
        status: 500
      };

      jasmine.Ajax.stubRequest(/.*\/notebook\/api\/autocomplete\/$/).andReturn(
        Math.random() < 0.5
          ? failResponse
          : {
              status: 200,
              statusText: 'HTTP/1.1 200 OK',
              contentType: 'application/json',
              responseText: '{"status": 0, "databases": ["default"]}'
            }
      );

      jasmine.Ajax.stubRequest(/.*\/notebook\/api\/autocomplete\/[^/]+$/).andReturn(
        Math.random() < 0.5
          ? failResponse
          : {
              status: 200,
              statusText: 'HTTP/1.1 200 OK',
              contentType: 'application/json',
              responseText:
                '{"status": 0, "tables_meta": [' +
                '{"comment": "comment", "type": "Table", "name": "foo"}, ' +
                '{"comment": null, "type": "View", "name": "bar_view"}, ' +
                '{"comment": null, "type": "Table", "name": "bar"}]}'
            }
      );

      jasmine.Ajax.stubRequest(/.*\/notebook\/api\/autocomplete\/[^/]+\/[^/]+$/).andReturn(
        Math.random() < 0.5
          ? failResponse
          : {
              status: 200,
              statusText: 'HTTP/1.1 200 OK',
              contentType: 'application/json',
              responseText:
                '{"status": 0, "support_updates": false, "hdfs_link": "/filebrowser/view=/user/hive/warehouse/customers", "extended_columns": [{"comment": "", "type": "int", "name": "id"}, {"comment": "", "type": "string", "name": "name"}, {"comment": "", "type": "struct<email_format:string,frequency:string,categories:struct<promos:boolean,surveys:boolean>>", "name": "email_preferences"}, {"comment": "", "type": "map<string,struct<street_1:string,street_2:string,city:string,state:string,zip_code:string>>", "name": "addresses"}, {"comment": "", "type": "array<struct<order_id:string,order_date:string,items:array<struct<product_id:int,sku:string,name:string,price:double,qty:int>>>>", "name": "orders"}], "columns": ["id", "name", "email_preferences", "addresses", "orders"], "partition_keys": []}'
            }
      );

      jasmine.Ajax.stubRequest(/.*\/notebook\/api\/autocomplete\/[^/]+\/[^/]+\/[^/]+$/).andReturn(
        Math.random() < 0.5
          ? failResponse
          : {
              status: 200,
              statusText: 'HTTP/1.1 200 OK',
              contentType: 'application/json',
              responseText:
                '{"status": 0, "comment": "", "type": "struct", "name": "email_preferences", "fields": [{"type": "string", "name": "email_format"}, {"type": "string", "name": "frequency"}, {"fields": [{"type": "boolean", "name": "promos"}, {"type": "boolean", "name": "surveys"}], "type": "struct", "name": "categories"}]}'
            }
      );

      jasmine.Ajax.stubRequest(
        /.*\/notebook\/api\/autocomplete\/[^/]+\/[^/]+\/[^/]+\/.*$/
      ).andReturn(
        Math.random() < 0.5
          ? failResponse
          : {
              status: 200,
              statusText: 'HTTP/1.1 200 OK',
              contentType: 'application/json',
              responseText:
                '{"status": 0, "fields": [{"type": "boolean", "name": "promos"}, {"type": "boolean", "name": "surveys"}], "type": "struct", "name": "categories"}'
            }
      );

      jasmine.Ajax.stubRequest(/.*\/filebrowser\/view.*/).andReturn(
        Math.random() < 0.5
          ? failResponse
          : {
              status: 200,
              statusText: 'HTTP/1.1 200 OK',
              contentType: 'text/javascript',
              response: {
                superuser: 'hdfs',
                current_request_path: '/filebrowser/view=///var',
                current_dir_path: '///var',
                show_download_button: true,
                cwd_set: true,
                breadcrumbs: [
                  {
                    url: '/',
                    label: '/'
                  },
                  {
                    url: '/var',
                    label: 'var'
                  }
                ],
                apps: [
                  'help',
                  'sqoop',
                  'pig',
                  'hbase',
                  'rdbms',
                  'indexer',
                  'metastore',
                  'beeswax',
                  'jobsub',
                  'metadata',
                  'zookeeper',
                  'search',
                  'useradmin',
                  'notebook',
                  'proxy',
                  'oozie',
                  'spark',
                  'filebrowser',
                  'about',
                  'jobbrowser',
                  'dashboard',
                  'security',
                  'impala'
                ],
                show_upload_button: true,
                files: [
                  {
                    humansize: '0\u00a0bytes',
                    url: '/filebrowser/view=/',
                    stats: {
                      size: 0,
                      group: 'supergroup',
                      blockSize: 0,
                      replication: 0,
                      user: 'hdfs',
                      mtime: 1476970119,
                      path: '///var/..',
                      atime: 0,
                      mode: 16877
                    },
                    name: '..',
                    mtime: 'October 20, 2016 06:28 AM',
                    rwx: 'drwxr-xr-x',
                    path: '/',
                    is_sentry_managed: false,
                    type: 'dir',
                    mode: '40755'
                  },
                  {
                    humansize: '0\u00a0bytes',
                    url: '/filebrowser/view=/var',
                    stats: {
                      size: 0,
                      group: 'supergroup',
                      blockSize: 0,
                      replication: 0,
                      user: 'hdfs',
                      mtime: 1470887321,
                      path: '///var',
                      atime: 0,
                      mode: 16877
                    },
                    name: '.',
                    mtime: 'August 10, 2016 08:48 PM',
                    rwx: 'drwxr-xr-x',
                    path: '/var',
                    is_sentry_managed: false,
                    type: 'dir',
                    mode: '40755'
                  },
                  {
                    humansize: '0\u00a0bytes',
                    url: '/filebrowser/view=/var/lib',
                    stats: {
                      size: 0,
                      group: 'supergroup',
                      blockSize: 0,
                      replication: 0,
                      user: 'hdfs',
                      mtime: 1470887321,
                      path: '/var/lib',
                      atime: 0,
                      mode: 16877
                    },
                    name: 'lib',
                    mtime: 'August 10, 2016 08:48 PM',
                    rwx: 'drwxr-xr-x',
                    path: '/var/lib',
                    is_sentry_managed: false,
                    type: 'dir',
                    mode: '40755'
                  },
                  {
                    humansize: '0\u00a0bytes',
                    url: '/filebrowser/view=/var/log',
                    stats: {
                      size: 0,
                      group: 'mapred',
                      blockSize: 0,
                      replication: 0,
                      user: 'yarn',
                      mtime: 1470887196,
                      path: '/var/log',
                      atime: 0,
                      mode: 17405
                    },
                    name: 'log',
                    mtime: 'August 10, 2016 08:46 PM',
                    rwx: 'drwxrwxr-xt',
                    path: '/var/log',
                    is_sentry_managed: false,
                    type: 'dir',
                    mode: '41775'
                  }
                ],
                users: [],
                is_embeddable: false,
                supergroup: 'supergroup',
                descending: 'false',
                groups: [],
                is_trash_enabled: true,
                pagesize: 50,
                file_filter: 'any',
                is_fs_superuser: false,
                is_sentry_managed: false,
                home_directory: '/user/admin',
                path: '///var',
                page: {
                  num_pages: 1,
                  total_count: 2,
                  next_page_number: 1,
                  end_index: 2,
                  number: 1,
                  previous_page_number: 1,
                  start_index: 1
                }
              }
            }
      );

      huePubSub.publish('assist.clear.all.caches');
    });

    afterEach(() => {
      AUTOCOMPLETE_TIMEOUT = 0;
      dataCatalog.enableCache();
      jasmine.Ajax.uninstall();
    });

    LOTS_OF_PARSE_RESULTS.forEach(parseResult => {
      // if (parseResult.index < 9) {
      it('should handle parse result no. ' + parseResult.index, () => {
        if (parseResult.suggestKeywords) {
          const cleanedKeywords = [];
          parseResult.suggestKeywords.forEach(keyword => {
            if (!keyword.value) {
              cleanedKeywords.push({ value: keyword });
            } else {
              cleanedKeywords.push(keyword);
            }
          });
          parseResult.suggestKeywords = cleanedKeywords;
        }
        try {
          subject.update(parseResult);
        } catch (e) {
          fail('Got exception');
          console.error(e);
        }
        if (subject.loading()) {
          for (let i = 0; i < jasmine.Ajax.requests.count(); i++) {
            console.log(jasmine.Ajax.requests.at(i));
          }
          fail('Still loading, missing ajax spec?');
        }
        expect(subject.loading()).toBeFalsy();
      });
      // }
    });
  });

  it('should handle parse results with keywords', () => {
    subject.entries([]);
    expect(subject.filtered().length).toBe(0);
    subject.update({
      lowerCase: true,
      suggestKeywords: [{ value: 'BAR', weight: 1 }, { value: 'FOO', weight: 2 }]
    });
    expect(subject.filtered().length).toBe(2);
    // Sorted by weight, case adjusted
    expect(subject.filtered()[0].meta).toBe(I18n('keyword'));
    expect(subject.filtered()[0].value).toBe('foo');
    expect(subject.filtered()[1].meta).toBe(I18n('keyword'));
    expect(subject.filtered()[1].value).toBe('bar');
  });

  it('should handle parse results with identifiers', () => {
    subject.entries([]);
    expect(subject.filtered().length).toBe(0);
    subject.update({
      lowerCase: false,
      suggestIdentifiers: [{ name: 'foo', type: 'alias' }, { name: 'bar', type: 'table' }]
    });
    expect(subject.filtered().length).toBe(2);
    // Sorted by name, no case adjust
    expect(subject.filtered()[0].meta).toBe('table');
    expect(subject.filtered()[0].value).toBe('bar');
    expect(subject.filtered()[1].meta).toBe('alias');
    expect(subject.filtered()[1].value).toBe('foo');
  });

  it('should handle parse results with functions', () => {
    subject.entries([]);
    expect(subject.filtered().length).toBe(0);
    subject.update({
      lowerCase: false,
      suggestFunctions: {}
    });
    expect(subject.filtered().length).toBeGreaterThan(0);
    expect(subject.filtered()[0].details.arguments).toBeDefined();
    expect(subject.filtered()[0].details.signature).toBeDefined();
    expect(subject.filtered()[0].details.description).toBeDefined();
  });
});
