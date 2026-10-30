---
title: "Dependencies"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: -1
---

You need Python, some OS packages, a database, and Node.js to build and run Hue.

## Python

Hue uses Python modules that compile native code, so you need the Python development libraries and build tools on your system. See [OS packages](#os-packages).

Supported versions:

* Python 3.11 only. Python 3.11.18 or later is recommended (see the security note below).

Before you build, set the Python version:

```bash
export PYTHON_VER=python3.11
```

> **Security note (eMudhra CA incident):** the compromised eMudhra (emSign) CA was removed from CA bundles such as `certifi`. The Hue build pins `certifi` to `2026.10.23`, installs `pip` 26.2.2 (older `pip` versions keep trusting the compromised CA through their vendored `certifi`) and uses `virtualenv` 21.14.13 on the build host. Python 3.11.18 additionally rejects the compromised intermediate CAs on its own. Rebuild container images without layer caching (`tools/container/build.sh` does this by default) so they pick up the latest system certificates.

## Database

Hue stores its data (users, query history, sharing permissions) in a database. It runs best with [MySQL InnoDB, MariaDB, PostgreSQL, or Oracle](/administrator/administration/database/). The embedded SQLite database is for testing only.

Install the Python client library of your database in the Hue virtual environment, after `make apps` or `make install`.

### MySQL / MariaDB

Install the OS client headers (`libmysqlclient-dev` on Ubuntu), then install `mysqlclient`:

```bash
./build/env/bin/pip install mysqlclient
```

The Hue Docker image uses `mysqlclient==2.2.7`. Use the `mysql` engine for both MySQL and MariaDB.

### PostgreSQL

Install `psycopg2-binary`:

```bash
./build/env/bin/pip install psycopg2-binary
```

### Oracle

Hue ships the `cx_Oracle` 8.3.0 Python module. It needs the Oracle Instant Client libraries on the host. Download the Basic and SDK packages of the same version from [Oracle Instant Client](https://www.oracle.com/database/technologies/instant-client/downloads.html), unzip them into one directory, and make the directory available to the loader:

```bash
export ORACLE_HOME=/usr/local/share/oracle
export LD_LIBRARY_PATH=$ORACLE_HOME
```

On macOS, use `DYLD_LIBRARY_PATH` instead of `LD_LIBRARY_PATH`.

Hue sets `options={"threaded": true}` for Oracle by default. If you override `options` in the `[[database]]` section of the `hue.ini`, keep `threaded` set to `true` to avoid crashes. See [Database](/administrator/administration/database/).

## OS packages

The [File Import API](/developer/api/rest/importer/) detects the file type with the `libmagic` library. Install it with the OS package manager: `libmagic1` on Ubuntu, `file-libs` on RHEL and `brew install libmagic` on macOS. Without it, Hue logs a warning and cannot guess the file type.

### Ubuntu

```bash
sudo apt-get install git gcc g++ make pkg-config libffi-dev libkrb5-dev krb5-config libsasl2-dev libsasl2-modules-gssapi-mit libsqlite3-dev libssl-dev libxml2-dev libxslt-dev libldap2-dev libsnappy-dev libmysqlclient-dev python3.11 python3.11-dev python3.11-venv python3.11-distutils
```

On Ubuntu 22.04, `python3.11` is in the `universe` repository.

### CentOS/RHEL

```bash
sudo yum install cyrus-sasl-devel cyrus-sasl-gssapi cyrus-sasl-plain gcc gcc-c++ krb5-devel libffi-devel libxml2-devel libxslt-devel make mysql mysql-devel openldap-devel python3.11-devel sqlite-devel gmp-devel openssl-devel
```

### SLES 12

```bash
zypper in cyrus-sasl-devel cyrus-sasl-gssapi cyrus-sasl-plain gcc gcc-c++ krb5-devel libffi-devel libxml2-devel libxslt-devel make mysql mysql-devel openldap2-devel python311-devel sqlite-devel gmp-devel
```

> **Note:** If the Kerberos extension fails to build with `krb5-config: command not found`, install `krb5-devel` and add the directory of `krb5-config` to your `PATH`:

```bash
rpm -ql krb5-devel | grep krb5-config ## find the path of krb5-config
export PATH=$PATH:/usr/lib/mit/bin
```

### macOS

Prerequisites:

* Xcode command line tools
* [Homebrew](https://brew.sh)

#### Apple Silicon (M1, M2, M3)

This step-by-step guide was tested on a fresh macOS installation on Apple Silicon.

1. Clone the Hue repository:

   ```bash
   git clone https://github.com/cloudera/hue.git
   cd hue
   ```

2. Install Homebrew if it is not already installed:

   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

3. Install and start PostgreSQL (or use another database):

   ```bash
   brew install postgresql@14
   brew services start postgresql@14
   ```

4. Create the Hue database and user:

   ```bash
   createdb hue_d --lc-collate='en_US.UTF-8' -T "template0"
   psql -s hue_d
   ```

   In the `psql` shell, run these statements one by one:

   ```sql
   create user hue_u with password 'huepassword';
   grant all privileges on database hue_d to hue_u;
   \q
   ```

5. Install `gmp`, `openssl`, and `libffi`. Some of them might already be installed with PostgreSQL:

   ```bash
   brew install gmp openssl libffi
   ```

6. Install Python 3.11, either with Homebrew or with the macOS installer from [python.org](https://www.python.org/downloads/macos/). The direct download from python.org is the tested option.

   > **Note:** Hue requires Python 3.11. python.org only publishes macOS installers for Python 3.11 up to 3.11.9. To get 3.11.18 or later, install Python 3.11 with Homebrew or build it from source. The Hue build upgrades `pip` and pins `certifi` either way.

7. Install Node.js 22.13 or later with `nvm` or Homebrew:

   ```bash
   brew install node
   ```

8. In the Hue directory, set the build variables and build:

   ```bash
   export PYTHON_VER=python3.11
   export SKIP_PYTHONDEV_CHECK=true
   export CFLAGS="-I$(xcrun --show-sdk-path)/usr/include/sasl"
   export LDFLAGS="-L/usr/local/opt/libffi/lib -L/usr/local/opt/openssl@1.1/lib"
   export CPPFLAGS="-L/usr/local/opt/libffi/lib/include -L/usr/local/opt/openssl@1.1/lib/include"
   make apps
   ```

9. Create the configuration file and set the database in the `[[database]]` section under `[desktop]` of `desktop/conf/pseudo-distributed.ini`:

   ```bash
   cp desktop/conf/pseudo-distributed.ini.tmpl desktop/conf/pseudo-distributed.ini
   ```

   ```ini
   [[database]]
     engine=postgresql_psycopg2
     host=localhost
     port=5432
     user=hue_u
     password=huepassword
     name=hue_d
   ```

10. Install the PostgreSQL client library in the Hue virtual environment:

    ```bash
    ./build/env/bin/pip install psycopg2-binary
    ```

11. Apply the database migrations:

    ```bash
    ./build/env/bin/hue migrate
    ```

12. Start Hue:

    ```bash
    ./build/env/bin/hue runserver
    ```

    Open [http://localhost:8000](http://localhost:8000).

If you get a `Could not find Python.h` message, make sure `SKIP_PYTHONDEV_CHECK=true` is exported.

## Node.js

Node.js 22.13 or later is required.

For example, to install it on Ubuntu:

```bash
curl -sL https://deb.nodesource.com/setup_22.x | sudo bash -
sudo apt-get install -y nodejs
```

For CentOS or Red Hat, use this source:

```bash
curl -sL https://rpm.nodesource.com/setup_22.x | sudo bash -
sudo yum install -y nodejs
```

## Java

Java is optional. It is only needed for the [JDBC proxy](/developer/development/#connectors) connector, which is not built by default. Install a JDK and Maven from your OS package manager if you need it.

## Supported browsers

The two latest LTS versions of each browser:

* Edge
* Safari
* Chrome
* Firefox
