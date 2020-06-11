---
title: "Dependencies"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: -1
---

### Python

Hue employs some Python modules which use native code and requires certain development libraries be installed on your system. To install from the tarball, you'll need these library development packages and tools installed on your system:

Versions supported:
* Python 2.7
* Python 3.5+ (can be tested cf. instructions on [HUE-8737](https://issues.cloudera.org/browse/HUE-8737))
```
# If you are using Python 3.5+, set PYTHON_VER before the build, like
export PYTHON_VER=python3.8
```

### Database
* [MySQL InnoDB or PostgreSQL or Oracle](https://www.cloudera.com/documentation/enterprise/latest/topics/hue_dbs_0.html)


### Ubuntu

    sudo apt-get install git ant gcc g++ libffi-dev libkrb5-dev libmysqlclient-dev libsasl2-dev libsasl2-modules-gssapi-mit libsqlite3-dev libssl-dev libxml2-dev libxslt-dev make maven libldap2-dev python-dev python-setuptools libgmp3-dev


**Install Node.js**

    curl -sL https://deb.nodesource.com/setup_10.x | sudo bash -
    sudo apt-get install -y nodejs


### CentOS/RHEL

    sudo yum install ant asciidoc cyrus-sasl-devel cyrus-sasl-gssapi cyrus-sasl-plain gcc gcc-c++ krb5-devel libffi-devel libxml2-devel libxslt-devel make mysql mysql-devel openldap-devel python-devel sqlite-devel gmp-devel

* mvn (from [``apache-maven``](https://gist.github.com/sebsto/19b99f1fa1f32cae5d00) package or maven3 tarball)
* libtidy (for unit tests only)
* openssl-devel (for version 7+)

Installing Python 2.7:

#### CentOS 6.8 / 6.9 OS

Check your OS Version:

    cat /etc/redhat-release

Make sure "/etc/redhat-release" contains "CentOS 6.8 or 6.9" version. These instructions are tested on CentOS 6.8 and 6.9 versions only. It may or may not work on previous CentOS 6 series OS.

    yum install -y centos-release-SCL
    yum install -y scl-utils
    yum install -y python27

#### RedHat 6.8 / 6.9 OS

Check your OS Version

    cat /etc/redhat-release

Make sure `/etc/redhat-release` contains "RedHat 6.8 or 6.9" version. These instructions are tested on RedHat 6.8 and 6.9 versions only. It may or may not work on previous RedHat 6 series OS.

    wget http://mirror.infra.cloudera.com/centos/6/extras/x86_64/Packages/centos-release-scl-rh-2-3.el6.centos.noarch.rpm
    rpm -ivh centos-release-scl-rh-2-3.el6.centos.noarch.rpm
    yum install -y scl-utils
    yum install -y python27

#### Oracle 6.8 / 6.9 OS

Check your OS Version

    cat /etc/redhat-release

Make sure `/etc/redhat-release` contains "Oracle 6.8 or 6.9" version. These instructions are tested on Oracle 6.8 and 6.9 versions only. It may or may not work on previous Oracle 6 series OS.

    wget -O /etc/yum.repos.d/public-yum-ol6.repo http://yum.oracle.com/public-yum-ol6.repo

Set the value of the enabled parameter for the software_collections repository to 1: for file `/etc/yum.repos.d/public-yum-ol6.repo`

    [ol6_software_collections]
    name=Software Collection Library release 3.0 packages for Oracle Linux 6 (x86_64)
    baseurl=http://yum.oracle.com/repo/OracleLinux/OL6/SoftwareCollections/x86_64/
    gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-oracle
    gpgcheck=1
    enabled=1

for more details, refer to this link: [https://docs.oracle.com/cd/E37670_01/E59096/html/section_e3v_nbl_cr.html](https://docs.oracle.com/cd/E37670_01/E59096/html/section_e3v_nbl_cr.html)

    yum install -y scl-utils
    yum install -y python27

### MacOS

* Xcode command line tools
* [Homebrew](https://brew.sh)

Install Dependencies via Homebrew

    brew install mysql@5.7 maven gmp openssl libffi

Install Xcode command line tools

    sudo xcode-select --install

Fix openssl errors (required for MacOS 10.11+)

    export LDFLAGS=-L/usr/local/opt/openssl/lib && export CPPFLAGS=-I/usr/local/opt/openssl/include

If you are getting **"Could not find Python.h"** message

    export SKIP_PYTHONDEV_CHECK=true

On macOS 10.15+, install an older version of openssl

    brew uninstall --ignore-dependencies openssl && brew install https://github.com/tebelorg/Tump/releases/download/v1.0.0/openssl.rb

Fix the possible missing Python headers message by installing the MacOS SDK headers

On macOS 10.14.x

    open /Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg

On macOS 10.15.x

    sudo ln -s /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/include/* /usr/local/include/


### Oracle Client lib

#### Version 11

Download both instantclient-basic and instantclient-sdk of the same version (11.2.0.4.0 for this example) and on your ~/.bash_profile, add

    export ORACLE_HOME=/usr/local/share/oracle
    export VERSION=11.2.0.4.0
    export ARCH=x86_64
    export DYLD_LIBRARY_PATH=$ORACLE_HOME
    export LD_LIBRARY_PATH=$ORACLE_HOME

and then

    source ~/.bash_profile
    sudo mkdir -p $ORACLE_HOME
    sudo chmod 775 $ORACLE_HOME

then unzip the content of both downloaded zip files into the newly created $ORACLE_HOME in a way that the 'sdk' folder is at the same level with the other files and then

    ln -s libclntsh.dylib.11.1 libclntsh.dylib
    ln -s libocci.dylib.11.1 libocci.dylib

and finally

    cd sdk
    unzip ottclasses.zip

#### Version 12

Hue comes with an older Oracle client cx_Oracle-5.2.1 Python module so it will fail. We need to do the above client install and then upgrade Hue's client module to at least cx_Oracle-5.3.

Make sure you have the `python-dev` package dependencies, ensure that ORACLE_HOME and LB_LIBRARY_PATH are properly set so that pip knows which version to install, then:

    echo $ORACLE_HOME $LD_LIBRARY_PATH

    ./build/env/bin/pip install cx_Oracle

Tip: You can also wget the proper cx_Oracle file yourself: https://pypi.python.org/pypi/cx_Oracle/.

Tip: Going to where is the Oracle client, e.g. /usr/local/share/oracle then creating a symlink similar to below could even trick the cx_Oracle-5.2.1 module to work with 12.2 without doing the pip upgrade:

    ln -s libclntsh.so.12.2 libclntsh.so.11.1

There is more details on this [Apply Temporary Workaround for Oracle 12 Client](https://docs.cloudera.com/documentation/enterprise/latest/topics/hue_dbs_oracle_pkg.html#concept_qx3_hfw_4z).


#### Mac

* [Oracle Instant Client](http://www.oracle.com/technetwork/database/database-technologies/instant-client/downloads/index.html)

### Java

Java is only for the [JDBC proxy](/developer/connectors/#jdbc) connector.

**Install Oracle JDK**

On Ubuntu 16.04 or less only:

    sudo add-apt-repository ppa:webupd8team/java
    sudo apt-get update
    sudo apt-get install oracle-java8-installer

On Centos:

* [Oracle JDK](https://www.digitalocean.com/community/tutorials/how-to-install-java-on-centos-and-fedora)

On Mac:

    brew cask install adoptopenjdk

### Supported Browsers

The two latest LTS versions of each browsers:

* Edge
* Safari
* Chrome
* Firefox
