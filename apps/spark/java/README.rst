Welcome to Livy, the REST Spark Server
======================================

Livy is an open source REST interface for interacting with a remote Spark Shell
running locally or from inside YARN.


Prerequisites
=============

To build Livy, you will need:

    Debian/Ubuntu:
      * mvn (from ``maven`` package or maven3 tarball)
      * openjdk-7-jdk (or Oracle Java7 jdk)

    Redhat/CentOS:
      * mvn (from ``maven`` package or maven3 tarball)
      * java-1.7.0-openjdk (or Oracle Java7 jdk)



Building Livy
=============

Livy is normally built by the `Hue Build System`_, it can also be built on it's
own (aka without any other Hue dependency) with `Apache Maven`_. To build, run:

    $ cd $HUE_HOME/apps/spark/java
    $ mvn -DskipTests clean package

 .. _Hue Build System: https://github.com/cloudera/hue/#getting-started
 .. _Apache Maven: http://maven.apache.org


Running Tests
=============

In order to run the Livy Tests, first follow the instructions in `Building
Livy`_. Then run:

    $ cd $HUE_HOME/apps/spark/java
    $ mvn test


Community
=========
   * User group: http://groups.google.com/a/cloudera.org/group/hue-user
   * Jira: https://issues.cloudera.org/browse/HUE
   * Reviews: https://review.cloudera.org/dashboard/?view=to-group&group=hue (repo 'hue-rw')


License
=======
Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0
