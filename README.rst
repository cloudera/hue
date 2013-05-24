=========================================
          Hue Oozie UI v1.1
=========================================

Instructions to install the tarball release of Hue Oozie.


## Install in any directory. 
## If you don't have the permissions, you will need to 'sudo' the commands.
$ PREFIX=/usr/share make install

## Run
$ /usr/share/hue/build/env/bin/hue runspawningserver

## Goto: http://localhost:11011 !

## Enter the username you want



Optional
--------

## Install plug-ins (for direct access to logs. Requires Hadoop 1.2 or 0.23)
$ cd /usr/lib/hadoop-0.20-mapreduce/lib
$ ln -s /usr/share/hue/desktop/libs/hadoop/java-lib/hue*jar

## Configure Hadoop (for HDFS file links)
Edit hdfs-site.xml:

<property>
  <name>dfs.webhdfs.enable</name>
  <value>true</value>
</property>

Edit mapred-site.xml:

<property>
  <name>mapred.jobtracker.plugins</name>
  <value>org.apache.hadoop.thriftfs.ThriftJobTrackerPlugin</value>
  <description>Comma-separated list of jobtracker plug-ins to be activated.
  </description>
</property>


Dependencies
------------

You might need some of these library development packages (in particular the python* ones) if they not installed on your system:

Ubuntu:
* ant
* gcc
* g++
* libsqlite3-dev
* libxml2-dev
* libxslt-dev
* mvn (from maven2 package or tarball)
* python-dev
* python-simplejson
* python-setuptools

CentOS:
* ant
* asciidoc
* gcc
* gcc-c++
* libxml2-devel
* libxslt-devel
* mvn (from maven2 package or tarball)
* python-devel
* python-simplejson
* sqlite-devel

MacOS (mac port):
* liblxml
* libxml2
* libxslt
* simplejson (easy_install)
* sqlite3
