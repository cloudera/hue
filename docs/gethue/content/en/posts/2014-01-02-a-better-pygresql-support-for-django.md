---
title: A better PyGreSql support for Django
author: admin
type: post
date: 2014-01-02T21:33:40+00:00
url: /a-better-pygresql-support-for-django/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/72002742226/a-better-pygresql-support-for-django
tumblr_gethue_id:
  - 72002742226
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
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
categories:
  - Development

---
<p id="docs-internal-guid-4b2195c3-54dc-08d4-5d6f-c137c78b95a2">
  <span>With the release of </span><a href="https://github.com/abec/django-pygresql"><span>django-pygresql</span></a><span>, the </span><a href="http://gethue.com"><span>Hue</span></a><span> team has taken a first stab at </span><a href="http://www.pygresql.org/"><span>PyGreSQL</span></a><span> support in </span><a href="https://www.djangoproject.com/"><span>Django</span></a><span>!</span>
</p>

# <span>The ‘Why’</span>

<span>The open source world has many different kinds of licenses and it can be confusing to know which one makes sense for you. PyGreSQL is a </span>[<span>PostgreSQL</span>][1] <span>client with a permissible enough license that it can be packaged and shipped.</span>

# <span>The ‘How’</span>

<span>PyGreSQL has some minor differences from the provided postgresql backend. It required a few changes including:</span>

  * <span>Massaging Date/Datetime/Time types to work with Django.</span>
  * <span>A custom cursor for massaging data.</span>
  * <span>Custom autocommit management.</span>

&nbsp;

<span>To install this backend:</span>

  1. <span>Download </span>[<span>django-pygresql</span>][2]<span>.</span>
  2. <span>Run</span> <pre class="code">unzip master.zip && cd django-pygresql-master && /build/env/bin/python install setup.py</pre>

  3. <span>At the bottom of <hue root>/desktop/core/src/desktop/settings.py, add the following code:</span>

<pre class="code">if DATABASES['default']['ENGINE'] == 'django_pygresql':
  SOUTH_DATABASE_ADAPTERS = {
    'default': 'south.db.postgresql_psycopg2'
  }</pre>

<ol start="4">
  <li>
    <span>In the hue.ini, set desktop->database->engine to “django_pygresql”. Then, add the normal postgresql configuration parameters.</span>
  </li>
</ol>

# <span>Summary</span>

<span>This is an initial implementation of a backend for Django to communicate with PostgreSQL via PyGreSQL. We hope this helps other members of the community.</span>

&nbsp;

<span>Write to us at</span>[<span>hue-user</span>][3] <span>mailing list or</span>[<span>@gethue</span>][4]<span>!</span>

 [1]: http://www.postgresql.org/
 [2]: https://github.com/abec/django-pygresql/archive/master.zip
 [3]: http://groups.google.com/a/cloudera.org/group/hue-user
 [4]: https://twitter.com/gethue
