---
title: Quick Start a Hue development environment in 3 minutes with Docker
author: Hue Team
type: post
date: 2019-07-24T16:28:55+00:00
url: /quick-start-a-hue-development-environment-in-3-minutes-with-docker/
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
  # - Version 4.5

---
Looking at simplifying the usage of Databases and Datawarehouses or learning how to build Cloud webapps? Hue would be a great candidate for you!

Typically the development is made [natively][1] but here is a new way to quickly get started with Docker:

    git clone https://github.com/cloudera/hue.git

    cd hue

    cp desktop/conf/pseudo-distributed.ini.tmpl desktop/conf/pseudo-distributed.ini

Then edit the `[[database]]` section to specify a proper database, here MySql:

    host=127.0.0.1 # Not localhost if Docker
    engine=mysql
    user=hue
    password=hue
    name=huedb


Then map the local Hue source code into the running container (so that local edits are seen in the running Hue):

    sudo docker run -it -v $PWD/apps:/usr/share/hue/apps -v $PWD/desktop:/usr/share/hue/desktop -v $PWD/desktop/conf/pseudo-distributed.ini:/usr/share/hue/desktop/conf/z-hue.ini --network="host" gethue/hue

And open-up <http://127.0.0.1:8888>!

<a href="https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-11-15-at-3.34.20-PM.png"><img src="https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-11-15-at-3.34.20-PM.png" /></a>


Note: code updates won&#8217;t be seen after the Docker container runs. For this Hue would need to be [started][3] in dev server mode by replacing the line by

    ./build/env/bin/hue runserver 0.0.0.0:8888

and it will auto-restart on Python code changes. For JavaScript, those would need to be [compiled][4].

&nbsp;

 [1]: https://docs.gethue.com/developer/
 [2]: https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-11-15-at-3.34.20-PM.png
 [3]: https://github.com/cloudera/hue/blob/master/tools/docker/hue/startup.sh#L5
 [4]: https://docs.gethue.com/developer/development/#javascript
