
## Build

    docker build docs -t gethue/website:latest -f tools/docker/website/Dockerfile

    docker push gethue/website:latest

## Run

    docker run -it -p 80:80 gethue/website:latest
