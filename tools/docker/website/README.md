
## Build

    docker build docs -t gethue/website:latest -f tools/docker/website/Dockerfile --build-arg lang=en
    docker build docs -t gethue/website-jp:latest -f tools/docker/website/Dockerfile --build-arg lang=jp

    docker push gethue/website:latest
    docker push gethue/website-jp:latest

## Run

    docker run -it -p 8000:80 gethue/website:latest
    docker run -it -p 8001:80 gethue/website-jp:latest
