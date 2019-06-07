# Hue Server


## Get the docker image

Just pull the latest from the Internet or build it yourself from the Hue repository via the [Dockerfile](Dockerfile).


### Pull the image from Docker Hub

```
sudo docker pull gethue/hue:latest
```

### Build the image

Directly from Github source:

```
sudo docker build https://github.com/cloudera/hue.git#master -t hue -f tools/docker/hue/Dockerfile
```

Or from a cloned local Hue:

```
sudo docker build . -t hue -f tools/docker/hue/Dockerfile
```

**Note**

Feel free to replace `-t hue` in all the commands by your own docker repository and image tag, e.g. `gethue/hue:latest`, `docker-account/hue:4.5.0`

**Tag and push the image to the container registry**

```
docker build . -t gethue/hue:latest
docker push docker.io/gethue/hue:latest
```


## Run the image

### Docker

Directly boot the image:

```
docker run -it -p 8888:8888 gethue/hue:latest
```

Hue should then be up and running on your default Docker IP on the port 8888, so usually [http://127.0.0.1:8888](http://127.0.0.1:8888).


#### Configuration

By default the Hue container is using
[``tools/docker/hue/conf/hue-overrides.ini``](/tools/docker/hue/conf/hue-overrides.ini) on top of [``desktop/conf/hue.ini``](/desktop/conf/hue.ini) which assumes localhost for all the data services and uses and embedded sqlite database that will error out.

The default ini is used for configuration at the image build time (e.g. which apps to always disable or certain settings like [banner customization](http://gethue.com/add-a-top-banner-to-hue/)).

In order to be useful, configure Hue at runtime to point to external services. The simplified ini [``hue-overrides.ini``](/tools/docker/hue/conf/hue-overrides.ini) can be edited before starting Hue via:

```
cd tools/docker/hue
cp conf/hue-overrides.ini hue.ini
```

Edit the database settings in `hue.ini` for one of these two databases. Do not forget to create a 'hue' database too.

Postgres

```
    [desktop]
    [[database]]
    engine=postgresql_psycopg2
    host=127.0.0.1
    port=5432
    user=hue
    password=hue
    name=hue
```

MySql

```
    [desktop]
    [[database]]
    engine=mysql
    host=127.0.0.1
    port=3306
    user=root
    password=secret
    name=hue
```

If you want to be able to query a database out of the box, update the connector interpreters accordingly, e.g.:

```
[notebook]

  # One entry for each type of snippet.
  [[interpreters]]
    # Define the name and how to connect and execute the language.
    # http://cloudera.github.io/hue/latest/administrator/configuration/editor/

    [[[mysql]]]
      name = MySQL
      interface=sqlalchemy
      ## https://docs.sqlalchemy.org/en/latest/dialects/mysql.html
      options='{"url": "mysql://root:secret@database:3306/hue"}'
```

Then start the Hue server:

```
docker run -it -p 8888:8888 -v $PWD/hue.ini:/usr/share/hue/desktop/conf/z-hue.ini gethue/hue
```

*Note*

If for example the database is pointing to your localhost, if using Docker on Linux just add the `--network="host"` parameter and the container will correctly point to it.

    sudo docker run -it -p 8888:8888 -v $PWD/desktop/conf/pseudo-distributed.ini:/usr/share/hue/desktop/conf/z-hue.ini --network="host" gethue/hue


### Docker Compose

Docker compose allows to start all the required services in one command line.

This will start a Hue server as well as a MySQL database by default. Only the MySQL interpreter is configured in [``tools/docker/hue/conf/hue-overrides.ini``](/tools/docker/hue/conf/hue-overrides.ini).

Assuming we have a local ``hue.ini`` as shown in the previous section:

```
cd tools/docker/hue
```

Then:

```
docker-compose up -d
```

And to stop:

```
docker-compose down
```

**Note**
If http://127.0.0.1:8888 does not work, get the IP of the docker container with:
```
sudo docker ps
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS                            NAMES
4064b02b42c9        gethue/hue          "./startup.sh"      About a minute ago   Up About a minute   0.0.0.0:8888->8888/tcp   awesome_wiles
```

```
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 4064b02b42c9
172.17.0.2
```

So in our case [http://172.17.0.2:8888](http://172.17.0.2:8888).
