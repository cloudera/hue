var MAIN_SCROLLABLE = '.page-content';
(function () {
    let importerOptionsElement = document.getElementById('importerOptionsJson');
    let importerOptions = JSON.parse(importerOptionsElement.textContent);
    if (ko.options) {
        ko.options.deferUpdates = true;
    }

    var MAPPINGS = {
        SOLR_TO_HIVE: {
            "string": "string",
            "plong": "bigint",
            "pdouble": "double",
            "pdate": "timestamp",
            "long": "bigint",
            "double": "double",
            "date": "timestamp",
            "boolean": "boolean",
        },
        HIVE_TO_SOLR: {
            "bigint": "plong"
        },
        get: function (type, key, defaultValue) {
            return type[key] || defaultValue
        }
    };

    var fieldNum = 0;

    var getNewFieldName = function () {
        fieldNum++;
        return "new_field_" + fieldNum
    };

    var createDefaultField = function () {
        var defaultField = ko.mapping.fromJS(JSON.parse(importerOptions.default_field_type));

        defaultField.name = ko.observable(getNewFieldName());

        return defaultField;
    };

    var Operation = function (type) {
        var self = this;

        var createArgumentValue = function (arg) {
            if (arg.type === "mapping") {
                return ko.observableArray([]);
            }
            if (arg.type === "checkbox") {
                return ko.observable(false);
            }
            return ko.observable("");
        };

        var constructSettings = function (type) {
            var settings = {};

            var operation = viewModel.createWizard.operationTypes.find(function (currOperation) {
                return currOperation.name === type;
            });

            for (var i = 0; i < operation.args.length; i++) {
                var argVal = createArgumentValue(operation.args[i]);

                if (operation.args[i].type === "checkbox" && operation.outputType === "checkbox_fields") {
                    argVal.subscribe(function (newVal) {
                        if (newVal) {
                            self.fields.push(createDefaultField());
                        } else {
                            self.fields.pop();
                        }
                    });
                }

                settings[operation.args[i].name] = argVal;
            }

            settings.getArguments = function () {
                return operation.args
            };

            settings.outputType = function () {
                return operation.outputType;
            };

            return settings;
        };

        var init = function () {
            self.fields([]);
            self.numExpectedFields(0);

            self.numExpectedFields.subscribe(function (numExpectedFields) {
                if (numExpectedFields < self.fields().length) {
                    self.fields(self.fields().slice(0, numExpectedFields));
                } else if (numExpectedFields > self.fields().length) {
                    var difference = numExpectedFields - self.fields().length;

                    for (var i = 0; i < difference; i++) {
                        self.fields.push(createDefaultField());
                    }
                }
            });
            self.settings(constructSettings(self.type()));
        };

        self.load = function (data) {
            self.numExpectedFields(data.numExpectedFields);

            var newSettings = constructSettings(data.type);
            for (var key in data.settings) {
                newSettings[key] = ko.mapping.fromJS(data.settings[key]);
            }
            self.settings(newSettings);

            data.fields.forEach(function (field) {
                self.fields.push(loadField(field));
            });
        };

        self.type = ko.observable(type);
        self.fields = ko.observableArray();
        self.numExpectedFields = ko.observable();
        self.settings = ko.observable();

        init();

        self.type.subscribe(function () {
            init();
        });
    };

    var FileType = function (typeName, args) {
        var self = this;
        var type;

        var init = function () {
            self.type = ko.observable(typeName);
            var types = viewModel.createWizard.fileTypes;

            for (var i = 0; i < types.length; i++) {
                if (types[i].name === typeName) {
                    type = types[i];
                    break;
                }
            }

            if (type) {
                for (var i = 0; i < type.args.length; i++) {
                    self[type.args[i].name] = ko.observable();
                }

                if (args) {
                    loadFromObj(args);
                }

                setTimeout(function () {
                    var types = type.args.filter(function (x) {
                        return x && (x.type !== 'checkbox' || x.name === 'hasHeader');
                    });
                    for (var i = 0; i < types.length; i++) {
                        self[types[i].name].subscribe(function () {
                            // Update the data preview when tweaking Format options on step 1
                            viewModel.createWizard.guessFieldTypes();
                        });
                    }
                }); // Prevent notification on start
            }
        };

        var loadFromObj = function (args) {
            for (var attr in args) {
                self[attr] = ko.mapping.fromJS(args[attr]);
            }
        };

        self.getArguments = function () {
            return type ? type.args : [];
        };

        self.isCustomizable = function () {
            return type.isCustomizable;
        };

        init();
    };

    var Source = function (vm, wizard) {
        var self = this;

        self.sourceType = ko.observable(vm.sourceType);
        self.name = ko.observable('');
        self.sample = ko.observableArray();
        self.sampleCols = ko.observableArray();
        self.namespace = wizard.namespace;
        self.compute = wizard.compute;
        self.selectedComputeId = ko.observable();

        self.selectedComputeId.subscribe(function (computeId) {
            var selectedCompute = self.namespace().computes.find(function (currCompute) {
                return currCompute.name == computeId;
            })
            self.compute(selectedCompute);
        });

        self.namespace.subscribe(function (namespace) {
            if (namespace.computes.length > 0 && self.selectedComputeId() === undefined) {
                self.selectedComputeId(namespace.computes[0].name)
            }
        })

        var refreshThrottle = -1;
        var sampleColSubDisposals = [];
        var lastStatement = '';
        var refreshTemporaryTable = function (sampleCols) {
            window.clearTimeout(refreshThrottle);
            window.setTimeout(function () {
                while (sampleColSubDisposals.length) {
                    sampleColSubDisposals.pop()();
                }
                if (!self.sampleCols().length) {
                    return;
                }

                var tableName = 'input';
                switch (self.inputFormat()) {
                    case 'stream':
                        if (self.streamSelection() === 'kafka' && self.kafkaSelectedTopics()) {
                            tableName = self.kafkaSelectedTopics();
                        }
                        break;
                    case 'file':
                        tableName = self.path().split('/').pop();
                        break;
                    case 'table':
                    case 'rdbms':
                        tableName = self.tableName();
                }

                var statementCols = [];
                var temporaryColumns = [];

                var deferreds = []; // TODO: Move to async/await when in webpack

                sampleCols.forEach(function (sampleCol) {
                    var deferred = $.Deferred();
                    deferreds.push(deferred);
                    sqlUtils.backTickIfNeeded({ id: self.sourceType(), dialect: self.sourceType() }, sampleCol.name()).then(function (value) {
                        statementCols.push(value);
                        var col = {
                            name: sampleCol.name(),
                            type: sampleCol.type()
                        };
                        temporaryColumns.push(col);
                        var colNameSub = sampleCol.name.subscribe(function () {
                            refreshTemporaryTable(self.sampleCols())
                        });
                        var colTypeSub = sampleCol.type.subscribe(function () {
                            refreshTemporaryTable(self.sampleCols())
                        });
                        sampleColSubDisposals.push(function () {
                            colNameSub.dispose();
                            colTypeSub.dispose();
                        })
                        deferred.resolve();
                    }).catch(deferred.reject);
                });

                $.when.apply($, deferreds).done(function () {
                    var statement = 'SELECT ';
                    statement += statementCols.join(',\n    ');
                    statement += '\n FROM ' + sqlUtils.backTickIfNeeded({ id: self.sourceType(), dialect: self.sourceType() }, tableName) + ';';
                    if (!wizard.destination.fieldEditorValue() || wizard.destination.fieldEditorValue() === lastStatement) {
                        wizard.destination.fieldEditorValue(statement);
                    }
                    lastStatement = statement;
                    wizard.destination.fieldEditorPlaceHolder('Example: SELECT' + ' * FROM ' + sqlUtils.backTickIfNeeded({ id: self.sourceType(), dialect: self.sourceType() }, tableName));

                    var handle = dataCatalog.addTemporaryTable({
                        namespace: self.namespace(),
                        compute: self.compute(),
                        connector: { id: self.sourceType() }, // TODO: Migrate importer to connectors
                        name: tableName,
                        columns: temporaryColumns,
                        sample: self.sample()
                    });
                    sampleColSubDisposals.push(function () {
                        handle.delete();
                    })
                })
            }, 500)
        };


        self.sampleCols.subscribe(refreshTemporaryTable);
        if (window.ENABLE_DIRECT_UPLOAD) {
            self.inputFormat = ko.observable(wizard.prefill.source_type() ? wizard.prefill.source_type() : 'localfile');
        } else {
            self.inputFormat = ko.observable(wizard.prefill.source_type() ? wizard.prefill.source_type() : 'file');
        }


        self.inputFormat.subscribe(function (val) {
            window.hueAnalytics.log('importer', 'source-type-selection/' + val);
            wizard.destination.columns.removeAll();
            if (self.sample()) {
                self.sample.removeAll();
            }
            self.path('');
            resizeElements();
            if (val === 'stream') {
                if (self.streamSelection() === 'kafka') {
                    wizard.guessFormat();
                    wizard.destination.outputFormat('table');
                    wizard.destination.tableFormat('kudu');
                } else {
                    wizard.destination.tableFormat('text');
                }
            } else if (val === 'table') {
                wizard.destination.outputFormat('altus');
            } else if (val === 'rdbms') {
                self.rdbmsMode('customRdbms');
            }
        });
        self.inputFormatsAll = ko.observableArray([]);

        if (window.ENABLE_DIRECT_UPLOAD) {
            self.inputFormatsAll.push({ 'value': 'localfile', 'name': 'Small Local File' });
        }
        if (window.REQUEST_FS) {
            self.inputFormatsAll.push({ 'value': 'file', 'name': 'Remote File' });
        }
        if (window.ENABLE_SQOOP) {
            self.inputFormatsAll.push({ 'value': 'rdbms', 'name': 'External Database' });
        }
        if (window.ENABLE_KAFKA) {
            self.inputFormatsAll.push({ 'value': 'stream', 'name': 'Stream' });
        }
        if (window.ENABLE_ALTUS) {
            self.inputFormatsAll.push({ 'value': 'table', 'name': 'Table' });
        }
        if (window.ENABLE_SQL_INDEXER) {
            self.inputFormatsAll.push({ 'value': 'query', 'name': 'SQL Query' });
        }
        if (window.ENABLE_ENVELOPE) {
            self.inputFormatsAll.push({ 'value': 'connector', 'name': 'Connectors' });
        }
        self.inputFormatsAll.push({ 'value': 'manual', 'name': 'Manually' });

        self.inputFormatsManual = ko.observableArray([
            { 'value': 'manual', 'name': 'Manually' }
        ]);
        self.inputFormats = ko.pureComputed(function () {
            if (wizard.prefill.source_type() === 'manual') {
                return self.inputFormatsManual();
            }
            return self.inputFormatsAll();
        });

        self.interpreters = ko.pureComputed(function () {
            return window.getLastKnownConfig().app_config.editor.interpreters.filter(function (interpreter) { return interpreter.is_sql && interpreter.dialect != 'phoenix' });
        });
        self.interpreter = ko.observable(vm.sourceType);
        self.interpreter.subscribe(function (val) {
            self.sourceType(val);
            wizard.destination.sourceType(val);
            var dialect = self.interpreters().filter(function (interpreter) {
                return interpreter['type'] === val;
            });
            wizard.destination.dialect(dialect[0]['dialect']);
        });

        // File
        self.path = ko.observable('');
        self.file_type = ko.observable('');
        self.path.subscribe(function (val) {
            if (val) {
                wizard.guessFormat();
                wizard.destination.nonDefaultLocation(val);
            }
            resizeElements();
        });
        self.isObjectStore = ko.pureComputed(function () {
            return self.inputFormat() === 'file' && /^(s3a|adl|abfs):\/.*$/.test(self.path());
        });
        self.isObjectStore.subscribe(function (newVal) {
            wizard.destination.useDefaultLocation(!newVal);
        });

        // Rdbms
        self.rdbmsMode = ko.observable();
        self.rdbmsMode.subscribe(function (val) {
            self.rdbmsTypes(null);
            self.rdbmsType('');
            self.rdbmsDatabaseName('');
            self.rdbmsIsAllTables(false);
            self.rdbmsJdbcDriver('');
            self.rdbmsJdbcDriverName('');
            self.rdbmsHostname('');
            self.rdbmsPort('');
            self.rdbmsUsername('');
            self.rdbmsPassword('');
            self.rdbmsDbIsValid(false);
            if (val === 'configRdbms') {
                $.post("/indexer/api/indexer/indexers/get_drivers", {}, function (resp) {
                    if (resp.data) {
                        self.rdbmsTypes(resp.data);
                        window.setTimeout(function () {
                            self.rdbmsType(self.rdbmsTypes()[0].value);
                        }, 0);
                    }
                });
            } else if (val === 'customRdbms') {
                self.rdbmsTypes([
                    { 'value': 'jdbc', 'name': 'JDBC' },
                    { 'value': 'mysql', 'name': 'MySQL' },
                    { 'value': 'oracle', 'name': 'Oracle' },
                    { 'value': 'postgresql', 'name': 'PostgreSQL' }
                ]);
                window.setTimeout(function () {
                    self.rdbmsType(self.rdbmsTypes()[0].value);
                }, 0);

            }
        });
        self.rdbmsTypes = ko.observableArray();

        self.rdbmsType = ko.observable(null);
        self.rdbmsType.subscribe(function (val) {
            self.path('');
            self.rdbmsDatabaseNames([]);
            self.rdbmsDatabaseName('');
            resizeElements();
            if (self.rdbmsMode() === 'configRdbms' && val !== 'jdbc') {
                self.isFetchingDatabaseNames(true);
                $.post("/indexer/api/indexer/indexers/get_db_component", {
                    "source": ko.mapping.toJSON(self)
                }, function (resp) {
                    if (resp.data) {
                        self.rdbmsDatabaseNames(resp.data);
                    }
                }).always(function () {
                    self.isFetchingDatabaseNames(false);
                });
            } else if (self.rdbmsMode() === 'configRdbms' && val === 'jdbc') {
                self.isFetchingDriverNames(true);
                $.post("/indexer/api/indexer/indexers/jdbc_db_list", {
                    "source": ko.mapping.toJSON(self)
                }, function (resp) {
                    if (resp.data) {
                        self.rdbmsJdbcDriverNames(resp.data);
                    }
                }).always(function () {
                    self.isFetchingDriverNames(false);
                });
            }
        });
        self.rdbmsDatabaseName = ko.observable('');
        self.rdbmsDatabaseName.subscribe(function (val) {
            if (val !== '') {
                self.isFetchingTableNames(true);
                $.post("/indexer/api/indexer/indexers/get_db_component", {
                    "source": ko.mapping.toJSON(self)
                }, function (resp) {
                    if (resp.data) {
                        self.rdbmsTableNames(resp.data.map(function (opt) {
                            return ko.mapping.fromJS(opt);
                        }));
                    }
                }).always(function () {
                    self.isFetchingTableNames(false);
                });
            }
        });
        self.rdbmsDatabaseNames = ko.observableArray();
        self.isFetchingDatabaseNames = ko.observable(false);
        self.rdbmsJdbcDriverNames = ko.observableArray();
        self.isFetchingDriverNames = ko.observable(false);
        self.rdbmsJdbcDriverName = ko.observable();
        self.rdbmsJdbcDriverName.subscribe(function () {
            self.rdbmsDatabaseNames([]);
            self.rdbmsDatabaseName('');
            self.isFetchingDatabaseNames(true);
            $.post("/indexer/api/indexer/indexers/get_db_component", {
                "source": ko.mapping.toJSON(self)
            }, function (resp) {
                if (resp.data) {
                    self.rdbmsDatabaseNames(resp.data);
                }
            }).always(function () {
                self.isFetchingDatabaseNames(false);
            });
        });
        self.rdbmsJdbcDriver = ko.observable('');
        self.rdbmsJdbcDriver.subscribe(function () {
            self.rdbmsDatabaseNames([]);
        });
        self.isFetchingTableNames = ko.observable(false);
        self.rdbmsTableNames = ko.observableArray();

        self.rdbmsHostname = ko.observable('');
        self.rdbmsHostname.subscribe(function () {
            self.rdbmsDatabaseNames([]);
        });
        self.rdbmsPort = ko.observable('');
        self.rdbmsPort.subscribe(function () {
            self.rdbmsDatabaseNames([]);
        });
        self.rdbmsUsername = ko.observable('');
        self.rdbmsUsername.subscribe(function () {
            self.rdbmsDatabaseNames([]);
        });
        self.rdbmsPassword = ko.observable('');
        self.rdbmsPassword.subscribe(function () {
            self.rdbmsDatabaseNames([]);
        });
        self.rdbmsIsAllTables = ko.observable(false);
        self.rdbmsIsAllTables.subscribe(function (newVal) {
            if (newVal) {
                wizard.destination.name(self.rdbmsDatabaseName());
            } else {
                wizard.destination.name(self.tables()[0] && self.tables()[0].name() || '');
            }
        });
        self.rdbmsAllTablesSelected = ko.pureComputed(function () {
            return self.rdbmsIsAllTables() || self.tables().length > 1;
        });
        self.rdbmsTablesExclude = ko.pureComputed(function () {
            var rdbmsTables = self.rdbmsTableNames();
            var tables = self.tables();
            if (tables.length <= 1) {
                return [];
            }
            var map = tables.reduce(function (map, table) {
                map[table.name()] = 1;
                return map;
            }, {});
            return rdbmsTables.map(function (table) {
                return table.name();
            }).filter(function (name) {
                return !map[name];
            });
        });
        self.rdbmsDbIsValid = ko.observable(false);
        self.rdbmsCheckConnection = function () {
            self.isFetchingDatabaseNames(true);
            self.rdbmsDatabaseNames([]);
            self.rdbmsDatabaseName(''); // Need to clear or else get_db_component will return list of tables
            $.post("/indexer/api/indexer/indexers/get_db_component", {
                "source": ko.mapping.toJSON(self)
            }, function (resp) {
                if (resp.status === 0 && resp.data) {
                    self.rdbmsDbIsValid(true);
                    self.rdbmsDatabaseNames(resp.data);
                } else if (resp.status === 1) {
                    huePubSub.publish('hue.global.error', { message: "Connection Failed: " + resp.message });
                    self.rdbmsDbIsValid(false);
                }
            }).always(function () {
                self.isFetchingDatabaseNames(false);
            });
        };

        // Table
        self.tables = ko.observableArray([
            ko.mapping.fromJS({ name: '' })
        ]);
        self.tables.subscribe(function (newVal) {
            if (newVal.length == 0) {
                wizard.destination.name('');
            } else if (newVal.length == 1) {
                wizard.destination.name(self.tables()[0].name() || ''); // TODO: db prefix and check if DB exists
            } else {
                wizard.destination.name(self.rdbmsDatabaseName());
            }
        });
        self.tablesNames = ko.observableArray([]);
        self.selectedTableIndex = ko.observable(0);
        self.table = ko.pureComputed(function () {
            var index = Math.min(self.selectedTableIndex(), self.tables().length - 1);
            return self.tables().length > 0 ? self.tables()[index].name() : ''
        });
        self.tableName = ko.pureComputed(function () {
            return self.table().indexOf('.') > 0 ? self.table().split('.', 2)[1] : self.table();
        });
        self.databaseName = ko.pureComputed(function () {
            return self.table().indexOf('.') > 0 ? self.table().split('.', 2)[0] : 'default';
        });
        self.table.subscribe(function (val) {
            if (val) {
                wizard.guessFormat();
                wizard.destination.nonDefaultLocation(val);
            }
            resizeElements();
        });

        // Queries
        self.query = ko.observable('');
        self.query.subscribe(function (newValue) {
            if (newValue) {
                viewModel.createWizard.guessFieldTypes();
            }
        });
        self.draggedQuery = ko.observable();

        // Connectors
        self.connectorList = ko.observable([
            { 'value': 'sfdc', 'name': 'Salesforce' }
        ]);
        self.connectorSelection = ko.observable(self.connectorList()[0]['value']);

        // Streams, Kafka, Flume
        self.publicStreams = ko.observable([
            { 'value': 'kafka', 'name': 'Kafka Topics' },
            { 'value': 'flume', 'name': 'Flume Agent' }
        ]);
        self.streamSelection = ko.observable(self.publicStreams()[0]['value']);
        self.streamSelection.subscribe(function (newValue) {
            if (newValue == 'flume') {
                $.post("/metadata/api/manager/get_hosts", {
                    "service": "flume"
                }, function (resp) {
                    if (resp.status === 0 && resp.hosts) {
                        self.channelSourceHosts(resp.hosts);
                    } else {
                        huePubSub.publish('hue.global.error', { message: "Error getting hosts" + resp.message });
                    }
                });
            }
        });

        self.kafkaClusters = ko.observableArray(['localhost', 'demo.gethue.com']);
        self.kafkaSelectedCluster = ko.observable();
        self.kafkaSelectedCluster.subscribe(function (val) {
            if (val && self.inputFormat() == 'stream') {
                wizard.guessFormat();
            }
        });
        self.kafkaSelectedCluster('localhost');
        self.kafkaSelectedClusterUsername = ko.observable('gethue');
        self.kafkaSelectedClusterPassword = ko.observable('pwd');
        self.kafkaTopics = ko.observableArray();
        self.kafkaSelectedTopics = ko.observable(''); // Currently designed just for one
        self.kafkaSelectedTopics.subscribe(function (newValue) {
            if (newValue) {
                viewModel.createWizard.guessFieldTypes();
                //self.kafkaFieldNames(hueUtils.hueLocalStorage('pai' + '_kafka_topics_' + newValue + '_kafkaFieldNames'));
                //self.kafkaFieldTypes(hueUtils.hueLocalStorage('pai' + '_kafka_topics_' + newValue + '_kafkaFieldTypes'));
            }
        });
        self.kafkaSchemaManual = ko.observable('detect');
        self.kafkaFieldType = ko.observable('delimited');
        self.kafkaFieldDelimiter = ko.observable(',');
        self.kafkaFieldNames = ko.observable('');
        self.kafkaFieldNames.subscribe(function (newValue) {
            hueUtils.hueLocalStorage('pai' + '_kafka_topics_' + self.kafkaSelectedTopics() + '_kafkaFieldNames', newValue);
            viewModel.createWizard.guessFieldTypes();
        });
        self.kafkaFieldTypes = ko.observable('');
        self.kafkaFieldTypes.subscribe(function (newValue) {
            hueUtils.hueLocalStorage('pai' + '_kafka_topics_' + self.kafkaSelectedTopics() + '_kafkaFieldTypes', newValue);
            viewModel.createWizard.guessFieldTypes();
        });
        self.kafkaFieldSchemaPath = ko.observable('');

        self.channelSourceTypes = ko.observableArray([
            { 'name': 'Directory or File', 'value': 'directory' },
            { 'name': 'Program', 'value': 'exec' },
            { 'name': 'Syslogs', 'value': 'syslogs' },
            { 'name': 'HTTP', 'value': 'http' }
        ]);
        self.channelSourceType = ko.observable();
        self.channelSourceHosts = ko.observableArray();
        self.channelSourceSelectedHosts = ko.observableArray([]);
        self.channelSourceSelectedHosts.subscribe(function (newVal) {
            if (newVal) {
                viewModel.createWizard.guessFieldTypes();
            }
        })
        self.channelSourcePath = ko.observable('/var/log/hue-httpd/access_log');

        self.streamUsername = ko.observable('');
        self.streamPassword = ko.observable('');
        self.streamToken = ko.observable('');
        self.streamToken.subscribe(function (newVal) {
            if (newVal) {
                wizard.guessFormat(); // Todo
            }
        });
        self.streamEndpointUrl = ko.observable('https://login.salesforce.com/services/Soap/u/42.0');
        self.streamObjects = ko.observableArray();
        self.streamObject = ko.observable();
        self.streamObject.subscribe(function (newValue) {
            if (newValue) {
                wizard.guessFieldTypes();
            }
        });
        self.hasStreamSelected = ko.pureComputed(function () {
            return (self.streamSelection() === 'kafka' && self.kafkaSelectedTopics()) ||
                (self.streamSelection() === 'sfdc' && self.streamObject())
        });
        self.hasStreamSelected.subscribe(function (newValue) {
            if (newValue) {
                wizard.guessFormat();
                if (self.streamSelection() === 'kafka') {
                    wizard.destination.tableFormat('kudu');
                } else {
                    wizard.destination.tableFormat('text');
                }
            }
        });
        self.streamCheckConnection = function () {
            huePubSub.publish('hide.global.alerts');
            $.post("/indexer/api/indexer/indexers/get_db_component", {
                "source": ko.mapping.toJSON(self)
            }, function (resp) {
                if (resp.status === 0 && resp.data) {
                    huePubSub.publish('notebook.task.submitted', resp);
                } else if (resp.status === 1) {
                    huePubSub.publish('hue.global.error', { message: "Connection Failed: " + resp.message });
                    self.rdbmsDbIsValid(false);
                }
            });
        };

        self.format = ko.observable();
        self.format.subscribe(function (newVal) {
            if (typeof newVal.hasHeader !== 'undefined') {
                wizard.destination.hasHeader(newVal.hasHeader());
                newVal.hasHeader.subscribe(function (newVal) {
                    wizard.destination.hasHeader(newVal);
                });
            }

            if (typeof newVal.fieldSeparator !== 'undefined') {
                wizard.destination.useCustomDelimiters(newVal.fieldSeparator() !== ',');
                wizard.destination.customFieldDelimiter(newVal.fieldSeparator());
                newVal.fieldSeparator.subscribe(function (newVal) {
                    if (newVal !== '') {
                        wizard.destination.customFieldDelimiter(newVal);
                    }
                });
            }
        });

        self.show = ko.pureComputed(function () {
            if (self.inputFormat() === 'localfile') {
                return self.path().length > 0;
            }
            if (self.inputFormat() === 'file') {
                return self.path().length > 0;
            }
            if (self.inputFormat() === 'table') {
                return self.tableName().length > 0;
            }
            if (self.inputFormat() === 'query') {
                return self.query();
            }
            if (self.inputFormat() === 'manual') {
                return true;
            }
            if (self.inputFormat() === 'stream') {
                if (self.streamSelection() === 'kafka') {
                    return self.kafkaSelectedTopics() && self.kafkaSelectedTopics().length > 0;
                } else if (self.streamSelection() === 'flume') {
                    return self.channelSourceSelectedHosts().length > 0;
                }
            }
            if (self.inputFormat() === 'sfdc') {
                return self.streamUsername().length > 0 &&
                    self.streamPassword().length > 0 &&
                    self.streamToken().length > 0 &&
                    self.streamEndpointUrl().length > 0 &&
                    self.streamObject();
            }
            if (self.inputFormat() === 'rdbms') {
                return (self.rdbmsDatabaseName().length > 0 && self.tables().length > 0) || self.rdbmsAllTablesSelected();
            }
        });
    };

    var Destination = function (vm, wizard) {
        var self = this;
        self.apiHelperType = vm.sourceType;
        self.sourceType = ko.observable(vm.sourceType);
        self.dialect = ko.observable('');

        self.name = ko.observable('').extend({ throttle: 500 });
        self.nameChanged = function (name) {
            var exists = false;

            var checkDbEntryExists = function () {
                wizard.computeSetDeferred.done(function () {
                    dataCatalog.getEntry({
                        compute: wizard.compute(),
                        connector: { id: self.sourceType() }, // TODO: Use connectors in the importer
                        namespace: wizard.namespace(),
                        path: self.outputFormat() === 'table' ? [self.databaseName(), self.tableName()] : [],
                    }).then(function (catalogEntry) {
                        catalogEntry.getSourceMeta({ silenceErrors: true }).then(function (sourceMeta) {
                            self.isTargetExisting(self.outputFormat() === 'table' ? !sourceMeta.notFound : (sourceMeta.databases || []).indexOf(self.databaseName()) >= 0);
                            self.isTargetChecking(false);
                        }).catch(function () {
                            self.isTargetExisting(false);
                            self.isTargetChecking(false);
                        })
                    });
                })
            };

            if (name.length === 0) {
                self.isTargetExisting(false);
                self.isTargetChecking(false);
            } else if (self.outputFormat() === 'file') {
                // self.path()
            } else if (self.outputFormat() === 'table' && wizard.isValidDestination()) {
                if (self.tableName() !== '') {
                    self.isTargetExisting(false);
                    self.isTargetChecking(true);
                    checkDbEntryExists();
                } else {
                    self.isTargetExisting(false);
                    self.isTargetChecking(false);
                }
            } else if (self.outputFormat() === 'hbase') {
                // Todo once autocomplete is implemented for hbase
            } else if (self.outputFormat() === 'database' && wizard.isValidDestination()) {
                if (self.databaseName() !== '') {
                    self.isTargetExisting(false);
                    self.isTargetChecking(true);
                    checkDbEntryExists();
                } else {
                    self.isTargetExisting(false);
                    self.isTargetChecking(false);
                }
            } else if (self.outputFormat() === 'index') {
                $.post("/indexer/api/index/list", {
                    name: self.name()
                }, function (data) {
                    self.isTargetExisting(data.status === 0);
                    self.isTargetChecking(false);
                }).fail(function (xhr, textStatus, errorThrown) {
                    self.isTargetExisting(false);
                    self.isTargetChecking(false);
                });
                $.post("/indexer/api/configs/list/", function (data) {
                    if (data.status === 0) {
                        self.indexerConfigSets(data.configs.map(function (config) {
                            return { 'name': config, 'value': config };
                        }));
                    } else {
                        huePubSub.publish('hue.global.error', { message: data.message });
                    }
                });
            }
            resizeElements();
        };
        self.name.subscribe(self.nameChanged);

        self.description = ko.observable('');
        self.outputFormat = ko.observable(wizard.prefill.target_type() || 'table');
        self.outputFormat.subscribe(function (newValue) {
            if (newValue && newValue !== 'database' && ((['table', 'rdbms', 'index'].indexOf(newValue) >= 0) && wizard.source.table().length > 0)) {
                self.nameChanged(self.name());
                wizard.guessFieldTypes();
                resizeElements();
            }
            window.hueAnalytics.log('importer', 'destination-type-selection/' + newValue);
        });
        self.outputFormatsList = ko.observableArray([
            { 'name': 'Table', 'value': 'table' }
        ]);

        if (window.ENABLE_NEW_INDEXER) {
            self.outputFormatsList.push({ 'name': 'Search index', 'value': 'index' });
        }

        self.outputFormatsList.push({ 'name': 'Database', 'value': 'database' });

        if (window.ENABLE_KAFKA) {
            self.outputFormatsList.push({ 'name': 'Stream Table', 'value': 'stream-table' });
            self.outputFormatsList.push({ 'name': 'Stream Topic', 'value': 'stream' });
            self.outputFormatsList.push({ 'name': 'Phoenix Table', 'value': 'big-table' });
        }

        if (window.ENABLE_SQOOP || window.ENABLE_KAFKA) {
            self.outputFormatsList.push({ 'name': 'Folder', 'value': 'file' });
        }

        if (window.ENABLE_ALTUS) {
            self.outputFormatsList.push({ 'name': 'Altus SDX', 'value': 'altus' });
        }

        if (window.ENABLE_SQOOP) {
            self.outputFormatsList.push({ 'name': 'HBase Table', 'value': 'hbase' });
        }

        self.outputFormats = ko.pureComputed(function () {
            return $.grep(self.outputFormatsList(), function (format) {
                if (
                    format.value === 'database' &&
                    wizard.source.inputFormat() !== 'manual' &&
                    (wizard.source.inputFormat() !== 'rdbms' || !wizard.source.rdbmsAllTablesSelected())) {
                    return false;
                }
                if (format.value === 'file' && (
                    wizard.source.inputFormat() === 'stream' ||
                    ['manual', 'rdbms', 'stream'].indexOf(wizard.source.inputFormat()) === -1)) {
                    return false;
                }
                if (format.value === 'index' && (
                    wizard.source.inputFormat() === 'stream' ||
                    ['file', 'query', 'stream'].indexOf(wizard.source.inputFormat()) === -1)) {
                    return false;
                }
                if (format.value === 'table' &&
                    (wizard.source.inputFormat() === 'table' || (
                        wizard.source.inputFormat() === 'rdbms' && wizard.source.rdbmsAllTablesSelected()))) {
                    return false;
                }
                if (format.value === 'altus' && ['table'].indexOf(wizard.source.inputFormat()) === -1) {
                    return false;
                }
                if (format.value === 'stream' &&
                    (wizard.source.inputFormat() === 'stream' || ['file', 'stream'].indexOf(wizard.source.inputFormat()) === -1)) {
                    return false;
                }
                if (format.value === 'stream-table' && ['stream'].indexOf(wizard.source.inputFormat()) === -1) {
                    return false;
                }
                if (format.value === 'big-table' && ['file', 'localfile'].indexOf(wizard.source.inputFormat()) === -1) {
                    return false;
                }
                if (format.value === 'hbase' && (wizard.source.inputFormat() !== 'rdbms' || wizard.source.rdbmsAllTablesSelected())) {
                    return false;
                }
                return true;
            })
        });
        self.outputFormats.subscribe(function (newValue) {
            if (newValue.length && newValue.map(function (entry) { return entry.value; }).indexOf(self.outputFormat()) < 0) {
                self.outputFormat(newValue && newValue[0].value);
            }
        });
        wizard.prefill.target_type.subscribe(function (newValue) {
            // Target_type gets updated by the router (onePageViewModelModel.js) and delaying allow the notification to go through
            setTimeout(function () {
                self.outputFormat(newValue || 'table');
            }, 0);
            if (newValue === 'database') {
                vm.currentStep(2);
            } else {
                vm.currentStep(1);
            }
        });
        self.defaultName = ko.pureComputed(function () {
            var name = '';

            if (['file', 'stream', 'localfile'].indexOf(wizard.source.inputFormat()) != -1) {
                if (['table', 'big-table'].indexOf(self.outputFormat()) != -1) {
                    name = wizard.prefill.target_path().length > 0 ? wizard.prefill.target_path() : 'default';

                    if (wizard.source.inputFormat() === 'stream') {
                        if (wizard.source.streamSelection() === 'kafka') {
                            name += '.' + wizard.source.kafkaSelectedTopics();
                        } else {
                            name += '.' + wizard.source.streamObject();
                        }
                    } else if (wizard.source.path()) {
                        const source_path = wizard.source.path();
                        var database_name = name += '.';
                        if (self.outputFormat() === 'big-table' && wizard.prefill.target_path().length === 0) {
                            database_name = '';
                        }
                        if (wizard.source.inputFormat() === 'localfile') {
                            name = database_name + source_path.substring(source_path.lastIndexOf(':') + 1, source_path.lastIndexOf(';')).split('.')[0];
                        } else {
                            name = database_name + source_path.split('/').pop().split('.')[0];
                        }
                    }
                } else { // Index
                    name = wizard.prefill.target_path().length > 0 ? wizard.prefill.target_path() : wizard.source.path().split('/').pop().split('.')[0];
                }
            } else if (wizard.source.inputFormat() === 'table') {
                name = wizard.source.databaseName();
            } else if (wizard.source.inputFormat() === 'query') {
                if (wizard.source.query()) {
                    name = wizard.source.name();
                }
                if (wizard.prefill.target_path().length > 0) {
                    name = wizard.prefill.target_path();
                }
            } else if (wizard.source.inputFormat() === 'manual') {
                name = wizard.prefill.target_path().length > 0 ? wizard.prefill.target_path() + '.' : '';
            }

            return name.replace(/ /g, '_').toLowerCase();
        });
        self.defaultName.subscribe(function (newVal) {
            self.name(newVal);
        });

        self.format = ko.observable();
        self.columns = ko.observableArray();

        self.namespaces = wizard.namespaces;
        self.namespace = wizard.namespace;
        self.compute = wizard.compute;
        self.targetNamespaceId = ko.observable(self.namespace() ? self.namespace().id : undefined);

        self.namespace.subscribe(function (namespace) {
            if (namespace && namespace.id !== self.targetNamespaceId) {
                self.targetNamespaceId(namespace.id);
            }
        })

        self.targetNamespaceId.subscribe(function (namespaceId) {
            if (namespaceId && (!self.namespace() || self.namespace().id !== namespaceId)) {
                self.namespaces().some(function (namespace) {
                    if (namespaceId === namespace.id) {
                        self.namespace(namespace);
                        return true;
                    }
                })
            }
        });

        // UI
        self.bulkColumnNames = ko.observable('');
        self.showProperties = ko.observable(false);

        self.columns.subscribe(function (newVal) {
            self.bulkColumnNames(newVal.map(function (item) {
                return item.name()
            }).join(','));
        });

        self.processBulkColumnNames = function () {
            var val = self.bulkColumnNames();
            try {
                if (val.indexOf("\"") === -1 && val.indexOf("'") === -1) {
                    val = '"' + val.replace(/,/gi, '","') + '"';
                }
                if (val.indexOf("[") === -1) {
                    val = "[" + val + "]";
                }
                var parsed = JSON.parse(val);
                self.columns().forEach(function (item, cnt) {
                    if ($.trim(parsed[cnt]) !== '') {
                        item.name($.trim(parsed[cnt]));
                    }
                });
            }
            catch (err) {
            }
            $('#fieldsBulkEditor').modal('hide');
        };

        self.isTargetExisting = ko.observable();
        self.isTargetChecking = ko.observable(false);
        self.existingTargetUrl = ko.pureComputed(function () { // Should open generic sample popup instead
            if (self.isTargetExisting()) {
                if (self.outputFormat() === 'file') {
                    // Todo
                    return '';
                }
                if (self.outputFormat() === 'table') {
                    return '/metastore/table/' + self.databaseName() + '/' + self.tableName();
                }
                if (self.outputFormat() === 'database') {
                    return '/metastore/tables/' + self.databaseName();
                }
                if (self.outputFormat() === 'index') {
                    return '/indexer/indexes/' + self.name();
                }
            }
            return '';
        });

        // Table
        self.tableName = ko.pureComputed(function () {
            return self.outputFormat() === 'table' && self.name().indexOf('.') > 0 ? self.name().split('.', 2)[1] : self.name();
        });
        self.databaseName = ko.pureComputed(function () {
            return self.outputFormat() === 'database' ? self.name() : (self.outputFormat() === 'table' && self.name().indexOf('.') > 0 ? self.name().split('.', 2)[0] : 'default');
        });
        self.tableFormat = ko.observable('text');
        self.tableFormat.subscribe(function (value) {
            window.hueAnalytics.log('importer', 'table-format-selection/' + value);
        })
        self.KUDU_DEFAULT_RANGE_PARTITION_COLUMN = { values: [{ value: '' }], name: 'VALUES', lower_val: 0, include_lower_val: '<=', upper_val: 1, include_upper_val: '<=' };
        self.KUDU_DEFAULT_PARTITION_COLUMN = { columns: [], range_partitions: [self.KUDU_DEFAULT_RANGE_PARTITION_COLUMN], name: 'HASH', int_val: 16 };


        self.icebergEnabled = ko.observable(vm.sourceType == 'impala' || vm.sourceType == 'hive');
        self.isIceberg = ko.observable(false);

        self.tableFormats = ko.pureComputed(function () {
            if (wizard.source.inputFormat() === 'stream') {
                return [{ 'value': 'kudu', 'name': 'Kudu' }];
            } else if (vm.sourceType == 'impala') { // Impala supports Kudu
                return [
                    { 'value': 'text', 'name': 'Text' },
                    { 'value': 'parquet', 'name': 'Parquet' },
                    { 'value': 'kudu', 'name': 'Kudu' },
                    { 'value': 'csv', 'name': 'Csv' },
                    { 'value': 'avro', 'name': 'Avro' },
                    { 'value': 'json', 'name': 'Json' },
                    { 'value': 'regexp', 'name': 'Regexp' },
                    { 'value': 'orc', 'name': 'ORC' },
                ];
            }
            return [
                { 'value': 'text', 'name': 'Text' },
                { 'value': 'parquet', 'name': 'Parquet' },
                { 'value': 'csv', 'name': 'Csv' },
                { 'value': 'avro', 'name': 'Avro' },
                { 'value': 'json', 'name': 'Json' },
                { 'value': 'regexp', 'name': 'Regexp' },
                { 'value': 'orc', 'name': 'ORC' },
            ]
        });

        self.partitionColumns = ko.observableArray();
        self.kuduPartitionColumns = ko.observableArray();
        self.primaryKeys = ko.observableArray();
        self.primaryKeyObjects = ko.observableArray();

        self.useFieldEditor = ko.observable(false);
        // TODO: Figure out the database to use for field editor autocomplete
        self.fieldEditorDatabase = ko.observable('default');
        // TODO: Do something with the editor value
        self.fieldEditorValue = ko.observable();
        self.fieldEditorPlaceHolder = ko.observable();
        self.fieldEditorEnabled = ko.pureComputed(function () {
            return window.ENABLE_FIELD_EDITOR;
        });

        self.importData = ko.observable(true);
        self.importData.subscribe(function (val) {
            window.hueAnalytics.log('importer', 'import-data/' + val);
        })
        self.useDefaultLocation = ko.observable(true);
        self.useDefaultLocation.subscribe(function (val) {
            window.hueAnalytics.log('importer', 'default-location/' + val);
        })
        self.nonDefaultLocation = ko.observable('');

        var isTransactionalVisibleImpala = importerOptions.is_transactional;
        var isTransactionalVisibleHive = importerOptions.has_concurrency_support;
        var transactionalDefaultType = importerOptions.default_transactional_type && importerOptions.default_transactional_type.toLowerCase;

        self.isTransactionalVisible = ko.observable((vm.sourceType == 'impala' && isTransactionalVisibleImpala) || (vm.sourceType == 'hive' && isTransactionalVisibleHive));
        self.isTransactional = ko.observable(self.isTransactionalVisible());
        self.isTransactional.subscribe(function (val) {
            window.hueAnalytics.log('importer', 'is-transactional/' + val);
        })
        self.isInsertOnly = ko.observable(true); // Impala doesn't have yet full support.
        self.isTransactionalUpdateEnabled = ko.pureComputed(function () {
            var enabled = self.tableFormat() == 'orc' && (vm.sourceType == 'hive' || (vm.sourceType == 'impala' && transactionalDefaultType.length && transactionalDefaultType != 'insert_only'));
            if (!enabled) {
                self.isInsertOnly(true);
            }
            return enabled;
        });
        self.isIceberg.subscribe(function (val) {
            if (val) {
                self.useDefaultLocation(false);
                self.isTransactional(false);
                if (['avro', 'orc'].indexOf(self.tableFormat()) === -1 || vm.sourceType === 'impala') {
                    self.tableFormat('parquet');
                }
            }
            else {
                self.useDefaultLocation(true);
                self.isTransactional(self.isTransactionalVisible());
                self.tableFormat('text');
            }
            window.hueAnalytics.log('importer', 'is-iceberg/' + val);
        });

        self.useCopy = ko.observable(false);

        self.hasHeader = ko.observable(false);

        self.useCustomDelimiters = ko.observable(false);
        self.customFieldDelimiter = ko.observable(',');
        self.customCollectionDelimiter = ko.observable('\\002');
        self.customMapDelimiter = ko.observable('\\003');
        self.customRegexp = ko.observable('');

        // Index
        self.indexerRunJob = ko.observable(false);
        self.indexerJobLibPath = ko.observable(window.CONFIG_INDEXER_LIBS_PATH);
        self.indexerConfigSet = ko.observable('');
        self.indexerConfigSets = ko.observableArray([]);
        self.indexerNumShards = ko.observable(1);
        self.indexerReplicationFactor = ko.observable(1);
        self.indexerPrimaryKey = ko.observableArray();
        self.indexerPrimaryKeyObject = ko.observableArray();
        self.indexerDefaultField = ko.observableArray();
        self.indexerDefaultFieldObject = ko.observableArray();

        // File, Table, HBase
        self.sqoopJobLibPaths = ko.observableArray([]);
        self.addSqoopJobLibPath = function () {
            var newValue = {
                path: ko.observable('')
            };
            self.sqoopJobLibPaths.push(newValue);
        };
        self.addSqoopJobLibPath();
        self.removeSqoopJobLibPath = function (valueToRemove) {
            self.sqoopJobLibPaths.remove(valueToRemove);
        };
        self.numMappers = ko.observable(1);
        self.customFieldsDelimiter = ko.observable(',');
        self.customLineDelimiter = ko.observable('\\n');
        self.customEnclosedByDelimiter = ko.observable('\'');
        self.rdbmsFileOutputFormat = ko.observable('text');
        self.rdbmsFileOutputFormats = ko.observableArray([
            { 'value': 'text', 'name': 'text' },
            { 'value': 'sequence', 'name': 'sequence' },
            { 'value': 'avro', 'name': 'avro' }
        ]);
        self.rdbmsSplitByColumn = ko.observableArray();

        // Flume
        self.channelSinkTypes = ko.observableArray([
            { 'name': 'This topic', 'value': 'kafka' },
            { 'name': 'Solr', 'value': 'solr' },
            { 'name': 'HDFS', 'value': 'hdfs' }
        ]);
        self.channelSinkType = ko.observable();
        self.channelSinkPath = ko.observable();
    };

    var CreateWizard = function (vm) {
        var self = this;
        var guessFieldTypesXhr;

        self.namespaces = ko.observableArray();
        self.namespace = ko.observable();
        self.compute = ko.observable();

        self.computeSetDeferred = $.Deferred();

        // TODO: Use connectors in the importer
        contextCatalog.getNamespaces({ connector: { id: vm.sourceType } }).then(function (context) {
            self.namespaces(context.namespaces);
            if (!vm.namespaceId || !context.namespaces.some(function (namespace) {
                if (namespace.id === vm.namespaceId) {
                    self.namespace(namespace);
                    return true;
                }
            })) {
                self.namespace(context.namespaces[0]);
            }

            if (!vm.computeId || !self.namespace().computes.some(function (compute) {
                if (compute.id === vm.computeId) {
                    self.compute(compute);
                    return true;
                }
            })) {
                self.compute(self.namespace().computes[0]);
            }
            self.namespace.subscribe(function (namespace) {
                if (!namespace) {
                    self.compute(undefined);
                    return;
                }
                if (!self.compute() || !namespace.computes.some(function (compute) {
                    if (compute.id === self.compute()) {
                        return true;
                    }
                })) {
                    if (namespace.computes.length) {
                        self.compute(namespace.computes[0]);
                    }
                }
            })
            self.computeSetDeferred.resolve();
        }).catch();

        self.fileType = ko.observable();
        self.fileType.subscribe(function (newType) {
            if (self.source.format()) {
                if (self.source.format()?.type() !== newType?.name) {
                    window.hueAnalytics.log('importer', 'file-type-selected/' + newType?.name);
                }
                self.source.format().type(newType.name);
            }
        });

        self.fileTypeName = ko.observable();
        self.fileTypeName.subscribe(function (newType) {
            for (var i = 0; i < self.fileTypes.length; i++) {
                if (self.fileTypes[i].name === newType) {
                    self.fileType(self.fileTypes[i]);
                    break;
                }
            }
        });

        self.operationTypes = JSON.parse(importerOptions.operators_json);

        self.fieldTypes = JSON.parse(importerOptions.fields_json).solr;
        self.hivePrimitiveFieldTypes = JSON.parse(importerOptions.fields_json).hivePrimitive;
        self.hiveFieldTypes = JSON.parse(importerOptions.fields_json).hive
        self.fileTypes = JSON.parse(importerOptions.file_types_json);
        self.prefill = ko.mapping.fromJS(JSON.parse(importerOptions.prefill));

        self.prefill.source_type.subscribe(function (newValue) {
            self.source.inputFormat(newValue ? newValue : 'file');
        });

        self.show = ko.observable(true);
        self.showCreate = ko.observable(false);

        self.source = new Source(vm, self);
        self.destination = new Destination(vm, self);

        self.customDelimiters = ko.observableArray([
            { 'value': ',', 'name': 'Comma (,)' },
            { 'value': '\\t', 'name': '^Tab (\t)' },
            { 'value': '\\n', 'name': 'New line' },
            { 'value': '|', 'name': 'Pipe' },
            { 'value': '\"', 'name': 'Double Quote' },
            { 'value': '\'', 'name': 'Single Quote' },
            { 'value': '\x00', 'name': '^0' },
            { 'value': '\x01', 'name': '^A (\001)' },
            { 'value': '\x02', 'name': '^B (\002)' },
            { 'value': '\x03', 'name': '^C (\003)' },
            { 'value': '\x01', 'name': '^A (\x01)' }
        ]);

        self.editorId = ko.observable();
        self.jobId = ko.observable();
        self.editorVM = null;

        self.indexingStarted = ko.observable(false);

        self.isValidDestination = ko.pureComputed(function () {
            return self.destination.name().length > 0 && (
                (['table', 'database'].indexOf(self.destination.outputFormat()) === -1 || /^([a-zA-Z0-9_]+\.)?[a-zA-Z0-9_]+$/.test(self.destination.name())) &&
                (['index'].indexOf(self.destination.outputFormat()) === -1 || /^[^\\/:]+$/.test(self.destination.name()))
            );
        });
        self.readyToIndex = ko.pureComputed(function () {
            var validFields = self.destination.columns().length || self.destination.outputFormat() === 'database';
            var isValidColumnNames = self.destination.columns().every(function (column) {
                return /^[a-zA-Z0-9_]+$/.test(column.name());
            });

            var validTableColumns = self.destination.outputFormat() !== 'table' || ($.grep(self.destination.columns(), function (column) {
                return column.name().length === 0;
            }).length === 0
                && $.grep(self.destination.partitionColumns(), function (column) {
                    return column.name().length === 0 || (self.source.inputFormat() !== 'manual' && column.partitionValue().length === 0);
                }).length === 0
            );
            var isTargetAlreadyExisting;
            if (self.destination.outputFormat() === 'database' && self.source.inputFormat() === 'rdbms') {
                isTargetAlreadyExisting = self.destination.isTargetExisting();
            } else {
                isTargetAlreadyExisting = !self.destination.isTargetExisting()
                    || self.destination.outputFormat() === 'index'
                    || (self.source.inputFormat() === 'stream' && self.destination.outputFormat() === 'table' && self.destination.tableFormat() === 'kudu')
                    ;
            }
            var isValidTable = ((self.destination.outputFormat() !== 'table' || (
                self.destination.tableFormat() !== 'kudu' || (
                    $.grep(self.destination.kuduPartitionColumns(), function (partition) {
                        return partition.columns().length > 0
                    }
                    ).length === self.destination.kuduPartitionColumns().length && self.destination.primaryKeys().length > 0
                ) && (self.destination.outputFormat() !== 'big-table' || self.destination.primaryKeys().length > 0)
            )
            )
            );
            var validIndexFields = self.destination.outputFormat() !== 'index' || ($.grep(self.destination.columns(), function (column) {
                return !(/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(column.name()) && column.name() !== '_version_');
            }).length === 0
            ) || self.destination.indexerConfigSet();

            var isComputeSelected = self.namespace().computes.length === 0 || self.source.selectedComputeId().length > 0
            return self.isValidDestination() && validFields && validTableColumns && validIndexFields && isTargetAlreadyExisting && isValidTable && isValidColumnNames && isComputeSelected;
        });

        self.formatTypeSubscribed = false;

        self.source.format.subscribe(function () {
            for (var i = 0; i < self.fileTypes.length; i++) {
                if (self.fileTypes[i].name === self.source.format().type()) {
                    self.fileType(self.fileTypes[i]);
                    self.fileTypeName(self.fileTypes[i].name);
                    break;
                }
            }

            if (self.source.format().type) {
                if (!self.formatTypeSubscribed) {
                    self.formatTypeSubscribed = true;
                    self.source.format().type.subscribe(function (newType) {
                        self.source.format(new FileType(newType));
                        self.destination.columns.removeAll();
                        self.guessFieldTypes();
                    });
                }
            }
        });

        self.isGuessingFormat = ko.observable(false);
        self.guessFormat = function () {
            self.isGuessingFormat(true);
            self.destination.columns.removeAll();
            $.post("/indexer/api/indexer/guess_format", {
                "fileFormat": ko.mapping.toJSON(self.source)
            }, function (resp) {
                if (resp.status !== 0) {
                    huePubSub.publish('hue.global.error', { message: resp.message });
                } else {
                    var newFormat = ko.mapping.fromJS(new FileType(resp['type'], resp));
                    self.source.format(newFormat);
                    if (self.source.inputFormat() === 'stream') {
                        if (self.source.streamSelection() === 'kafka') {
                            self.source.kafkaTopics(resp['topics']);
                        } else if (self.source.streamSelection() === 'flume') {
                            self.source.streamObjects(resp['objects']);
                        }
                    } else if (self.source.inputFormat() === 'connector') {
                        // Assumes selectectedConnector == 'sfdc'
                        self.source.streamObjects(resp['objects']);
                    }

                    if (self.source.inputFormat() !== 'stream' && self.source.inputFormat() !== 'connector' &&
                        (['localfile', 'file'].indexOf(self.source.inputFormat()) != -1 && self.source.path() != '')) {
                        self.guessFieldTypes();
                    }
                }

                self.isGuessingFormat(false);
                viewModel.wizardEnabled(true);
            }).fail(function (xhr) {
                huePubSub.publish('hue.global.error', { message: xhr.responseText });
                viewModel.isLoading(false);
                self.isGuessingFormat(false);
            });
        };

        self.isGuessingFieldTypes = ko.observable(false);

        self.guessFieldTypes = function () {
            if (guessFieldTypesXhr) {
                guessFieldTypesXhr.abort();
            }
            self.isGuessingFieldTypes(true);
            guessFieldTypesXhr = $.post("/indexer/api/indexer/guess_field_types", {
                "fileFormat": ko.mapping.toJSON(self.source)
            }, function (resp) {
                self.loadSampleData(resp);
                self.isGuessingFieldTypes(false);
                guessFieldTypesXhr = null;
            }).fail(function (xhr) {
                self.loadSampleData({ sample_cols: [], columns: [], sample: [] });
                huePubSub.publish('hue.global.error', { message: xhr.responseText });
                self.isGuessingFieldTypes(false);
                viewModel.isLoading(false);
                guessFieldTypesXhr = null;
            });
        };
        self.loadSampleData = function (resp) {
            resp.columns.forEach(function (entry, i, arr) {
                if (['table', 'big-table'].indexOf(self.destination.outputFormat()) != -1 && self.source.inputFormat() != 'rdbms') {
                    entry.type = MAPPINGS.get(MAPPINGS.SOLR_TO_HIVE, entry.type, 'string');
                } else if (self.destination.outputFormat() === 'index') {
                    entry.type = MAPPINGS.get(MAPPINGS.HIVE_TO_SOLR, entry.type, entry.type);
                }
                arr[i] = loadField(entry, self.destination, i);
            });
            self.source.sampleCols(resp.sample_cols ? resp.sample_cols : resp.columns);
            self.source.sample(resp.sample);
            self.destination.columns(resp.columns);
            if (self.destination.tableFormat() == 'kudu' && $.grep(resp.columns, function (column) { return column.name() == 'id' }).length > 0) {
                self.destination.primaryKeys(['id']); // Auto select ID column
            }
        };
        self.isIndexing = ko.observable(false);
        self.indexingError = ko.observable(false);
        self.indexingSuccess = ko.observable(false);
        self.destination.indexerRunJob.subscribe(function () {
            self.destination.columns().forEach(function (column) {
                column.operations.removeAll();
            });
        });
        self.operationTypesFiltered = ko.pureComputed(function () {
            var indexerRunJob = self.destination.indexerRunJob();
            return self.operationTypes.filter(function (operation) {
                return indexerRunJob || operation.name === 'split'; // We only support split for now with CSV API
            }).map(function (o) {
                return o.name;
            });
        });
        self.commands = ko.observable([]);
        self.showCommands = function () {
            self.indexFile({ show: true });
        };
        self.indexFile = function (options) {
            var options = options || {};
            if (!self.readyToIndex()) {
                return;
            }
            huePubSub.publish('hide.global.alerts');

            self.indexingStarted(true);
            $.post("/indexer/api/importer/submit", {
                "source": ko.mapping.toJSON(self.source),
                "destination": ko.mapping.toJSON(self.destination),
                "start_time": ko.mapping.toJSON((new Date()).getTime()),
                "show_command": options.show || ''
            }, function (resp) {
                self.indexingStarted(false);
                if (resp.status === 0) {
                    if (resp.history_uuid) {
                        huePubSub.publish('hue.global.info', {
                            message: "Task submitted"
                        });
                        huePubSub.publish('notebook.task.submitted', resp);
                    } else if (resp.on_success_url) {
                        if (resp.pub_sub_url) {
                            huePubSub.publish(resp.pub_sub_url);
                        }
                        huePubSub.publish('hue.global.info', {
                            message: "Creation success"
                        });
                        if (resp.errors && resp.errors.length) {
                            huePubSub.publish('hue.global.warning', {
                                message: "Skipped records: " + resp.errors.join(', ')
                            });
                        }
                        huePubSub.publish('open.link', resp.on_success_url);
                    } else if (resp.commands) {
                        self.commands(resp.commands);
                        $('#showCommandsModal').modal('show');
                    }
                } else {
                    huePubSub.publish('hue.global.error', { message: resp && resp.message ? resp.message : 'Error importing' });
                }
            }).fail(function (xhr) {
                self.indexingStarted(false);
                huePubSub.publish('hue.global.error', { message: xhr.responseText });
            });

            hueAnalytics.log('importer', 'submit/' + self.source.inputFormat() + '/' + self.destination.outputFormat());
        };

        self.removeOperation = function (operation, operationList) {
            operationList.remove(operation);
            hueAnalytics.log('importer', 'step/removeOperation');
        };

        self.addOperation = function (field) {
            field.operations.push(new Operation("split"));
            hueAnalytics.log('importer', 'step/addOperation');
        };

        self.load = function (state) {
            self.source.name(state.name);
            self.source.show(state.show);
            self.source.path(state.path);
            self.destination.columns.removeAll();
            if (state.format && 'type' in state.format) {
                var koFormat = ko.mapping.fromJS(new FileType(state.format.type, state.format));
                self.source.format(koFormat);
            }
            if (state.columns) {
                state.columns.forEach(function (currCol) {
                    self.destination.columns.push(loadField(currCol));
                });
            }
        }
    };

    var loadDefaultField = function (options) {
        if (!options.name) {
            options.name = getNewFieldName();
        }
        return loadField($.extend({}, JSON.parse(importerOptions.default_field_type), options));
    };

    var loadField = function (currField, parent, idx) {
        var koField = ko.mapping.fromJS(currField);
        if (koField.name && parent) {
            koField.name.subscribe(function (newVal) {
                if (newVal.indexOf(',') > -1) {
                    var fields = newVal.split(',');
                    fields.forEach(function (val, i) {
                        if (i + idx < parent.columns().length) {
                            parent.columns()[i + idx].name(val);
                        }
                    });
                }
                parent.bulkColumnNames(parent.columns().map(function (item) {
                    return item.name()
                }).join(','));
            });
        }

        koField.operations.removeAll();

        currField.operations.forEach(function (operationData) {
            var operation = new Operation(operationData.type);
            operation.load(operationData);

            koField.operations.push(operation);
        });

        var autoExpand = function (newVal) {
            if ((newVal === 'array' || newVal === 'map' || newVal === 'struct') && koField.nested().length === 0) {
                koField.nested.push(loadDefaultField({ level: koField.level() + 1 }));
            }
        };
        koField.type.subscribe(autoExpand);
        koField.keyType.subscribe(autoExpand);

        return koField;
    };

    var IndexerViewModel = function () {
        var self = this;

        self.apiHelper = window.apiHelper;
        self.sourceType = hueUtils.getParameter('sourceType', true) || importerOptions.source_type
        self.namespaceId = hueUtils.getParameter('namespace', true);
        self.computeId = hueUtils.getParameter('compute', true);

        self.assistAvailable = ko.observable(true);
        self.isLeftPanelVisible = ko.observable();
        window.hueUtils.withLocalStorage('assist.assist_panel_visible', self.isLeftPanelVisible, true);
        self.isLeftPanelVisible.subscribe(function () {
            huePubSub.publish('assist.forceRender');
        });
        self.loadDefaultField = loadDefaultField;

        self.createWizard = new CreateWizard(self);

        // Wizard related
        self.wizardEnabled = ko.observable(false);
        self.currentStep = ko.observable(self.createWizard.prefill.target_type() === 'database' ? 2 : 1);
        self.currentStep.subscribe(function () {
            $('.page-content').scrollTop(0);
        });
        self.previousStepVisible = ko.pureComputed(function () {
            return self.currentStep() > 1 && (self.createWizard.destination.outputFormat() !== 'database' || self.createWizard.source.inputFormat() === 'rdbms');
        });
        self.nextStepVisible = ko.pureComputed(function () {
            return self.currentStep() < 3 && self.wizardEnabled();
        });
        self.nextStep = function () {
            if (self.nextStepVisible()) {
                self.currentStep(self.currentStep() + 1);
                hueAnalytics.log('importer', 'step/' + self.currentStep());
            }
        };
        self.previousStep = function () {
            if (self.previousStepVisible()) {
                self.currentStep(self.currentStep() - 1);
                window.hueAnalytics.log('importer', 'back-btn-click/' + self.createWizard?.source?.inputFormat());
            }
        };

        self.isLoading = ko.observable(false);

    };

    var viewModel;

    function resizeElements() {
        var $contentPanel = $('#importerComponents').find('.content-panel-inner');
        $('.step-indicator-fixed').width($contentPanel.width());
        document.styleSheets[0].addRule('.form-actions', 'margin-left: -11px !important');
        document.styleSheets[0].addRule('.step-indicator li:first-child:before', 'max-width: ' + ($contentPanel.find('.step-indicator li:first-child .caption').width()) + 'px');
        document.styleSheets[0].addRule('.step-indicator li:first-child:before', 'left: ' + ($contentPanel.find('.step-indicator li:first-child .caption').width() / 2) + 'px');
        document.styleSheets[0].addRule('.step-indicator li:last-child:before', 'max-width: ' + ($contentPanel.find('.step-indicator li:last-child .caption').width()) + 'px');
        document.styleSheets[0].addRule('.step-indicator li:last-child:before', 'right: ' + ($contentPanel.find('.step-indicator li:last-child .caption').width() / 2) + 'px');
    }

    $(document).ready(function () {
        viewModel = new IndexerViewModel();
        ko.applyBindings(viewModel, $('#importerComponents')[0]);


        var draggableMeta = {};
        huePubSub.subscribe('draggable.text.meta', function (meta) {
            draggableMeta = meta;
        });

        huePubSub.subscribe('importer.show.bulkeditor', function (meta) {
            $('#fieldsBulkEditor').modal('show');
        }, 'importer');

        huePubSub.subscribe('split.panel.resized', resizeElements);

        hueUtils.waitForRendered('.step-indicator li:first-child .caption', function (el) { return el.width() < $('#importerComponents').find('.content-panel-inner').width() / 2 }, resizeElements);

        $(window).on('resize', resizeElements);

        document.getElementById('inputfile').onclick = function () {
            this.value = null;
        };

        document.getElementById('inputfile').onchange = function () {
            upload();
        };

        function upload() {
            var fd = new FormData();
            var files = $('#inputfile')[0].files[0];
            fd.append('file', files);
            var file_size = files.size;
            if (file_size === 0) {
                huePubSub.publish('hue.global.warning', {
                    message: "This file is empty, please select another file."
                });
            }
            else if (file_size > 200 * 1024) {
                huePubSub.publish('hue.global.warning', {
                    message: "File size exceeds the supported size (200 KB). Please use the S3, ABFS or HDFS browser to upload files."
                });
            } else {
                $.ajax({
                    url: "/indexer/api/indexer/upload_local_file",
                    type: 'post',
                    data: fd,
                    contentType: false,
                    cache: false,
                    processData: false,
                    success: function (response) {
                        viewModel.createWizard.source.path(response['local_file_url']);
                        viewModel.createWizard.source.file_type(response['file_type']);
                    }
                });
            }
        };

        $('.importer-droppable').droppable({
            accept: ".draggableText",
            drop: function (e, ui) {
                var text = ui.helper.text();
                var generatedName = 'idx';
                switch (draggableMeta.type) {
                    case 'sql':
                        if (draggableMeta.table !== '') {
                            generatedName += draggableMeta.table;
                            viewModel.createWizard.source.inputFormat('table');
                            viewModel.createWizard.source.table(draggableMeta.table);
                        }
                        break;
                    case 'hdfs':
                        generatedName += draggableMeta.definition.name;
                        viewModel.createWizard.source.inputFormat('file');
                        viewModel.createWizard.source.path(draggableMeta.definition.path);
                        break;
                    case 'document':
                        if (draggableMeta.definition.type === 'query-hive') {
                            generatedName += draggableMeta.definition.name;
                            viewModel.createWizard.source.inputFormat('query');
                            viewModel.createWizard.source.draggedQuery(draggableMeta.definition.uuid);
                        }
                        break;
                }
                if (generatedName !== 'idx' && viewModel.createWizard.source.name() === '') {
                    viewModel.createWizard.source.name(generatedName);
                }
            }
        });
    });
})();