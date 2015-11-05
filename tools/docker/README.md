![alt text](https://raw.githubusercontent.com/cloudera/hue/master/docs/images/hue_logo.png "Hue Logo")


#Welcome to the repository for the Hue Dockerfiles


Hue is an open source Web interface for analyzing data with any Apache Hadoop: [gethue.com](http://gethue.com)

Here you can find the Dockerfiles for Hue and Livy, the Spark REST server.

You can catch us on [Docker Hub](https://hub.docker.com/u/gethue/) as well. 

[![DockerPulls](https://img.shields.io/docker/pulls/gethue/hue.svg)](https://registry.hub.docker.com/u/gethue/hue/)
[![DockerStars](https://img.shields.io/docker/stars/gethue/hue.svg)](https://registry.hub.docker.com/u/gethue/hue/)


##Pull the image from Docker Hub
```
docker pull gethue/hue:latest
```

##Build the image
```
docker build --rm -t gethue/hue:latest .
```

## Running the image
```
docker run -it -p 8888:8888 gethue/hue:latest bash
```
This opens a bash to the root of the project. From there you can run the development version of Hue with the command

```
./build/env/bin/hue runserver_plus 0.0.0.0:8888
```

Hue should then be up and running on your default Docker IP on the port 8888, so usually [http://192.168.99.100:8888](http://192.168.99.100:8888).

You can then configure Hue and start using it! Read more about configuring Hue on our [blog](http://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/). The development version uses the configuration file ``desktop/conf/pseudo-distributed.ini``

In case you don't want to have the development server running, you can change the two run commands like this

```
docker run -it -p 8000:8000 gethue/hue:latest bash
```

and

```
./build/env/bin/hue runcpserver 0.0.0.0:8000
```


