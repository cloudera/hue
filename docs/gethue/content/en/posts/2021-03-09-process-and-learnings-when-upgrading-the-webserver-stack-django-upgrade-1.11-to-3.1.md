---
title: Process & Learnings when upgrading the Webserver Stack - Django Upgrade (1.11 to 3.1)
author: Hue Team
type: post
date: 2021-03-09T00:00:00+00:00
url: /blog/2021-03-09-process-and-learnings-when-upgrading-the-webserver-stack-django-upgrade-1-to-3
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

---

The Hue project was started around [10 years](https://gethue.com/blog/2020-01-28-ten-years-data-querying-ux-evolution/) back. In the meantime some of our technologies were getting old or deprecated, hence we need to upgrade them for the bright future of HUE. So In this, the [Django](https://www.djangoproject.com/) upgrade was one of the most important ones. We were using Django 1.11 before this upgrade, for which extended support was ended in April 2020.
![Django roadmap](https://cdn.gethue.com/uploads/2021/03/Django_roadmap.png)

## Goal

* Hue running with Django 3.1 (latest) while still being able to compile/run with 1.11.

## Why Upgrade

* The older version of [Django 1.11 is deprecated](https://www.djangoproject.com/download/#supported-versions) (e.g. no longer receiving security updates or improvements).
* Django 1.11 requires Python 2 which is also [deprecated](https://docs.djangoproject.com/en/3.1/faq/install/#what-python-version-should-i-use-with-django).
* [New features, bug fixes and improvements](https://docs.djangoproject.com/en/dev/internals/deprecation/) are added.
* Upgrading as each new Django release is available makes future upgrades less painful by keeping your code base up to date.
* Some features or libraries do not support the older version of Django (e.g. [DjangoRest framework](https://www.django-rest-framework.org/#requirements)).

## Challenges

* Don’t break the backward compatibility i.e. supports both versions in the same code base (when no choice, we use if sys.version_info[0] < 3 switches).
* Some of our product dependencies may not yet support the new Django version. In these cases, we might have to wait until new versions of dependencies are released.

## Plan

* Major tradeoff:
  * Python 3 build of Hue will move to Django 3.
  * Python 2 will stay with Django 1.11 (as Django 1.11 is the latest version supporting Python 2 anyway)
* Move slowly but perfectly and not go backward, so we decided that we will upgrade Django step by step from 1.11 to 2.0 then 2.0 to 2.1 then 2.1 to 2.2 then 2.2 to 3.0 then 3.0 to 3.1.
* Resolves the deprecation warnings raised by the current Django version and save them in google sheet before upgrading to the next version.
* After resolving the warnings upgrade Django to the next version as per plan.
* Run all [unit tests](https://docs.gethue.com/developer/development/#testing) for both versions (the last one and the upgraded one). If a test fails then need to correct either unit test or the related upgraded part.
* For the consistent and automated way to build, package, and test, we are using [CircleCI](https://circleci.com/product/#how-it-works).
  * ![Passed CircleCi](https://cdn.gethue.com/uploads/2021/03/Passed_CircleCi.png)
  * Each commit was passing through CircleCI and as we can see in above screenshot that CircleCI is checking the code for both the versions (build-py3.6 -> Django 3 and build -> Django 1.11).
  * ![Failed CircleCi](https://cdn.gethue.com/uploads/2021/03/Failed_CircleCi.png)
  * And in this screenshot, we can see that commit gets failed for Django 1.11 (build). So this is the indication that our code is failing for Django 1.11 so need to change the code accordingly.
* After following all the above steps each time we are good to go with the new version.
* Rinse and repeat :)

## Main changes and Learnings

* From Django 1.11 to 2.0
  * Mainly in this transition, we need to make 2 types of correction for the upgrade
    * Functional arguments added or deprecated
    * Older Dependencies do not support the new version of Django
  * But there was one major change named “Old-style middleware using settings.MIDDLEWARE_CLASSES is deprecated” So there were two ways to do it.
    * Writing your own middleware.
    * Upgrading pre-Django 1.10-style middleware.
  * As we want backward compatibility so we go with the later one and followed the [instructions](https://docs.djangoproject.com/en/1.10/topics/http/middleware/#upgrading-pre-django-1-10-style-middleware) carefully.


* From Django 2.0 to 2.1
  * In this upgradation there is one major change named “desktop.auth.backend.AllowFirstUserDjangoBackend.authenticate() to accept a positional `request` argument “ so the challenge is to make it compilable with both Python 2 + Django 1.11 and Python 3 + Django 2.1 so we overcome this problem by using sys.version_info[0] flag (i.e. python version).
    * But during the above up-gradation, we missed the LDAP authentication function, so this problem came up when we’re on Django 3, although we were able to solve this problem but real lesson was to add unit tests for everything wherever possible so we added the mock unit test for LDAP auth.


* From Django 2.1 to 2.2
  * The major issue was related to the Django admin app. Basically, Django 2.2 was giving the error with admin app, so we found that may be the reason is mako template but we didn’t spend time on this because we were not using Django admin as such and also replacing the mako to [Vue.js](https://gethue.com/blog/vue3-build-cli-options-composition-api-template-web-components-hue/), so we disabled it and move on with thinking that if needed in future, we will add it.


* From Django 2.2 to 3.0
  * In this transition, we got an error regarding third-party dependency named ‘django-babel’ supports only till Django 2.2. After discussion, we found that we can [fork](https://github.com/gethue/django-babel) it and change the setup.py file and the things accordingly and make it work for Django 3.0.


* From Django 3.0 to 3.1
  * As such no major changes, only ‘STATICFILES_STORAGE’  changed from CachedStaticFilesStorage to ManifestStaticFilesStorage.

## And now give Hue with Django 3 a spin!
  ```
  git clone https://github.com/cloudera/hue.git   # Clone the Hue repository
  export PYTHON_VER=python3.8                     # Before build set the Pyhton_VER like
  make apps                                       # build the apps
  ./build/env/bin/hue runserver
  ```
  Note: If you are facing any issues please follow this [link](https://docs.gethue.com/developer/development/).

</br>
</br>

Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!


Onwards!

Ayush from the Hue Team
