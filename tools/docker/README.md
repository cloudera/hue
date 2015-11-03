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
This opens a bash to the root of the project. You can then configure Hue and start using it! Read more about configuring Hue on our [blog](http://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/).

