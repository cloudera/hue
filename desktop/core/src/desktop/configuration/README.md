# DefaultConfiguration API
## API Endpoints

### [Default and Group Configurations](#default_and_group_configurations)
* GET [/desktop/api/configurations/](#default_configurations)
* POST [/desktop/api/configurations/](#update_default_group_configurations)

### [User-Specific Configuration for App](#user_specific_configuration)

* GET [/desktop/api/configurations/user/](#app_configuration_for_user)
* POST [/desktop/api/configurations/user/](#save_app_configuration_for_user)

### Delete a Saved Configuration

* POST [desktop/api/configurations/delete/](#delete_default_configuration)

----

## <a name="default_and_group_configurations"></a> Default and Group Configurations

### <a name="default_configurations"></a> GET /desktop/api/configurations/
**Returns all configurable apps and their defined, default, and group configurations**

Returns a JSON response with `status` and `configuration` where configuration contains a dictionary of all configurable apps and their defined configuration, as well as any default and group saved configurations.

Each record in `configuration` will map to a dictionary that contains a **required** `properties` record which maps to a list of defined properties for the app. Optionally, the app may also contain a `default` list of properties, and/or `group` properties where each object includes a list of group ID with corresponding properties.

#### Example Request
GET /desktop/api/configurations/

##### Parameters:
None

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
            "groups": [
                {
                    "group_ids": [1, 2],
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
                },
                {
                    "group_ids": [3, 4, 5],
                    "properties": [
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
            ]
        }
    }
}
```

### <a name="update_default_group_configurations"></a> POST /desktop/api/configurations/
**Override (delete and replace) all default and group configurations with the updated configuration sent in request**

Assumes that the `configuration` parameter contains a JSON of all apps and their new `default` and `groups` configurations.
Only processes `default` and `groups`; ignores the defined `properties` and `users` if they are in the `configuration` object.

#### Parameters

* (**Required**) configuration: JSON dictionary where the key is the app name and the value is another dictionary that can contain `default` and/or `groups` properties. If no `default` or `groups` keys are found, all saved default and group configurations are deleted without replacement.


#### Example Request
POST /desktop/api/configurations/

```
"configuration": {
    "hive": {
        "default": [
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
                "help_text": "Add one or more registered UDFs (requires function name and fully-qualified classname).",
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
```

#### Example Response
```
{
    "status": 0,
    "configuration": {
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
```

----

## <a name="user_specific_configuration"></a> User-Specific Configuration for App
### <a name="app_configuration_for_user"></a> GET /desktop/api/configurations/user/
** Returns the configuration that should be used for a given user and app. Checks in order of user, group, default precedence. **

#### Parameters

* (**Required**) app: app type (e.g. - hive, impala, jdbc, etc.)
* (**Required**) user_id: User ID for user


#### Example Request
GET /desktop/api/configurations/user/?app=hive&user_id=1

#### Example Response

```
{
    "status": 0,
    "configuration": {
        "is_default": false,
        "app": "hive",
        "groups": [1],
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


### <a name="save_app_configuration_for_user"></a> POST /desktop/api/configurations/user/
Saves a single configuration for a specific `user` designated by `user_id` and `app`. This will create or update an existing user-specific configuration.

#### Parameters

* (**Required**) app: app type (e.g. - hive, impala, jdbc, etc.)
* (**Required**) properties: JSON of saved properties
* (**Required**) user_id: user ID if this is a saved configuration for a specific user

`properties` is the properties list, NOT the full `configuration` JSON


#### Example Request
POST /desktop/api/configurations/user

```
{
    "app": "hive",
    "user_id": 1,
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
        "groups": [],
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
        "user": 1
    }
}
```

---


### <a name="delete_default_configuration"></a> GET /desktop/api/configurations/delete
TODO: Write me

#### Example Request
GET /desktop/api/configurations/delete

#### Example Response
TODO: write me