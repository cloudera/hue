# Connectors

Goal: [HUE-8758](https://issues.cloudera.org/browse/HUE-8758)
Configuration of external services via an interface and API instead of hue.ini.


## Apps and Connectors

In Hue 4, apps and dialects are combined into the same configuration.

Desktop + apps and Connectors

* Apps: editor, notebook, filebrowser, jobbrowser, metastore, importer, home
* Connectors: impala, hive, hive-llap, mysql...
* Connections: Impala Cluster1, MySql Analytics

Each app is using instances of connectors which represent a connection. For example the Editor App
can point to several MySql servers.

## Permissions

Before there was app level permissions, and one language (e.g. Hive) was associated to an app.

Now the goal is to be able to add your own connector instance in a self service way without any Hue restart.
The instance is restricted with a corresponding Permission object.

* HuePermission --> ConnectorPermission / OrganizationConnectorPermission

**Note**
Out of scope but to keep in mind

* AWS, Apache ranger permissions: HuePermission --> OrganizationAwsPermission, OrganizationRangerPermission ...
* HuePermission (e.g. specific settings to assign to a group, like download limit, superuser group...)

## Connectors

### HMS

Activate "Tables" app when there is at least one.
Add "catalog" connectors. e.g. SQL connectors, HMS, Metadata catalogs...

### Storages

Multiple S3s configs, need "namespaces" or list of keys.
