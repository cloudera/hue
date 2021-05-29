---
title: Build your own SQL Editor (BYOE) in 5 minutes via Sql Scratchpad component and public REST API.
author: Hue Team
type: post
date: 2021-05-29T00:00:00+00:00
url: /blog/2021-05-29-create-own-sql-editor-via-webcomponent-and-public-api
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
  - Version 4.10
  - Development
  - Query

---

Leveraging the new Hue’s SQL Scratchpad Web Component and REST API into your own project.

The [Hue SQL Editor](https://gethue.com/) project has been evolving for more than [10 years](https://gethue.com/blog/2020-01-28-ten-years-data-querying-ux-evolution/) and allows you to query any Database or Data Warehouse. Segmenting the overall project into fully decoupled components is one reason it could rapidly evolve and still be alive after so long.

The already popular [SQL Parser](https://docs.gethue.com/developer/components/parsers/) component is now joined by the [SQL Scratchpad](https://docs.gethue.com/developer/components/scratchpad/) component.

![The SQL Scratchpad is a lightweight repackaging of the mature Hue SQL Editor](https://cdn-images-1.medium.com/max/2494/0*XnfuFshfdqc9vX74.png)*The SQL Scratchpad is a lightweight repackaging of the mature Hue SQL Editor*
> <sql-scratchpad />

One major added benefit is that now the Editor is easy to share and integrate, hence making a strong case for avoiding to re-invent the wheel and re-create various duplicated SQL Editors instead of focusing on making a single one better for the end users.

Here is a live demo of how easy it is to add the component:

![Adding the component in 3 lines and watching the interaction with the public API of demo.gethue.com](https://cdn-images-1.medium.com/max/2356/1*yXRjYQN_eRUimzlXPl5SwQ.gif)*Adding the component in 3 lines and watching the interaction with the public API of demo.gethue.com*

### How it works

![The SQL Editor is a module published to a registry called NPM. The component can then be integrated in any Web page. It then communicates via a REST API with the Hue server which interacts with the Databases we want to query.](https://cdn-images-1.medium.com/max/2242/1*stLGGVTXa_V_PK2s1i6vIQ.png)*The SQL Editor is a module published to a registry called NPM. The component can then be integrated in any Web page. It then communicates via a REST API with the Hue server which interacts with the Databases we want to query.*

**Query Editor Component**

Here is how easy it is to integrate it into a Web page. Copy paste the HTML code below into an index.html file and open it with FireFox:

    <!DOCTYPE html>
    <html>

    <head>
      <title>SQL Scratchpad</title>
      <script type="text/javascript" src="https://unpkg.com/gethue/lib/components/SqlScratchpadWebComponent.js"></script>
    </head>

    <body>
      <div style="position: absolute; height: 100%; width: 100%">
        <sql-scratchpad api-url="https://demo.gethue.com" username="demo" password="demo" dialect="hive" />
      </div>
    </body>

    </html>

And “that’s it”!

![Directly opening the local HTML page with Firefox](https://cdn-images-1.medium.com/max/2000/1*JzVbsWHqzZPI2pEAhG2mwQ.png)
<br>*Directly opening the local HTML page with Firefox*

The autocomplete is powered by the local parser and will show-up. It obviously can only help with the SQL syntax on its own. In order to get the dynamic content like the list of tables, columns… and execute SQL queries, the component needs to point to a Query API.

For the next steps and integrating deeper the component, have a look to the [NPM Hue registry](https://www.npmjs.com/package/gethue).

**Query Editor API**

To be truly alive, the Editor component needs to talk to the service that can authenticate the user and execute the queries.

This is possible via the new [public REST API](https://docs.gethue.com/developer/api/rest/#execute-a-query) which is much simpler to use than before and follows nowadays standards. It leverages the exact same authentication as the regular login page and only requires to provide a JWT token afterwards.

For example, simply ask for an access token:

    curl -X POST https://demo.gethue.com/api/token/auth -d 'username=demo&password=demo'

Then provide the token value in each following calls.

    curl -X POST https://demo.gethue.com/api/editor/execute/hive --data 'statement=SHOW TABLES' -H "Authorization: Bearer <token value>"

The endpoints for executing SQL queries have been greatly simplified and now only ask for the essential like which SQL dialect and query statement or the id of the query previously sent for execution:

    curl -X POST https://demo.gethue.com/api/editor/check_status --data 'operationId=63ce87ba-ca0f-4653-8aeb-e9f5c1781b78'

This first release lets you edit and execute SQL content. Popular functionalities of the full editor are gradually being integrated, e.g.

* Query formatting and sharing
* Result downloading
* Open Scratchpad in a popup (e.g. for editing embedded SQL in PySpark)...

An option to SSO and look-up a local JWT token in order to not require the credentials is coming soon.

The [SQL Scratchpad component](https://docs.gethue.com/developer/components/scratchpad/) and its API are rapidly evolving. Now is a great time to give it a try and [send feedback](https://github.com/cloudera/hue/issues) or contribute!

Onwards!

Romain from the Hue Team
