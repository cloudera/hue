# Welcome to Hue NGINX (http://gethue.com) Dockerfile
ARG registry=gethue
ARG tag=latest

FROM ${registry}/hue:${tag} as base


FROM nginx
LABEL description="Static files of Hue service"

COPY --from=base /usr/share/hue/build/static/ /usr/share/nginx/html/hue/static

RUN rm /etc/nginx/conf.d/default.conf

COPY tools/docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY tools/docker/nginx/hue.conf /etc/nginx/sites-available/hue

RUN mkdir /etc/nginx/sites-enabled
RUN ln -s /etc/nginx/sites-available/hue /etc/nginx/sites-enabled/hue

EXPOSE 80
