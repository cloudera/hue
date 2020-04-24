![alt text](https://raw.githubusercontent.com/cloudera/hue/master/docs/images/hue_logo.png "Hue Logo")

High Level Roadmap
------------------

* Better [SQL parsers](https://docs.gethue.com/developer/parsers/) for [Databases](https://docs.gethue.com/administrator/configuration/connectors/):
    * [Apache Calcite](https://calcite.apache.org) based: Phoenix, Druid, Spark SQL, Presto, Flink SQL..
    * Kafka SQL
    * Elastic Search SQL
    * Solr SQL
    * PartiQl
    * ZetaSql...

* Editor
  * [ ] Editor v2 [HUE-8768](https://issues.cloudera.org/browse/HUE-8768)
  * [ ] Query Browser v2
  * [ ] Query Scheduling [HUE-3797](https://issues.cloudera.org/browse/HUE-3797)
  * [ ] Query Builder [HUE-3228](https://issues.cloudera.org/browse/HUE-3228)
  * [ ] Public SQL REST APIs [HUE-1450](https://issues.cloudera.org/browse/HUE-1450)
* Cloud
  * [ ] Configuration of connectors via UI [HUE-8758](https://issues.cloudera.org/browse/HUE-8758)
  * [ ] Multi clusters [HUE-8330](https://issues.cloudera.org/browse/HUE-8330)
  * [ ] Multi tenants [HUE-8530](https://issues.cloudera.org/browse/HUE-8530)
  * [ ] SQL queries and requests tracing [HUE-8936](https://issues.cloudera.org/browse/HUE-8936)
  * [ ] Productionize metrics [HUE-9021](https://issues.cloudera.org/browse/HUE-9021)
  * [ ] Google Storage connector [HUE-8978](https://issues.cloudera.org/browse/HUE-8978)
* Collaboration
  * [ ] Document sharing improvements [HUE-8790](https://issues.cloudera.org/browse/HUE-8790)
  * [ ] Charting and visualization revamp [HUE-6093](https://issues.cloudera.org/browse/HUE-6093)
  * [ ] Result Sharing (Google Spreadsheet, Slack...)
* Core
  * [ ] Task Server workers [HUE-8738](https://issues.cloudera.org/browse/HUE-8738)
  * [ ] Result caching and storage [HUE-8787](https://issues.cloudera.org/browse/HUE-8787)
  * [ ] Reference architecture [HUE-8815](https://issues.cloudera.org/browse/HUE-8815)
  * [ ] Python 3 support [HUE-8737](https://issues.cloudera.org/browse/HUE-8737)
  * [ ] Gunicorn [HUE-8739](https://issues.cloudera.org/browse/HUE-8739)
  * [ ] Integrate with Apache Ranger [HUE-8748](https://issues.cloudera.org/browse/HUE-8748)
  * [ ] Git integration [HUE-951](https://issues.cloudera.org/browse/HUE-951)


Done

* [x] Additional/Improved SQL autocompletes [HUE-9084](https://issues.cloudera.org/browse/HUE-9084)
* [x] Generify risk alert and optimization API [HUE-8824](https://issues.cloudera.org/browse/HUE-8824)
* [x] Kubernetes [HUE-8744](https://issues.cloudera.org/browse/HUE-8744)
* [x] Minimal Continuous Integration [Blog post](http://gethue.com/improving-the-developer-productivity-with-some-continuous-integration/)
* [x] Integrate with Apache Atlas [HUE-8749](https://issues.cloudera.org/browse/HUE-8749)
* [x] Integrate with Apache Knox [HUE-8750](https://issues.cloudera.org/browse/HUE-8750)
* [x] Integrate with Apache Hive LLAP [HUE-8887](https://issues.cloudera.org/browse/HUE-8887)
* [x] Docker [HUE-8743](https://issues.cloudera.org/browse/HUE-8743)
* [x] Web Server [NGINX](http://gethue.com/using-nginx-to-speed-up-hue-3-8-0/)
* [x] Documentation refresh [HUE-8741](https://issues.cloudera.org/browse/HUE-8741)
* [x] Frontend moved to Webpack [HUE-8687](https://issues.cloudera.org/browse/HUE-8687)
* [x] SQL Alchemy full support [HUE-8740](https://issues.cloudera.org/browse/HUE-8740)
* [x] Modernize CI/CD [HUE-8888](https://issues.cloudera.org/browse/HUE-8888)

Links

* [Open Tasks](https://issues.cloudera.org/projects/HUE/issues)
* [Designs](/docs/designs)
* How to [contribute](/CONTRIBUTING.md)
