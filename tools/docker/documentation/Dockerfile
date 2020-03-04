
FROM ubuntu:18.04 as build
LABEL description="Hue documentation docs.gethue.com"

RUN apt-get update -y && apt-get install -y \
  wget \
  python-pip

RUN wget https://github.com/gohugoio/hugo/releases/download/v0.62.0/hugo_0.62.0_Linux-64bit.deb \
  && dpkg -i hugo*.deb \
  && rm hugo*.deb \
  && pip install Pygments

COPY tools/docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY tools/docker/documentation/docs.gethue.com.conf /etc/nginx/sites-available/docs.gethue.com

RUN mkdir /etc/nginx/sites-enabled

# Docs
ADD docs/docs-site /docs
WORKDIR /docs

RUN hugo


FROM nginx:1.17-alpine
COPY --from=build /docs/public /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
