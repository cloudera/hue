# Hue Server

## Run the image

Hue can run in one line via the `docker` command.

It also needs to be configured to point to a traditional database instead of Sqlite so see below how to configure the docker image to point to a local MySql or use `docker-compose` which will start both services for you.

To have a zero configuration start use [kubernetes](/tools/kubernetes/) is also a great option.

### Docker

Directly boot the image:

    docker run -it -p 8888:8888 gethue/hue:latest

Hue should then be up and running on your default Docker IP on the port 8888, so usually [http://127.0.0.1:8888](http://127.0.0.1:8888).

Then to avoid the `database locked` error, please see below [Configuration](#configuration).

### Docker Compose

Docker compose allows to start all the required services in one command line.

This will start a Hue server as well as a MySQL database by default. Only the MySQL interpreter is configured in [``tools/docker/hue/conf/z-hue-overrides.ini``](/tools/docker/hue/conf/z-hue-overrides.ini).

Assuming we have a local ``hue.ini`` as shown in the previous section:

    cd tools/docker/hue

Edit `conf/z-hue-overrides.ini` and ucomment the MySql section in `[[database]]`.

Then:

    docker-compose up -d

And to stop:

    docker-compose down

**Note**

If http://127.0.0.1:8888 does not work, get the IP of the docker container with:

    sudo docker ps
    CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS                            NAMES
    4064b02b42c9        gethue/hue          "./startup.sh"      About a minute ago   Up About a minute   0.0.0.0:8888->8888/tcp   awesome_wiles

    docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 4064b02b42c9
    172.17.0.2

So in our case [http://172.17.0.2:8888](http://172.17.0.2:8888).

### Configuration

#### Via local file

By default the Hue container is using
[``tools/docker/hue/conf/z-hue-overrides.ini``](/tools/docker/hue/conf/z-hue-overrides.ini) on top of [``desktop/conf/hue.ini``](/desktop/conf/hue.ini) which assumes localhost for all the data services and uses and embedded sqlite database that will error out.

To configure Hue to point to the databases to query, the simplified ini [``z-hue-overrides.ini``](/tools/docker/hue/conf/z-hue-overrides.ini) can be edited before starting Hue.

Just curl it:

    wget https://raw.githubusercontent.com/cloudera/hue/master/tools/docker/hue/conf/z-hue-overrides.ini -O hue.ini

 Or get is via the repository:

    cd tools/docker/hue
    cp conf/z-hue-overrides.ini hue.ini

#### Via the Image

Let's pull and start the latest Hue container and open a shell inside it:

    docker run -it -p 8888:8888 gethue/hue:latest /bin/bash

This puts us into the `/usr/share/hue` home folder of the Hue installation. Now let's open the configuration file:

    apt-get install -y vim

    vim desktop/conf/hue.ini

First let's make sure that Hue is backed by a relational database supporting transactions like MySQL, PostgreSql or Oracle. Here we go with MySQL and fill-up the `[[database]]` section with the credentials:

    [desktop]
    [[database]]
    host=demo.gethue.com  # Use 127.0.0.1 and not localhost if on the same host
    engine=mysql
    user=hue
    password=password
    name=hue

Now from another terminal use `docker ps` to identify the Hue container id and commit its state to remember the configuration even after stopping it:

    docker ps

    docker commit 368f0d568a5f hue-hive

Now you can start the saved container which will expose the Hue interface on [localhost:8888](localhost:8888).

    docker run -it -p 8888:8888 hue-hive ./startup.sh

#### Hue's Database

 Hue needs an existing database with transactions like MySQL to support concurrent requests and also not lose the registered users, saved queries, sharing permissions... when the server gets stopped.

Edit the database settings in `hue.ini` for one of these two databases. Do not forget to create a 'hue' database too.

PostGreSql

    [desktop]
    [[database]]
    engine=postgresql_psycopg2
    host=127.0.0.1
    port=5432
    user=hue
    password=hue
    name=hue

MySql

    [desktop]
    [[database]]
    engine=mysql
    host=127.0.0.1
    port=3306
    user=root
    password=secret
    name=hue

#### Querying a Data Warehouse

To be able to query a database, update the connector interpreters accordingly, e.g.:

    [notebook]
    [[interpreters]]
    [[[mysql]]]
    name = MySQL
    interface=sqlalchemy
    options='{"url": "mysql://root:secret@database-host:3306/hue"}'

If you are looking another warehouse than Hive, check out all the [other connectors](https://docs.gethue.com/administrator/configuration/connectors/).

Then start the Hue server:

    docker run -it -p 8888:8888 -v $PWD/hue.ini:/usr/share/hue/desktop/conf/z-hue.ini gethue/hue

*Note*

If for example the database is pointing to your localhost, if using Docker on Linux just add the `--network="host"` parameter and the container will correctly point to it.

    sudo docker run -it -p 8888:8888 -v $PWD/desktop/conf/pseudo-distributed.ini:/usr/share/hue/desktop/conf/z-hue.ini --network="host" gethue/hue

## Get the docker image

Just pull the latest from the Internet or build it yourself from the Hue repository via the [Dockerfile](Dockerfile).

### Pull the image from Docker Hub

    docker pull gethue/hue:latest

### Build the image

Directly from Github source:

    docker build https://github.com/cloudera/hue.git#master -t hue -f tools/docker/hue/Dockerfile

Or from a cloned local Hue:

    docker build . -t gethue/hue -f tools/docker/hue/Dockerfile

**Note**

Feel free to replace `-t hue` in all the commands by your own docker repository and image tag, e.g. `gethue/hue:latest`, `docker-account/hue:4.8.0`

**Push the image to the container registry**

    push docker.io/gethue/hue:latest
