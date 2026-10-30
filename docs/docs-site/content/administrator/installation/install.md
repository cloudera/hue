---
title: "Install"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: 2
---

Build Hue from a clone of the [repository](https://github.com/cloudera/hue) and install it on your server.

## Prerequisites

* The [dependencies](/administrator/installation/dependencies/) for your operating system: Python 3.11 and Node.js 22.13 or later.
* A user to run Hue. Run Hue as a non-root user.

## Install Hue

1. Set the build variables:

   ```bash
   export PYTHON_VER=python3.11
   ```

2. Set `PREFIX` to the directory that will contain the `hue` directory, then install:

   ```bash
   PREFIX=$HOME make install
   cd $HOME/hue
   ```

   Hue is installed in `$PREFIX/hue`. If you do not set `PREFIX`, it defaults to `/usr/local`, which usually requires root. To install in a shared location such as `/usr/share`, run the command with `sudo` and give the Hue user ownership of the `hue` directory.

You can install Hue anywhere on your system. Install it in a directory within `/usr/share` or in the home directory of the user that runs Hue.

## Build a tarball

To build a tarball for production, run `make prod` in the Hue directory:

```bash
make prod
```

The tarball is created in `build/release/prod/`.

## Start Hue

After the installation, start Hue from the installation directory:

```bash
build/env/bin/supervisor
```

The supervisor starts the Hue processes. Open `http://<server>:8888/`. The first user who logs in becomes the superuser.

> **Note:** Hue uses an embedded SQLite database by default. [Configure another database](/administrator/administration/database/) before real use.

Next, [configure the server](/administrator/configuration/) and point it to the external services to query.
