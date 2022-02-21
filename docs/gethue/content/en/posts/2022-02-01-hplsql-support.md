---
title: HPL/SQL Support
author: Hue Team
type: post
date: 2022-02-01T00:00:00+00:00
url: /blog/2022-02-01-hplsql-support
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
  - Version 4.11
  - Development
  - Query

---

HPL/SQL is an Apache open source procedural extension for SQL for Hive users. It has its own grammar. It is included with Apache Hive from version 2.0.

HPL/SQL is a hybrid and heterogeneous language that understands syntaxes and semantics of almost any existing procedural SQL dialect, and you can use it with any database. For example, you can run existing Oracle PL/SQL code on Apache Hive and Microsoft SQL Server, or Transact-SQL code on Oracle, Cloudera Impala, or Amazon Redshift.
For more information about the HPL/SQL language, see the [HPL/SQL Reference](http://www.hplsql.org/doc).

#### How to enable HPL/SQL dialect in Hue:
In the desktop/conf/hue.ini config file section, add the HPL/SQL interpreter:

    [notebook]
    [[interpreters]]
    [[[hplsql]]]
    name=Hplsql
    interface=hiveserver2

  **Note:** HPL/SQL uses the [beeswax config](https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/) like Hive uses.

#### Key features of HPL/SQL:
- Flow of Control Statements (FOR, WHILE, IF, CASE, LOOP, LEAVE, RETURN)
- Functions, procedures, and packages
- Built-in functions (string manipulations, datetime functions, conversions)
- Exception handling and conditions
- Constants and variable, assignment (DECLARE count INT := 1)
- Processing results using a CURSOR

#### HPL/SQL limitations:
- Some of the Hive specific CREATE TABLE parameters are missing
- No colon syntax to parametrize SQL strings
- No quoted string literals
- No GOTO and Label
- EXECUTE does not have output parameters
- Some complex data types, such as Arrays and Records are not supported
- No object-oriented extension

#### HPL/SQL examples:
The following example creates a function that takes the input of your name and returns "Hello `<name>`":

    CREATE PROCEDURE greet(name STRING)
    BEGIN
      PRINT 'Hello ' || name;
    END;
    greet('World');
![Example1](https://cdn.gethue.com/uploads/2022/02/Hplsql_example1.png)

The following example prints the sum of numbers between 1 and 10:

    declare sum int = 0;
    for i in 1..10 loop
      sum := sum + i;
    end loop;
    select sum;
![Example2](https://cdn.gethue.com/uploads/2022/02/Hplsql_example2.png)

**Attention:** In hplsql mode, you must terminate the commands using the forward slash character (/). The semicolon (;) is used throughout procedure declarations and can no longer be relied upon to terminate a query in the editor.


You can try this feature in the latest Hue version.  
</br>
</br>
For feedback, questions, or suggestions, feel free to comment here or on the [Forum](https://discourse.gethue.com/) and [quick start](https://docs.gethue.com/quickstart/) SQL querying!

Onwards!

Ayush from the Hue Team