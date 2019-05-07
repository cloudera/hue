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

Feel free to replace `-t hue` in all the commands by your own docker repository and image tag, e.g. `gethue/hue:latest`

**Tag and push the image to the container registry**

```
docker build . -t docker-registry.gethue.com/gethue/hue:4.4.0
docker push docker-registry.gethue.com/gethue/hue:4.4.0
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
[``tools/docker/hue/conf/z-defaults.ini``](/tools/docker/hue/conf/z-defaults.ini) on top of [``desktop/conf/hue.ini``](/desktop/conf/hue.ini) which assumes localhost for all the data services and uses and embedded sqlite database that will error out.

The default ini is used for configuration at the image build time (e.g. which apps to always disable or certain settings like [banner customization](http://gethue.com/add-a-top-banner-to-hue/)).

In order to be useful, configure Hue at runtime to point to external services. The simplified ini [``hue.ini``](/tools/docker/hue/hue.ini) can be edited before starting Hue via:

```
docker run -it -p 8888:8888 -v $PWD/tools/docker/hue/hue.ini:/usr/share/hue/desktop/conf/z-hue.ini gethue/hue
```

or copy the [``desktop/conf.dist/hue.ini``](/desktop/conf.dist/hue.ini):

```
cp desktop/conf.dist/hue.ini .

docker run -it -p 8888:8888 -v $PWD/hue.ini:/usr/share/hue/desktop/conf/z-hue.ini gethue/hue
```

*Note*

If for example the database is pointing to your localhost, if using Docker on Linux just add the `--network="host"` parameter and the container will correctly point to it.

    sudo docker run -it -p 8888:8888 -v $PWD/desktop/conf/pseudo-distributed.ini:/usr/share/hue/desktop/conf/z-hue.ini --network="host" gethue/hue


#### Docker Compose

Assuming we have a local ``hue.ini`` as shown in the previous section:

```
cd tools/docker/hue
cp docker-compose.yml.sample docker-compose.yml
```

Then:

```
docker-compose up -d
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
