---
title: "Dependencies"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: -1
---

You will need Python, some OS packages, a Database and Node.js.

## Python

Hue employs some Python modules which use native code and requires certain development libraries be installed on your system. To install from the tarball, you'll need these library development packages and tools installed on your system:

Versions supported:
* Python 3.8
* Python 3.9
* Python 3.11
```
# If you are using Python 3.11, set PYTHON_VER before the build, like
export PYTHON_VER=python3.11

# Export ROOT which should point to your Hue directory
export ROOT=<path_to_hue_directory>
```

## Database

Hue is being ran the most with [MySQL InnoDB, PostgreSQL or Oracle](https://docs.cloudera.com/documentation/enterprise/latest/topics/hue_dbs_0.html).

### MySQL / MariaDB

The client lib [MySQL-python](https://github.com/cloudera/hue/tree/master/desktop/core/ext-py/MySQL-python-1.2.5) is already included so it should work out of the box.

**Note**

With the recent OSs like Ubuntu 20.04 or using Python 3, the MySQL-python lib won't compile properly and will produce an error similar to:

    _mysql.c:44:10: fatal error: my_config.h: No such file or directory
      44 | #include "my_config.h"
          |          ^~~~~~~~~~~~~

The lib folder needs to be swapped with https://pypi.org/project/mysqlclient/. Unfortunately for licensing reason (GPL vs Apache) this can't be officially done in the Hue repository.

Remove and add the compatible MySql lib with these two commands:

    git cherry-pick 7a9100d4a7f38eaef7bd4bd7c715ac1f24a969a8
    git cherry-pick e67c1105b85b815346758ef1b9cd714dd91d7ea3

    git clean -fdx

    make apps

Read [HUE-9390](https://issues.cloudera.org/browse/HUE-9390) for more details.

### PostgreSQL

You would need the OS `python-psycopg2` or Python [psycopg2](https://pypi.org/project/psycopg2/).

### Oracle

How to install the client lib.

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

* [Oracle Instant Client](https://www.oracle.com/database/technologies/instant-client/downloads.html)

## OS Packages

### Ubuntu

    sudo apt-get install git ant gcc g++ libffi-dev libkrb5-dev libmysqlclient-dev libsasl2-dev libsasl2-modules-gssapi-mit libsqlite3-dev libssl-dev libxml2-dev libxslt-dev make maven libldap2-dev python-dev python-setuptools libgmp3-dev

With Python 3, also:

    sudo apt-get install python3.8-dev python3-distutils


### CentOS/RHEL

    sudo yum install ant asciidoc cyrus-sasl-devel cyrus-sasl-gssapi cyrus-sasl-plain gcc gcc-c++ krb5-devel libffi-devel libxml2-devel libxslt-devel make mysql mysql-devel openldap-devel python-devel sqlite-devel gmp-devel

* mvn (from [``apache-maven``](https://gist.github.com/sebsto/19b99f1fa1f32cae5d00) package or maven3 tarball)
* libtidy (for unit tests only)
* openssl-devel (for version 7+)

### SLES 12

    zypper in ant asciidoc cyrus-sasl-devel cyrus-sasl-gssapi cyrus-sasl-plain gcc gcc-c++ krb5-devel libffi-devel libxml2-devel libxslt-devel make mysql mysql-devel openldap2-devel python-devel sqlite-devel gmp-devel

Tip: if you run into building kerberos extension issue and see message `krb5-config: command not found`, install and append it to environment variable PATH.

    rpm -ql krb5-devel | grep krb5-config ## find the path of krb5-config
    export PATH=$PATH:/usr/lib/mit/bin

### MacOS

* Xcode command line tools
* [Homebrew](https://brew.sh)

#### Apple Silicon (M1, M2, M3)

This is a verified step-by-step guide on how to get Hue up and running on a fresh installation of macOS, tested on Apple Silicon (M1, M2, M3).

1. Clone the Hue repo

    `git clone https://github.com/cloudera/hue.git`

2. Install Homebrew (if not already installed)

   `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

3. Install Postgres (unless you prefer something else)

   `brew install postgresql@14`

4. Start Postgres

   `brew services start postgresql@14`

5. Create the Hue database and set permissions

   ```
   # Create the DB
   createdb hue_d --lc-collate='en_US.UTF-8' -T "template0"
   
   # Connect to the dbms shell
   psql -s hue_d
   
   # Run the following lines one by one
   create user hue_u with password 'huepassword';
   grant all privileges on database hue_d to hue_u;
   \q
   ```

6. Install gmp, openssl, and libffi (Note: some might be installed from Postgres)

   `brew install gmp openssl libffi`

7. Install Python, tested with the **macOS 64-bit (universal2) installer 3.11.x** direct download from python.org
`https://www.python.org/ftp/python/3.11.9/python-3.11.9-macos11.pkg`

   - For Apple Silicon (M1, M2, M3), Python 3.11 is recommended as of June 2025. You can install Python 3.11 either via Homebrew or by direct download from python.org—both options will work, but the direct download is preferred and tested.

>**Note:** By default, Hue will use the highest available Python version on your system. If you want to use a specific lower Python version (such as Python 3.8 or 3.9), set the `PYTHON_VER` environment variable before building. 
For Python 3.11, use `./build/env/bin/hue` as the command path. For Python versions lower than 3.11, the command path will be `./build/venvs/python3.x/bin/hue`, where `python3.x` matches your `PYTHON_VER` setting. Adjust all related commands accordingly if you use a lower Python version. Both options will work as long as you use the correct path for your Python version.

8. Install node and npm (unless already present) using nvm or brew

   `brew install node`

9. In the Hue directory run:

    ```
    export PYTHON_VER=python3.11
    export SKIP_PYTHONDEV_CHECK=true
    export CFLAGS="-I$(xcrun --show-sdk-path)/usr/include/sasl"
    export LDFLAGS="-L/usr/local/opt/libffi/lib -L/usr/local/opt/openssl@1.1/lib"
    export CPPFLAGS="-L/usr/local/opt/libffi/lib/include -L/usr/local/opt/openssl@1.1/lib/include"
    ```

    Also export `ROOT` which should point to your Hue directory:
    ```
    export ROOT=<path_to_hue_directory>
    ```
    
    Then run:
    ```
    make apps
    ```

10. Configure Hue to your liking, edit

    `desktop/conf/pseudo-distributed.ini`

    According to step 5 above for Postgres, set under `[desktop]`:

    ```
    [[database]]
      engine=postgresql_psycopg2
      host=localhost
      port=5432
      user=hue_u
      password=huepassword
      name=hue_d
    ```

11. If you use Postgres as configured in the previous step you'll need to add the psycopg2 lib manually

    `./build/env/bin/pip install psycopg2-binary`

12. Apply migrations (if any)

    ```
    ./build/env/bin/hue makemigrations
    ./build/env/bin/hue migrate
    ```

13. Start Hue

    `./build/env/bin/hue runserver`


#### macOS 10.14, 10.15

Install Dependencies via Homebrew

    brew install mysql@5.7 maven gmp openssl libffi

Install Xcode command line tools

    sudo xcode-select --install

Fix openssl errors (required for MacOS 10.11+)

    export LDFLAGS=-L/usr/local/opt/openssl/lib && export CPPFLAGS=-I/usr/local/opt/openssl/include

If `runserver` stops abruptly with a `"zsh: abort"` message

    export DYLD_FALLBACK_LIBRARY_PATH=/usr/local/opt/openssl/lib

If `runserver` stops abruptly with a `loading libcrypto in an unsafe way` message

    sudo mkdir /usr/local/lib
    # depends on your openssl version, link the following files to /usr/local/lib
    sudo ln -s /opt/homebrew/Cellar/openssl@3/3.0.2/lib/libcrypto.3.dylib /usr/local/lib/libcrypto.dylib
    sudo ln -s /opt/homebrew/Cellar/openssl@3/3.0.2/lib/libssl.3.dylib /usr/local/lib/libssl.dylib

If you are getting `Could not find Python.h` message

    export SKIP_PYTHONDEV_CHECK=true

On macOS 10.15+, install an older version of openssl

    brew uninstall --ignore-dependencies openssl && brew install https://github.com/tebelorg/Tump/releases/download/v1.0.0/openssl.rb

Fix the possible missing Python headers message by installing the MacOS SDK headers

On macOS 10.14.x

    open /Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg

On macOS 10.15.x

    sudo ln -s /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/include/* /usr/local/include/

## NodeJs

e.g. how to install on Ubuntu:

    curl -sL https://deb.nodesource.com/setup_20.x | sudo bash -
    sudo apt-get install -y nodejs

For Centos / Red Hat use this source:

    curl -sL https://rpm.nodesource.com/setup_20.x | sudo bash -
    sudo yum install -y nodejs

Upgrade to npm 10+:

    npm install --global npm

## Java

Optional.

Java is only for the [JDBC proxy](/developer/development/#connectors) connector which is not built automatically anymore.

**Install Oracle JDK**

On Ubuntu 16.04 or less only:

    sudo add-apt-repository ppa:webupd8team/java
    sudo apt-get update
    sudo apt-get install oracle-java8-installer

On Centos:

* [Oracle JDK](https://www.digitalocean.com/community/tutorials/how-to-install-java-on-centos-and-fedora)

On Mac:

    brew cask install adoptopenjdk

## Supported Browsers

The two latest LTS versions of each browsers:

* Edge
* Safari
* Chrome
* Firefox
