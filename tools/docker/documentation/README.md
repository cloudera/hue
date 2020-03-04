
## Build

    docker build . -t gethue/documentation:latest -f tools/docker/documentation/Dockerfile

## Push

    docker push gethue/documentation:latest

## Run

    docker run -it -p 9000:80 gethue/documentation:latest
