
## Build

    docker build . -t gethue/nginx:latest -f tools/docker/nginx/Dockerfile

## Push

    docker push gethue/nginx:latest

## Run

    docker run -it -p 80:80 gethue/nginx:latest

With a local Hue:

    docker run -it -p 80:80 --network="host" gethue/nginx:latest
