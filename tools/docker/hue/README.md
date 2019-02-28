# Hue Server


## Get the docker image

Just pull the latest from the Internet or build it yourself from the Hue repository.


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
docker build . -t docker-registry.gethue.com/gethue/hue:v4.4
docker push docker-registry.gethue.com/gethue/hue:v4.4
```


## Run the image

### Docker

Directly boot the image:

```
docker run -it -p 8888:8888 gethue/hue:latest
```

Hue should then be up and running on your default Docker IP on the port 8888, so usually [http://192.168.99.100:8888](http://192.168.99.100:8888).


#### Configuration

By default the Hue container is using 
[``tools/docker/hue/conf/defaults.ini``.](/tools/docker/hue/conf/defaults.ini) on top of [``desktop/conf/hue.ini``.](/desktop/conf/hue.ini)
which assumes localhost for all the data services.

In order to point to the services, use the simplified ini [``hue.ini``.](/tools/docker/hue/hue.ini), edit the values before starting it via:

```
docker run -it -p 8888:8888 -v $PWD/tools/docker/hue/hue.ini:/usr/share/hue/desktop/conf/z-hue.ini gethue/hue
```

or copy the full one:

```
cp /desktop/conf.dist/hue.ini .

docker run -it -p 8888:8888 -v $PWD/hue.ini:/usr/share/hue/desktop/conf/z-hue.ini gethue/hue
```

Read more about configuring Hue on the [blog](http://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/).


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
If 192.168.99.100 does not work, get the IP of the docker container with:
```
sudo docker ps
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS                            NAMES
b7950388c1db        gethue/hue:latest   "bash"              10 minutes ago      Up 10 minutes       22/tcp, 0.0.0.0:8888->8888/tcp   agitated_mccarthy
```

Then get ``inet addr``, so in our case [http://172.17.0.1:8888](http://172.17.0.1:8888):
```
sudo docker exec -it b7950388c1db /sbin/ifconfig eth0
eth0      Link encap:Ethernet  HWaddr 02:42:ac:11:00:01
          inet addr:172.17.0.1  Bcast:0.0.0.0  Mask:255.255.0.0
          inet6 addr: fe80::42:acff:fe11:1/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:67 errors:0 dropped:0 overruns:0 frame:0
          TX packets:8 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:0
          RX bytes:10626 (10.6 KB)  TX bytes:648 (648.0 B)
```

