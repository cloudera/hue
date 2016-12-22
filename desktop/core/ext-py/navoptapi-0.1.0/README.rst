Cloudera Navigator Optimizer Api SDK
==============================================

This package provides a API SDK for Cloudera Navigator Optimizer.

Install the package
====================
sudo pip install navoptapi-0.1.0.tar.gz

Example Usage for the Api
=========================

* Import the module
  from navoptapi.api_lib import *

* Create NavOpt object passing hostname, access key and private key:
  nav = ApiLib("navopt", "121.0.0.1", "e0819f3a-1e6f-4904-be69-5b704b299bbb", "-----BEGIN PRIVATE KEY-----\n..............\n-----END PRIVATE KEY-----")

* Get Top Tables for a workload:
  resp = nav.call_api("getTopTables", {"tenant" : "d6d54b73-2bab-e413-5376-a805f5d4ae53"})
  print json.dumps(resp.json(), indent=2)

* Get Top Databases for a workload:
  resp = nav.call_api("getTopDataBases", {"tenant" : "d6d54b73-2bab-e413-5376-a805f5d4ae53"})
  print json.dumps(resp.json(), indent=2)

* Get Top Queries for a workload:
    resp = nav.call_api("getTopQueries", {"tenant" : "d6d54b73-2bab-e413-5376-a805f5d4ae53"})
    print json.dumps(resp.json(), indent=2)

* Get Top Columns for a workload:
    resp = nav.call_api("getTopColumns", {"tenant" : "d6d54b73-2bab-e413-5376-a805f5d4ae53", "dbTableList":["default.sample_07"]})
    print json.dumps(resp.json(), indent=2)

* Get Top Filters for a workload:
    resp = nav.call_api("getTopFilters", {"tenant" : "d6d54b73-2bab-e413-5376-a805f5d4ae53", "dbTableList":["default.sample_07"]})
    print json.dumps(resp.json(), indent=2)

* Get Top Aggregates for a workload:
    resp = nav.call_api("getTopAggs", {"tenant" : "d6d54b73-2bab-e413-5376-a805f5d4ae53", "dbTableList":["default.sample_07"]})
    print json.dumps(resp.json(), indent=2)

* Get Top Joins for a workload:
    resp = nav.call_api("getTopJoins", {"tenant" : "d6d54b73-2bab-e413-5376-a805f5d4ae53", "dbTableList":["default.sample_07"]})
    print json.dumps(resp.json(), indent=2)

* Get Query Compatibility:
    resp = nav.call_api("getQueryCompatible", {"tenant" : "d6d54b73-2bab-e413-5376-a805f5d4ae53", "query":"select supplier.s_acctbal, supplier.s_name, nation.n_name, part.p_partkey, part.p_mfgr, supplier.s_address, supplier.s_phone, supplier.s_comment from part, supplier, partsupp, nation, region where part.p_partkey = partsupp.ps_partkey and supplier.s_suppkey = partsupp.ps_suppkey and part.p_size = 15 and part.p_type like '%BRASS' and supplier.s_nationkey = nation.n_nationkey and nation.n_regionkey = region.r_regionkey and region.r_name = 'EUROPE' and partsupp.ps_supplycost = ( select min(partsupp.ps_supplycost) from partsupp, supplier, nation, region where part.p_partkey = partsupp.ps_partkey and supplier.s_suppkey = partsupp.ps_suppkey and supplier.s_nationkey = nation.n_nationkey and nation.n_regionkey = region.r_regionkey and region.r_name = 'EUROPE' ) order by supplier.s_acctbal desc, nation.n_name, supplier.s_name, part.p_partkey", "sourcePlatform":"teradata", "targetPlatform":"hive"})
    print json.dumps(resp.json(), indent=2)

* Get Query Risk Analysis:
    resp = nav.call_api("getQueryRisk", {"tenant" : "d6d54b73-2bab-e413-5376-a805f5d4ae53", "query": "select * from web_logs limit 10"})
    print json.dumps(resp.json(), indent=2)

