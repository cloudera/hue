# Welcome to Hue NGINX (http://gethue.com) Dockerfile

FROM nginx
LABEL description="Image for Webserver"

COPY --from=gethue/hue:latest /usr/share/hue/build/static/ /usr/share/nginx/html/hue/static

RUN rm /etc/nginx/conf.d/default.conf

COPY tools/docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY tools/docker/nginx/hue.conf /etc/nginx/sites-available/hue

RUN mkdir /etc/nginx/sites-enabled
RUN ln -s /etc/nginx/sites-available/hue /etc/nginx/sites-enabled/hue

EXPOSE 80
