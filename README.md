<div align="center">

# Hue - SQL Assistant for Databases and Data Warehouses

![Hue Logo](https://raw.githubusercontent.com/cloudera/hue/master/docs/images/hue_logo.png)

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/cloudera/hue/commitflow-py3.yml?style=for-the-badge&logo=githubactions)
[![Docker Pulls](https://img.shields.io/docker/pulls/gethue/hue?style=for-the-badge&logo=docker&color=blue)](https://registry.hub.docker.com/u/gethue/hue/)
[![GitHub contributors](https://img.shields.io/github/contributors-anon/cloudera/hue?style=for-the-badge&logo=github)](https://github.com/cloudera/hue/graphs/contributors)
[![GitHub stars](https://img.shields.io/github/stars/cloudera/hue?style=for-the-badge&logo=github&color=yellow)](https://github.com/cloudera/hue/stargazers)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge&logo=opensourceinitiative)](LICENSE.txt)

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/cloudera/hue)

**Query. Explore. Share.**

</div>

## 🗄️ Overview

Hue is a mature SQL Assistant for querying Databases & Data Warehouses, trusted by:

* **1000+ customers** worldwide
* **Top Fortune 500** enterprises 

Organizations use Hue to quickly answer questions via self-service querying, executing hundreds of thousands of queries daily.

### Key Features

- ✏️ **Interactive SQL editing** with syntax highlighting and autocomplete
- 📁 **File Browser** for navigating and operating on HDFS, S3, ABFS, Ozone, and Google Storage (GS) files
- 📊 **Job Browser** for monitoring and managing Hive queries, Impala queries, YARN applications, and Livy Spark jobs
- 🗃️ **Table Browser** for exploring and managing database tables, schemas, and metadata
- 📤 **Table Importer** for creating Hive and Impala tables from CSV/Excel files, with support for uploading from local system or importing from remote filesystems (HDFS, S3, ABFS, Ozone, GS)
- 🔗 **Multiple database connectors** including Hive, Impala, MySQL, PostgreSQL, and more

## 🔗 Useful Links

- 🏠 **Website**: [gethue.com](https://gethue.com)
- 🔌 **Connect to a database**: [Configuration Guide](https://docs.gethue.com/administrator/configuration/connectors/)
- 🛠️ **Build your own Editor**: [SQL Scratchpad](https://docs.gethue.com/developer/components/scratchpad/)
- ⚙️ **Query Service**: [Kubernetes Setup](https://docs.gethue.com/administrator/installation/cloud/#kubernetes) and [API](https://docs.gethue.com/developer/api/)

![Hue Editor](https://cdn.gethue.com/uploads/2021/02/hue-4.9.png)

## 🚀 Getting Started

### Try Hue Now

- 🌐 **Live demo**: [demo.gethue.com](https://demo.gethue.com/)
- 🧪 **Quick integrations**:
  - [Hive](https://docs.gethue.com/administrator/configuration/connectors/#apache-hive)
  - [Impala](https://gethue.com/blog/quickstart-sql-editor-for-apache-impala/)
  - [Trino/Presto](https://docs.gethue.com/administrator/configuration/connectors/#trino-presto)
  - [Phoenix SQL / HBase](https://gethue.com/blog/querying-live-kafka-data-in-apache-hbase-with-phoenix/)
  - [Spark SQL](https://gethue.com/blog/querying-spark-sql-with-spark-thrift-server-and-hue-editor/)

Choose one of these deployment options to start the server, then [configure the databases](https://docs.gethue.com/administrator/configuration/connectors/) you want to query:

### 🐳 Docker

Start Hue instantly:

```bash
docker run -it -p 8888:8888 gethue/hue:latest
```

Hue will be available at [http://localhost:8888](http://localhost:8888)

📖 See the [Docker Guide](https://github.com/cloudera/hue/tree/master/tools/docker/hue) or watch the [Quick Start Video](http://gethue.com/getting-started-with-hue-in-2-minutes-with-docker/)

### ☸️ Kubernetes

```bash
helm repo add gethue https://helm.gethue.com
helm repo update
helm install hue gethue/hue
```

📖 Read more about configurations in the [Kubernetes docs](tools/kubernetes/)

### 💻 Development Setup

#### Quick Start with Docker

Use the [Dev Environment Docker](https://docs.gethue.com/developer/development/#dev-docker) for the fastest setup.

#### Manual Setup

1. Install [dependencies](https://docs.gethue.com/administrator/installation/dependencies/)
2. Clone and build:

```bash
git clone https://github.com/cloudera/hue.git
cd hue
make apps
build/env/bin/hue runserver
```

Hue will be available at [http://localhost:8000](http://localhost:8000)

📖 Read more in the [development documentation](https://docs.gethue.com/developer/development/)

## 🧩 Components

Hue offers several powerful components:

- **SQL Editor** - Interactive query interface
- **SQL Parsers** - Syntax handling for multiple dialects
- **REST/Python/CLI APIs** - Programmatic access to all functionality

📖 Learn about [components](https://docs.gethue.com/developer/components/) and [APIs](https://docs.gethue.com/developer/api/)

## 🤝 Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) guide to get started.

## 📜 License

[Apache License, Version 2.0](LICENSE.txt)
