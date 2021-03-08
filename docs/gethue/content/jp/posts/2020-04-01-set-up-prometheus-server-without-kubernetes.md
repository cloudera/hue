---
title: Kubernetes を使用せずに Prometheus Server をセットアップする
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

Hue prometheus のメトリクスを味わうには、Hue Server 上の [metrics](https://gethue.com/collecting-hue-metrics-with-prometheus-in-kubernetes/) エンドポイント /metrics をスクレイプするように prometheus サーバーを設定すると良いでしょう。(これは Docker や Kubernetes で実行する必要はないかもしれません)。以下は ubuntu 16.4 での設定例です。

**前提条件**: Hue server は localhost:8000 で実行されていること

1. サービスユーザーを作成します

```console
	$ sudo useradd --no-create-home --shell /bin/false prometheus
```

2. Prometheus の設定ファイル用に /etc にディレクトリを作成し、/var/lib にデータ用のディレクトリを作成します

```console
	$ sudo mkdir /etc/prometheus
	$ sudo mkdir /var/lib/prometheus
```
3. 新しいディレクトリのユーザーとグループを prometheus ユーザーに設定します

```console
	$ sudo chown prometheus:prometheus /etc/prometheus
	$ sudo chown prometheus:prometheus /var/lib/prometheus
```
4. Prometheus のバイナリを [https://prometheus.io/download/](https://prometheus.io/download/) からダウンロードします

```console
	$ cd ~/Downloads
	$ curl -LO https://github.com/prometheus/prometheus/releases/download/v2.16.0/prometheus-2.16.0.linux-amd64.tar.gz
```
5. チェックサムを検証します

```console
	$ Sha256sum prometheus-2.16.0.linux-amd64.tar.gz
```
6. ダウンロードしたアーカイブを解凍します

```console
	$ tar xvf prometheus-2.16.0.linux-amd64.tar.gz
```
7. 2つのバイナリを /usr/local/bin ディレクトリにコピーします

```console
	$ sudo cp prometheus-2.16.0.linux-amd64/prometheus /usr/local/bin/
	$ sudo cp prometheus-2.16.0.linux-amd64/promtool /usr/local/bin/
```
8. consoles と console_libraries ディレクトリを /etc/prometheus にコピーします

```console
	$ sudo cp -r prometheus-2.16.0.linux-amd64/consoles /etc/prometheus
	$ sudo cp -r prometheus-2.16.0.linux-amd64/console_libraries /etc/prometheus
```
9. ディレクトリのユーザーとグループを prometheus ユーザーに設定します。-R フラグを使用して、ディレクトリ内のファイルにも所有者が設定されるようにしてください

```console
	$ sudo chown -R prometheus:prometheus /etc/prometheus/consoles
	$ sudo chown -R prometheus:prometheus /etc/prometheus/console_libraries
```
10. ダウンロードしたフォルダから残りのファイルを削除します

```console
	$ rm -rf prometheus-2.16.0.linux-amd64.tar.gz prometheus-2.16.0.linux-amd64
```
11. prometheus.yml という名前の設定ファイルを作成します

```console
	$ vi /etc/prometheus/prometheus.yml
```

prometheus.yml の port 8000 は Hue server のポートです。必要に応じて変更してください。

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
12. 設定ファイルのユーザーとグループを prometheus ユーザーに設定します

```console
	$ sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml
```
13. 新しい systemd サービスファイルを作成します

```console
	$ vi /etc/systemd/system/prometheus.service
```
サービスファイルの内容

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

14. 新しく作成したサービを使用して、systemd をリロードして開始します。

```console
	$ sudo systemctl daemon-reload
	$ sudo systemctl start prometheus
```
ブラウザで localhost:9009 を開くと、次のスクリーンショットのような Prometheus サーバーのページがご覧になれます。

![prometheus_with_metrics_list.png](https://cdn.gethue.com/uploads/2020/04/prometheus_with_metrics_list.png)

フィードバックや質問はありますか？何かあれば [Forum](https://discourse.gethue.com/) や [@gethue](https://twitter.com/gethue) までお気軽にコメントください。[quick start](https://docs.gethue.com/quickstart/) で SQL のクエリを楽しんでください！


Ying Chen from the Hue Team
