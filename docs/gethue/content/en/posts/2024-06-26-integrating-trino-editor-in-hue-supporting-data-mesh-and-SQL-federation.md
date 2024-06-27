---
title: "Integrating Trino Editor in Hue: Supporting Data Mesh and SQL Federation"
author: Hue Team
type: post
date: 2024-06-26T00:00:00+00:00
url: /blog/2024-06-26-integrating-trino-editor-in-hue-supporting-data-mesh-and-SQL-federation
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
sf_remove_promo_bar:
  - 1
ampforwp-amp-on-off:
  - default
categories:
  - Version 5.0
  - Trino

---

Hello Everyone!

Hue Editor, the open-source SQL Assistant for querying databases and data warehouses, is now extending its support to Trino. This integration marks a significant step in enhancing data mesh and SQL federation capabilities.

### What is Trino?

[Trino](https://trino.io/docs/current/) is a powerful tool for querying massive datasets, particularly useful for those dealing with terabytes or petabytes of data. Unlike traditional tools that rely on MapReduce jobs, Trino efficiently handles distributed queries across various data sources, including Hadoop's HDFS, relational databases, and NoSQL systems like Cassandra. It's designed for data warehousing and analytics, making it ideal for tasks such as data analysis and report generation. Trino continues to be developed independently by its community and offers robust support for querying large datasets.

### Integrating Trino in Hue

To support Trino in Hue, we're leveraging the official [Trino Python client](https://github.com/trinodb/trino-python-client). This client provides a robust and efficient way to connect to Trino databases using the DBAPI. By integrating this client, we ensure better compatibility, ongoing support, and access to extensive documentation, facilitating seamless querying and data analysis capabilities within the Hue environment.


### Configuration

To configure the Trino editor in Hue, update the hue.ini file as follows:

    [notebook]
    [[interpreters]]
    [[[trino]]]
    name=Trino
    interface=trino
    options='{"url": "http://localhost:8080",  "auth_username": "", "auth_password":""}'


**Note:** Currently, only [basic LDAP authentication](https://github.com/trinodb/trino-python-client?tab=readme-ov-file#basic-authentication) using username and password or password script is supported. Alternatively, you can establish unsecured Trino connections.

### Getting Started

1. Launch a Trino container using Docker: `docker run --name trino -d -p 8080:8080 trinodb/trino`
2. Configure Hue: Add the Trino configuration to the hue.ini file as shown above.
3. Test and Validate: Test the integration by querying the Trino database through Hue. Ensure all functionalities are working as expected.

By integrating Trino into Hue, you can leverage enhanced SQL federation and data mesh capabilities, providing a more robust and versatile data querying experience.

You can try this feature in the latest [Hue](https://demo.gethue.com/hue/editor/?type=trino) version.  
</br>
</br>
For feedback, questions, or suggestions, feel free to comment on the [GitHub Discussions](https://github.com/cloudera/hue/discussions) and [quick start](https://docs.gethue.com/quickstart/) SQL querying!

Upwards and Onwards!


[Ayush](https://github.com/agl29) from the Hue Team
