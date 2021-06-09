
# SQL Editor for Spark SQL via Livy

## Background

* https://spark.apache.org/docs/latest/sql-programming-guide.html
* https://docs.gethue.com/user/querying/#spark

As detailed in the documentation, Spark SQL comes with different [connectors](https://docs.gethue.com/administrator/configuration/connectors/#apache-spark-sql). Here we will just show with Livy.

[Apache Livy](https://livy.incubator.apache.org/) provides a bridge to a running Spark interpreter so that SQL, pyspark and scala snippets can be executed interactively.

In the hue.ini configure the API url:

    [spark]
    # The Livy Server URL.
    livy_server_url=http://localhost:8998

And as always, make sure you have an interpreter configured:

    [notebook]
    [[interpreters]]
    [[[sparksql]]]
    name=Spark SQL
    interface=livy

And that's it, the editor will appear:

![Hue Spark Sql Editor](https://cdn.gethue.com/uploads/2020/04/editor_spark_sql_livy.png)

One advantage of using Hue is its [File Browser](https://docs.gethue.com/user/browsing/#data) for HDFS / S3 / Azure and full security.

![Hue Phoenix Editor](https://cdn.gethue.com/uploads/2016/08/image2.png)

### Future improvements

* Database/table/column autocomplete is currently empty
* SQL grammar autocomplete can [be extended](https://docs.gethue.com/developer/development/#sql-parsers)
* [SQL Scratchpad](https://docs.gethue.com/developer/api/#scratchpad) module to allow a mini SQL Editor popup is in progress
