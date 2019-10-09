
FROM nginx
LABEL description="Hue documentation docs.gethue.com"

RUN apt-get update -y && apt-get install -y \
  wget \
  python-pip

RUN wget https://github.com/gohugoio/hugo/releases/download/v0.58.3/hugo_0.58.3_Linux-64bit.deb
RUN dpkg -i hugo*.deb && rm hugo*.deb
RUN pip install Pygments

COPY tools/docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY tools/docker/documentation/docs.gethue.com.conf /etc/nginx/sites-available/docs.gethue.com

RUN mkdir /etc/nginx/sites-enabled

# Docs
ADD docs/docs-site /docs
WORKDIR /docs
RUN hugo

RUN mkdir -p /var/www/docs.gethue.com/html
RUN cp -R public/* /var/www/docs.gethue.com/html
RUN chmod -R 755 /var/www/docs.gethue.com
RUN ln -s /etc/nginx/sites-available/docs.gethue.com /etc/nginx/sites-enabled/docs.gethue.com
RUN rm -rf /docs

EXPOSE 80
