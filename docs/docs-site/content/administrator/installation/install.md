---
title: "Install"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: 2
---

Start from a [release](/releases/) tarball or [building](https://github.com/cloudera/hue#getting-started) the project yourself.

Make sure you have the [dependencies](/administrator/installation/dependencies/) for your operating system.

Then configure `$PREFIX` with the path where you want to install Hue by running:

    PREFIX=/usr/share make install
    cd /usr/share/hue

You can install Hue anywhere on your system, and run Hue as a non-root user.

It is a good practice to create a new user for Hue and either install Hue in
that user's home directory, or in a directory within `/usr/share`.

After the installation, you can start Hue on your Hue Server by doing:

    build/env/bin/supervisor

This will start several subprocesses, corresponding to the different Hue
components. Your Hue installation is now running.

After installation, you can use Hue by navigating to `http://myserver:8888/`.

Next step is to [configure](/administrator/configuration/) Hue to point to the external services.
Then, the [user guide](/user/index.html) will help users go through the various installed applications.
