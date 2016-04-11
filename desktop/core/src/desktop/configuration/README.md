# DefaultConfiguration API
## API Endpoints

* [/desktop/api/configurations/apps/](#get_configurable_apps)
* [/desktop/api/configurations/user/](#get_default_configuration_for_user)
* [/desktop/api/configurations/save/](#save_default_configuration)
* [desktop/api/configurations/delete/](#delete_default_configuration)

### <a name="get_configurable_apps"></a> GET /desktop/api/configurations/apps
Returns a JSON response with `status` and `apps` where apps contains a dictionary of all configurable apps and their defined configuration, as well as any default and group saved configurations.

Each record in `apps` will map to a dictionary that contains a **required** `properties` record which maps to a list of defined properties for the app. Optionally, the app may also contain a `default` list of properties, and/or `group` properties where each configured group ID is returned with corresponding properties.

#### Example Request
GET /desktop/api/configurations/apps

#### Example Response
```
{
    "status": 0,
    "apps": {
        "impala": {
            "properties": [
                {
                    "multiple": true,
                    "value": [],
                    "nice_name": "Settings",
                    "key": "settings",
                    "help_text": "Impala configuration properties.",
                    "type": "settings",
                    "options": [
                        "debug_action",
                        "explain_level",
                        "mem_limit",
                        "optimize_partition_key_scans",
                        "query_timeout_s"
                    ]
                }
            ]
        },
        "hive": {
            "properties": [
                {
                    "multiple": true,
                    "value": [],
                    "nice_name": "Files",
                    "key": "files",
                    "help_text": "Add one or more files, jars, or archives to the list of resources.",
                    "type": "hdfs-files"
                },
                {
                    "multiple": true,
                    "value": [],
                    "nice_name": "Functions",
                    "key": "functions",
                    "help_text": "Add one or more registered UDFs (requires function name and fully-qualified class name).",
                    "type": "functions"
                },
                {
                    "multiple": true,
                    "value": [],
                    "nice_name": "Settings",
                    "key": "settings",
                    "help_text": "Hive and Hadoop configuration properties.",
                    "type": "settings",
                    "options": [
                        "hive.map.aggr",
                        "hive.exec.compress.output",
                        "hive.exec.parallel",
                        "hive.execution.engine",
                        "mapreduce.job.queuename"
                    ]
                }
            ],
            "default": [
                {
                    "multiple": true,
                    "value": [],
                    "nice_name": "Files",
                    "key": "files",
                    "help_text": "Add one or more files, jars, or archives to the list of resources.",
                    "type": "hdfs-files"
                },
                {
                    "multiple": true,
                    "value": [],
                    "nice_name": "Functions",
                    "key": "functions",
                    "help_text": "Add one or more registered UDFs (requires function name and fully-qualified class name).",
                    "type": "functions"
                },
                {
                    "multiple": true,
                    "value": [
                        {
                            "mapreduce.job.queuename": "mr"
                        }
                    ],
                    "nice_name": "Settings",
                    "key": "settings",
                    "help_text": "Hive and Hadoop configuration properties.",
                    "type": "settings",
                    "options": [
                        "hive.map.aggr",
                        "hive.exec.compress.output",
                        "hive.exec.parallel",
                        "hive.execution.engine",
                        "mapreduce.job.queuename"
                    ]
                }
            ],
            "groups": {
                "1": [
                    {
                        "multiple": true,
                        "value": [
                            {
                                "path": "/user/test/myudfs.jar",
                                "type": "jar"
                            }
                        ],
                        "nice_name": "Files",
                        "key": "files",
                        "help_text": "Add one or more files, jars, or archives to the list of resources.",
                        "type": "hdfs-files"
                    },
                    {
                        "multiple": true,
                        "value": [
                            {
                                "class_name": "org.hue.udf.MyUpper",
                                "name": "myUpper"
                            }
                        ],
                        "nice_name": "Functions",
                        "key": "functions",
                        "help_text": "Add one or more registered UDFs (requires function name and fully-qualified class name).",
                        "type": "functions"
                    },
                    {
                        "multiple": true,
                        "value": [
                            {
                                "key": "mapreduce.job.queuename",
                                "value": "mr"
                            }
                        ],
                        "nice_name": "Settings",
                        "key": "settings",
                        "help_text": "Hive and Hadoop configuration properties.",
                        "type": "settings",
                        "options": [
                            "hive.map.aggr",
                            "hive.exec.compress.output",
                            "hive.exec.parallel",
                            "hive.execution.engine",
                            "mapreduce.job.queuename"
                        ]
                    }
                ]
            }
        }
    }
}
```


### <a name="get_default_configuration_for_user"></a> GET /desktop/api/configurations/user
Returns a JSON response with configuration for a given `app` type and user designated by `user_id`.

If no saved configuration is found in the DB (i.e. - no default, group or user specific saved configuration), null is returned.

#### Example Request
GET /desktop/api/configurations/user

#### Example Response
TODO: write me


### <a name="save_default_configuration"></a> POST /desktop/api/configurations/save/
Saves a configuration for either `default` (all users), a specific `group` designated by `group_id` or a specific `user` designated by `user_id`.

#### Parameters

* (**Required**) app: app type (e.g. - hive, impala, jdbc, etc.)
* (**Required**) properties: JSON of saved properties
* (**Optional**) is_default: boolean indicating if this is a default configuration or not
* (**Optional**) group_id: group ID if this is a saved configuration for a specific group
* (**Optional**) user_id: user ID if this is a saved configuration for a specific user

Either `is_default`, `group_id` or `user_id` must be passed


#### Example Request
POST /desktop/api/configurations/apps

```
{
    "app": "hive",
    "group_id": 1,
    "properties": [
        {
            "multiple": true,
            "value": [
                {
                    "path": "/user/test/myudfs.jar",
                    "type": "jar"
                }
            ],
            "nice_name": "Files",
            "key": "files",
            "help_text": "Add one or more files, jars, or archives to the list of resources.",
            "type": "hdfs-files"
        },
        {
            "multiple": true,
            "value": [
                {
                    "class_name": "org.hue.udf.MyUpper",
                    "name": "myUpper"
                }
            ],
            "nice_name": "Functions",
            "key": "functions",
            "help_text": "Add one or more registered UDFs (requires function name and fully-qualified class name).",
            "type": "functions"
        },
        {
            "multiple": true,
            "value": [
                {
                    "key": "mapreduce.job.queuename",
                    "value": "mr"
                }
            ],
            "nice_name": "Settings",
            "key": "settings",
            "help_text": "Hive and Hadoop configuration properties.",
            "type": "settings",
            "options": [
                "hive.map.aggr",
                "hive.exec.compress.output",
                "hive.exec.parallel",
                "hive.execution.engine",
                "mapreduce.job.queuename"
            ]
        }
    ]
}
```

#### Example Response
```
{
    "status": 0,
    "configuration": {
        "is_default": false,
        "app": "hive",
        "group": "default",
        "properties": [
            {
                "multiple": true,
                "value": [
                    {
                        "path": "/user/test/myudfs.jar",
                        "type": "jar"
                    }
                ],
                "nice_name": "Files",
                "key": "files",
                "help_text": "Add one or more files, jars, or archives to the list of resources.",
                "type": "hdfs-files"
            },
            {
                "multiple": true,
                "value": [
                    {
                        "class_name": "org.hue.udf.MyUpper",
                        "name": "myUpper"
                    }
                ],
                "nice_name": "Functions",
                "key": "functions",
                "help_text": "Add one or more registered UDFs (requires function name and fully-qualified class name).",
                "type": "functions"
            },
            {
                "multiple": true,
                "value": [
                    {
                        "key": "mapreduce.job.queuename",
                        "value": "mr"
                    }
                ],
                "nice_name": "Settings",
                "key": "settings",
                "help_text": "Hive and Hadoop configuration properties.",
                "type": "settings",
                "options": [
                    "hive.map.aggr",
                    "hive.exec.compress.output",
                    "hive.exec.parallel",
                    "hive.execution.engine",
                    "mapreduce.job.queuename"
                ]
            }
        ],
        "user": null
    }
}
```

### <a name="delete_default_configuration"></a> GET /desktop/api/configurations/delete
TODO: Write me

#### Example Request
GET /desktop/api/configurations/delete

#### Example Response
TODO: write me