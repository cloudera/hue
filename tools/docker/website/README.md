
## Build

    docker build . -t gethue/documentation:latest -f tools/docker/website/Dockerfile

## Push

    docker push gethue/documentation:latest

## Run

    docker run -it -p 80:80 gethue/documentation:latest
