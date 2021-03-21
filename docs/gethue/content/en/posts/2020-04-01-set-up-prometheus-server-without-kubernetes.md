---
title: Set Up Prometheus Server without Kubernetes
author: Ying Chen
type: post
date: 2020-04-01T00:00:00+00:00
url: /set-up-prometheus-server-without-kubernetes/
sf_thumbnail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
sf_detail_type:
  - none
sf_page_title:
  - 1
sf_page_title_style:
  - standard
sf_no_breadcrumbs:
  - 1
sf_page_title_bg:
  - none
sf_page_title_text_style:
  - light
sf_background_image_size:
  - cover
sf_social_sharing:
  - 1
sf_related_articles:
  - 1
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
ampforwp-amp-on-off:
  - default
categories:
  - Version 4
#  - Version 4.7

---

To taste Hue prometheus metrics, you may set up a Prometheus server to scrape the [metrics](https://gethue.com/collecting-hue-metrics-with-prometheus-in-kubernetes/) endpoint /metrics on a Hue server (which may not need to run in docker or Kubernetes). Here is the set up example on Ubuntu 16.4.

**Prerequisites**: a Hue server running at localhost:8000.

1. Create a service user

	```console
	$ sudo useradd --no-create-home --shell /bin/false prometheus
	```
2. Create a directory in /etc for Prometheus’ configuration files and a directory in /var/lib for its data

	```console
	$ sudo mkdir /etc/prometheus
	$ sudo mkdir /var/lib/prometheus
	```
3. Set the user and group ownership on the new directories to the prometheus user

	```console
	$ sudo chown prometheus:prometheus /etc/prometheus
	$ sudo chown prometheus:prometheus /var/lib/prometheus
	```
4. Download Prometheus binary from [https://prometheus.io/download/](https://prometheus.io/download/)

	```console
	$ cd ~/Downloads
	$ curl -LO https://github.com/prometheus/prometheus/releases/download/v2.16.0/prometheus-2.16.0.linux-amd64.tar.gz
	```
5. Validate checksum value with download

	```console
	$ Sha256sum prometheus-2.16.0.linux-amd64.tar.gz
	```
6. Unpack the downloaded archive

	```console
	$ tar xvf prometheus-2.16.0.linux-amd64.tar.gz
	```
7. Copy the two binaries to the /usr/local/bin directory

	```console
	$ sudo cp prometheus-2.16.0.linux-amd64/prometheus /usr/local/bin/
	$ sudo cp prometheus-2.16.0.linux-amd64/promtool /usr/local/bin/
	```
8. Copy the consoles and console_libraries directories to /etc/prometheus.

	```console
	$ sudo cp -r prometheus-2.16.0.linux-amd64/consoles /etc/prometheus
	$ sudo cp -r prometheus-2.16.0.linux-amd64/console_libraries /etc/prometheus
	```
9. Set the user and group ownership on the directories to the prometheus user. Using the -R flag will ensure that ownership is set on the files inside the directory as well.

	```console
	$ sudo chown -R prometheus:prometheus /etc/prometheus/consoles
	$ sudo chown -R prometheus:prometheus /etc/prometheus/console_libraries
	```
10. Remove the leftover files from your downloads folder

	```console
	$ rm -rf prometheus-2.16.0.linux-amd64.tar.gz prometheus-2.16.0.linux-amd64
	```
11. Create a configuration file named prometheus.yml

	```console
	$ vi /etc/prometheus/prometheus.yml
	```

	Content of prometheus.yml, port 8000 is your Hue server port, and change it if needed.

	```console
	global:
	  scrape_interval: 15s

	scrape_configs:
	  - job_name: 'prometheus'
	    scrape_interval: 5s
	    static_configs:
	      - targets: ['localhost:9090']

	  - job_name: 'hue'
	    scrape_interval: 5s
	    static_configs:
	      - targets: ['localhost:8000']
	```
12. Set the user and group ownership on the configuration file to the prometheus user

	```console
	$ sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml
	```
13. Create a new systemd service file.

	```console
	$ vi /etc/systemd/system/prometheus.service
	```
	Content of service file

	```console
	[Unit]
	Description=Prometheus
	Wants=network-online.target
	After=network-online.target

	[Service]
	User=prometheus
	Group=prometheus
	Type=simple
	ExecStart=/usr/local/bin/prometheus \
	    --config.file /etc/prometheus/prometheus.yml \
	    --storage.tsdb.path /var/lib/prometheus/ \
	    --web.console.templates=/etc/prometheus/consoles \
	    --web.console.libraries=/etc/prometheus/console_libraries

	[Install]
	WantedBy=multi-user.target
	```
14. To use the newly created service, reload and start systemd.

	```console
	$ sudo systemctl daemon-reload
	$ sudo systemctl start prometheus
	```
When you open the browser at localhost:9090, you will see the Prometheus server page like the screenshot below.

![prometheus_with_metrics_list.png](https://cdn.gethue.com/uploads/2020/04/prometheus_with_metrics_list.png)

Any feedback or questions? Feel free to comment here or on the [Forum](https://discourse.gethue.com/) or [@gethue](https://twitter.com/gethue) and [quick start](https://docs.gethue.com/quickstart/) SQL querying!


Ying Chen from the Hue Team
