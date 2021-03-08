---
title: Automatically checking documentation and website dead links with Continuous Integration
author: Romain
type: post
date: 2020-03-11T00:00:00+00:00
url: /checking-dead-links-automatically-continuous-integration/
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

Hi Data Crunchers,

Continuous integration and automation are investment that enable a major scaling in the resource and quality of software projects. This past year saw a lot of improvements with an [integrated commit flow](https://gethue.com/improving-the-developer-productivity-with-some-continuous-integration/) and adding series of checks like linting of JavaScript, also running Python 3 tests automatically...

This also create a virtuous circle that encourages developers to add more tests on their own (e.g. +200 since the beginning of this year), as all the plumbing is already done for them.


![CI workflow](https://cdn.gethue.com/uploads/2020/03/ci-both-python.png)
CI workflow

![List of CI checks](https://cdn.gethue.com/uploads/2020/03/ci-checks-lints-docs.png)
List of CI checks

Next item on the list to automate was the automated checking of deadlinks of https://docs.gethue.com and https://gethue.com/ that was previously [manual](https://gethue.com/easily-checking-for-deadlinks-on-docs-gethue-com/).


![New website deadlinks check](https://cdn.gethue.com/uploads/2020/03/ci-linting-docs.png)
New website deadlinks check


Overall the [action script](https://github.com/cloudera/hue/blob/master/tools/ci/check_for_website_dead_links.sh) will:

* Check if the new commits containing a documentation of website change
* Then boot `hugo` to locally serve the site
* And run `muffet` to crawl and checks the links

![Link checking failure](https://cdn.gethue.com/uploads/2020/03/ci-link-failure.png)
Link checking failure

Note: it is handy to had some URL blacklist and lower number of concurrent crawler connections to avoid hammering some external websites (e.g. https://issues.cloudera.org/browse/HUE which contains a lot of references).



What is your favorite CI process? Any feedback? Feel free to comment here or on [@gethue](https://twitter.com/gethue)!
