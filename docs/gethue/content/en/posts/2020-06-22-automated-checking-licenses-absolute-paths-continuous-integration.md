---
title: Automated checks for JavaScript modules compatible licenses and non absolute paths with Continuous Integration
author: Romain
type: post
date: 2020-06-22T00:00:00+00:00
url: /automated-checking-javascript-licenses-absolute-paths-continuous-integration/
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
  - Development
#  - Version 4.8

---

Hi Interface Builders,

The investment in Continuous Integration (CI) and automation continues in order to help scale the resource and quality of the Hue project. This past year saw a lot of improvements with an [integrated commit flow](https://gethue.com/improving-the-developer-productivity-with-some-continuous-integration/) and adding series of [link checking](https://gethue.com/checking-dead-links-automatically-continuous-integration/) automatically run by [Circle CI](https://circleci.com/gh/cloudera/hue).

Here is the latest about how to automatically check that JavaScript artifacts have the correct licensing and do not contain absolute paths.

## Licensing

Hue is an [Apache 2 licensed](https://www.apache.org/licenses/LICENSE-2.0) project, making it easy to contribute back to or be incorporated into other projects. One caveat is that we should be careful to not bundle libraries not as permissive like the GPL or LGPL. In order not to miss it, a new check [check-license](https://github.com/cloudera/hue/tree/master/tools/license) validates that all the JavaScript modules are compatible:

    npm run check-license

Which is then easily integrated into the [Hue CI](https://github.com/cloudera/hue/blob/master/.circleci/config.yml#L124):

    - run:
        name: run npm license checker
        command: |
          cd /usr/share/hue
          npm run check-license

![ci npm license checker](https://cdn.gethue.com/uploads/2020/06/ci-nmp-license-checker.png)

## Absolute paths

It is good practice to not ship any release artifact containing full file paths of the build machine. This helps guarantee that the artifacts are portable and do not leak unnessary information.

Hue already leverages the [removeNPMAbsolutePaths](https://github.com/juanjoDiaz/removeNPMAbsolutePaths) script but somehow this one was missing paths introduced by Vue.js. A short additional check [check-absolute-paths](https://github.com/cloudera/hue/tree/master/tools/detect-absolute-paths) was recently added to take care of the issue.

    npm run check-absolute-paths

And it was also added in the CI:

    - run:
        name: run npm absolute path detection
        command: |
          cd /usr/share/hue
          npm run check-absolute-paths

And that's it, more development time is saved for later!

What is your favorite CI process? Any feedback? Feel free to comment here or on [@gethue](https://twitter.com/gethue)!

Johan & Romain from the Hue Team
