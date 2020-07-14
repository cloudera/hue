
FROM ubuntu:18.04 as build
LABEL description="gethue.com website"

RUN apt-get update -y && apt-get install -y \
  wget \
  python-pip \
  git

RUN wget https://github.com/gohugoio/hugo/releases/download/v0.62.0/hugo_0.62.0_Linux-64bit.deb \
  && dpkg -i hugo*.deb \
  && rm hugo*.deb \
  && pip install Pygments

ADD . /gethue
#ADD docs/gethue /gethue
WORKDIR /gethue

RUN hugo --source docs/gethue --baseURL ""



FROM nginx:1.17-alpine
ARG lang=en
COPY --from=build /gethue/docs/gethue/public/${lang} /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
