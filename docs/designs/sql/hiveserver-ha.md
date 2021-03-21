
# HiveServer HA discovery and failover

A list of the available HiveServers [can be read](https://docs.cloudera.com/HDPDocuments/HDP3/HDP-3.1.5/fault-tolerance/content/configuring_hiveserver2_high_availability_using_zookeeper.html) from Apache Zookeeper. This enables dynamic configuration as well as managing failovers.

## Discovery only

As of today when the option is enabled one HiveServer is read. Hue use Service Discovery for LLAP (Hive Server Interactive) and/or Hiveserver2, this will override server and thrift port:

An initial upstream contribution [HUE-8887](https://issues.cloudera.org/browse/HUE-8887) offered a first version but its 100% robustness was not validated.

Some potential improvements:

* Simplify the number of parameters and code paths of `get_query_server_config()`
* HA failover support (with/without cache timeout)
  * Selected HiveServer2 cache is cleared after a 60s default timeout)
  * User Client reset (`cache_timeout=60` resets the cache but not the user client)
  * Connector support
* Document the feature
* Add more tests

A fraction of all the ini properties:

    # Whether to use Service Discovery for LLAP
    ## hive_discovery_llap = true

    # is llap (hive server interactive) running in an HA configuration (more than 1)
    # important as the zookeeper structure is different
    ## hive_discovery_llap_ha = false

    # Whether to use Service Discovery for HiveServer2
    ## hive_discovery_hs2 = true

    # Shortcuts to finding LLAP znode Key
    # Non-HA - hiveserver-interactive-site - hive.server2.zookeeper.namespace ex hive2 = /hive2
    # HA-NonKerberized - <llap_app_name>_llap ex app name llap0 = /llap0_llap
    # HA-Kerberized - <llap_app_name>_llap-sasl ex app name llap0 = /llap0_llap-sasl
    ## hive_discovery_llap_znode = /hiveserver2-hive2

    # Whether to use Service Discovery for HiveServer2
    ## hive_discovery_hs2 = true

    # Hiveserver2 is hive-site hive.server2.zookeeper.namespace ex hiveserver2 = /hiverserver2
    ## hive_discovery_hiveserver2_znode = /hiveserver2

    # Applicable only for LLAP HA
    # To keep the load on zookeeper to a minimum
    # ---- we cache the LLAP activeEndpoint for the cache_timeout period
    # ---- we cache the hiveserver2 endpoint for the length of session
    # configurations to set the time between zookeeper checks
    ## cache_timeout = 60


A different interpreter for LLAP:

    [notebook]

    [[interpreters]]

    [[[hive]]]
    name=Hive
    interface=hiveserver2

    [[[llap]]]
    name=LLAP
    interface=hiveserver2

Note: not sure about what specific with [LLAP HA](https://docs.cloudera.com/HDPDocuments/HDP3/HDP-3.1.5/performance-tuning/content/hive_setup_multiple_hsi.html).

## Improvements

* There are currently two caches to properly invalidate.
* Keep current design to have all users of a certain Hive connector point to the exact same HiveServer host (not multiplexing).
* When a failover occurs, all users will lose their current sessions.
* As locking should be avoided but in case of concurrent users, the newly selected server should be consistent (or add a locking?)

Two caches in [dbms.py](https://github.com/cloudera/hue/blob/master/apps/beeswax/src/beeswax/server/dbms.py#L62):

    DBMS_CACHE = {}
    cache = caches[CACHES_HIVE_DISCOVERY_KEY]

    # This cache is persistent on startup and we reset the hiveserver2 host.
    def reset_ha():
      cache.clear()

Questions:

* do we want to reset all the clients at the same time: probably yes, if we decided to fail over all connections to the previous HiveServer should be dropped anyway.

### Manual HA

One possibiliy would be to require a user Hue page refresh or close of connection and clear the caches in the call. This would be for an immediate solution for the short term.

Advantage:

* Simpler to implement (no need of auto retry logic)

Disadvantage:

* Poor experience, not seamless (user will see an error and would need to be told to refresh the page)
* Still 80% core of logic needs to be 100% correct
* No refactoring

### Automated HA

If the proper exception messages can be gathered, it would be possible to

* Still need to tell the user that the current queries are lost (if any currently running only?)
* Session listing is not currently refreshed (more minor)

Note that the client is being passed down into the Thrift lib, so resetting needs to be done at the top level (`Notebook API` probably).

Some code paths are still going via the `beeswax` API directly ad might shortcut it. One way would be to gradually support it everywhere:

* Editor only
* Else where (install examples, is alive checks...)

* Each Hue API server could potentially watch the znode for changes instead of trying to guess when a failover occured
* Multiple Hue servers handle their own HiveServer independently of each others
* Task Servers handle their own HiveServer independently of each others

## Tests

Add tests (with the help of the Mock module) to check if:

* Discovery --> pick up from the ZooKeeper list
* Discovery with security --> pick up from the ZooKeeper list
* Single usage with failover --> No deadlock and picking a new HiveServer
* Failover with no available HA server --> Proper error message
* Concurrent usage with failover --> No deadlock and not overriding newly selected HiveServer
