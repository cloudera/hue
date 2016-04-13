![alt text](https://raw.githubusercontent.com/cloudera/hue/master/docs/images/hue_logo.png "Hue Logo")


#Welcome to the repository for the Hue Dockerfiles


Hue is an open source Web interface for analyzing data with any Apache Hadoop: [gethue.com](http://gethue.com)

Here you can find the Dockerfiles for Hue and Livy, the Spark REST server.

You can catch us on [Docker Hub](https://hub.docker.com/u/gethue/) as well.

[![DockerPulls](https://img.shields.io/docker/pulls/gethue/hue.svg)](https://registry.hub.docker.com/u/gethue/hue/)
[![DockerStars](https://img.shields.io/docker/stars/gethue/hue.svg)](https://registry.hub.docker.com/u/gethue/hue/)

##Get the docker image

Just pull the latest from the Internet or build it yourself from the Hue repository.

###Pull the image from Docker Hub
```
sudo docker pull gethue/hue:latest
```

###Build the image
```
cd tools/docker/hue-base
sudo docker build --rm -t gethue/hue:latest .
```

## Running the image
```
docker run -it -p 8888:8888 gethue/hue:latest bash
```
This opens a bash to the root of the project. From there you can run the development version of Hue with the command

```
./build/env/bin/hue runserver_plus 0.0.0.0:8888
```

or

## Running with docker-compose
```
cd tools/docker/hue-base
cp docker-compose.yml.sample docker-compose.yml
cp ../../../hue/desktop/conf.dist/hue.ini
docker-compose up -d
docker exec -ti development_hue bash
```

Hue should then be up and running on your default Docker IP on the port 8888, so usually [http://192.168.99.100:8888](http://192.168.99.100:8888).

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

![alt text](https://raw.githubusercontent.com/cloudera/hue/master/docs/images/login.png "Hue First Login")


## Next

You can then configure Hue and start using it!

Read more about configuring Hue on our [blog](http://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/). The development version uses the configuration file ``desktop/conf/pseudo-distributed.ini``.
