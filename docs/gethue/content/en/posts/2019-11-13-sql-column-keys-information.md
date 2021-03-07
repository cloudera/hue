---
title: Visually surfacing SQL information like Primary Keys, Foreign Keys, Views and Complex Types
author: Hue Team
type: post
date: 2019-11-13T02:36:35+00:00
url: /2019-11-13-sql-column-assist-icons/
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
  - Version 4
# - Version 4.6

---
Hi SQL crunchers,

The Datawarehouse ecosystem with [Apache Hive](https://hive.apache.org/) and [Apache Impala](https://impala.apache.org/) is getting more complete with the introduction of [transactions](https://cwiki.apache.org/confluence/display/Hive/Hive+Transactions). In practice, this means your tables can now support `Primary Keys`, `INSERTs`, `DELETEs` and `UPDATEs` as well as `Partition Keys`.

Here is a tutorial demoing how Hue's SQL Editor helps you quickly visualize and use these instructions via its [assists](https://docs.gethue.com/user/concept/) and [autocomplete](https://docs.gethue.com/user/querying/#autocomplete) components.


![Assist All Keys](https://cdn.gethue.com/uploads/2019/11/sql_column_pk.png)


## Primary Keys

Primary Keys shows up like Partition Keys with the lock icon:

![Assist Primary Keys](https://cdn.gethue.com/uploads/2019/11/sql_columns_assist_pks.png)

Here is an example of SQL for using them:

    CREATE TABLE customer (
        first_name string,
        last_name string,
        website string,
        PRIMARY KEY (first_name, last_name) DISABLE NOVALIDATE
    );

[Apache Kudu](https://kudu.apache.org/) is supported as well:

    CREATE TABLE students (
      id BIGINT,
      name STRING,
      PRIMARY KEY(id)
    )
    PARTITION BY HASH PARTITIONS 16
    STORED AS KUDU
    TBLPROPERTIES ('kudu.num_tablet_replicas' = '1')
    ;

## Foreign Keys

When a column value points to another column in another table. e.g. The head of the business unit must exist in the person table:

![Assist Foreign Keys](https://cdn.gethue.com/uploads/2020/03/assist_foreign_keys_icons.png)

    CREATE TABLE person (
      id INT NOT NULL,
      name STRING NOT NULL,
      age INT,
      creator STRING DEFAULT CURRENT_USER(),
      created_date DATE DEFAULT CURRENT_DATE(),

      PRIMARY KEY (id) DISABLE NOVALIDATE
    );

    CREATE TABLE business_unit (
      id INT NOT NULL,
      head INT NOT NULL,
      creator STRING DEFAULT CURRENT_USER(),
      created_date DATE DEFAULT CURRENT_DATE(),

      PRIMARY KEY (id) DISABLE NOVALIDATE,
      CONSTRAINT fk FOREIGN KEY (head) REFERENCES person(id) DISABLE NOVALIDATE
    );

## Partition Keys

Partitioning of the data is a key concept for optimizing the querying. Those special columns are also shown with a key icon:

![Assist Column Partition Keys](https://cdn.gethue.com/uploads/2019/11/sql_columns_assist_keys.png)

Here is an example of SQL for using them:

    CREATE TABLE web_logs (
        _version_ BIGINT,
        app STRING,
        bytes SMALLINT,
        city STRING,
        client_ip STRING,
        code TINYINT,
        country_code STRING,
        country_code3 STRING,
        country_name STRING,
        device_family STRING,
        extension STRING,
        latitude FLOAT,
        longitude FLOAT,
        `METHOD` STRING,
        os_family STRING,
        os_major STRING,
        protocol STRING,
        record STRING,
        referer STRING,
        region_code BIGINT, request STRING,
        subapp STRING,
        TIME STRING,
        url STRING,
        user_agent STRING,
        user_agent_family STRING,
        user_agent_major STRING,
        id STRING
    )
    PARTITIONED BY ( `date` STRING);

    INSERT INTO web_logs
    PARTITION (`date`='2019-11-14') VALUES
    (1480895575515725824,'metastore',1041,'Singapore','128.199.234.236',127,'SG','SGP','Singapore','Other',NULL,1.2930999994277954,103.85579681396484,'GET','Other',NULL,'HTTP/1.1',NULL,'-',0,'GET /metastore/table/default/sample_07 HTTP/1.1','table','2014-05-04T06:35:49Z','/metastore/table/default/sample_07','Mozilla/5.0 (compatible; phpservermon/3.0.1; +http://www.phpservermonitor.org)','Other',NULL,'8836e6ce-9a21-449f-a372-9e57641389b3')

## Nested Types

Complex or Nested Types are handy for storing associated data close together. The assist lets you expand the tree of columns:

![Assist Nested Types](https://cdn.gethue.com/uploads/2019/11/sql_columns_assist_nested_types.png)

Here is an example of SQL for using them:

    CREATE TABLE subscribers (
      id INT,
      name STRING,
      email_preferences STRUCT<email_format:STRING,frequency:STRING,categories:STRUCT<promos:BOOLEAN,surveys:BOOLEAN>>,
      addresses MAP<STRING,STRUCT<street_1:STRING,street_2:STRING,city:STRING,state:STRING,zip_code:STRING>>,
      orders ARRAY<STRUCT<order_id:STRING,order_date:STRING,items:ARRAY<STRUCT<product_id:INT,sku:STRING,name:STRING,price:DOUBLE,qty:INT>>>>
    )
    STORED AS PARQUET

## Views

It can be sometimes confusing to not recognize that a table is instead a view. Views are shown with this little eye icon:

![Assist Nested Types](https://cdn.gethue.com/uploads/2019/11/sql_assist_view_icon.png)

Here is an example of SQL for using them:

    CREATE VIEW web_logs_november AS
    SELECT * FROM web_logs
    WHERE `date` BETWEEN '2019-11-01' AND '2019-12-01'


## Transactional Operations

Transactional tables now support these SQL instructions to update the data.

### Inserts

Here is how to add some data into a table. Previously, he was only possible to do this via LOADING some files.

    INSERT INTO TABLE customer
    VALUES
      ('Elli', 'SQL', 'gethue.com'),
      ('John', 'SELECT', 'docs.gethue.com')
    ;

### Deletes

Deletion of rows of data:

    DELETE FROM customer
    WHERE first_name = 'John';

### Updates

How to update the value of some columns in certain rows:

    UPDATE customer
    SET website = 'helm.gethue.com'
    WHERE first_name = 'Elli';


Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!


Romain, from the Hue Team
