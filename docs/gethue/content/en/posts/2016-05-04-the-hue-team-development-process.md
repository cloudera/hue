---
title: The Hue team development process
author: admin
type: post
date: 2016-05-04T14:34:51+00:00
url: /the-hue-team-development-process/
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
sf_remove_promo_bar:
  - 1
categories:
  - Development
#  - News

---
Hello potential Hue developers! 🙂

We want to share with you the development process we've been refining during the past years. This is what makes the Hue team ultra fast and efficient.

Ready? Go!

<ul class="airy">
  <li>
    All the changes (new features, improvements, bugs) need to be tracked. We use <a href="http://issues.cloudera.org">JIRA</a>.
  </li>
  <li>
    The changes should have a pseudo-mnemonic short ID (ie: HUE-123). That comes for free on JIRA but it requires a bit of programming on other systems. On Pivotal Tracker, for instance, you can use <a href="https://spin.atomicobject.com/2014/03/29/pivotal-tracker-ids">webhooks</a><br /> <a href="https://cdn.gethue.com/uploads/2016/05/Screenshot-2016-05-04-13.19.36.jpg"><img src="https://cdn.gethue.com/uploads/2016/05/Screenshot-2016-05-04-13.19.36-1024x686.jpg"  /></a>
  </li>
  <li>
    When a developer picks or gets assigned to a change, on her development environment she creates a branch specifically for that change. Our naming convention is DATE-SHORTID, so in the case of the previous example it would be <code>git checkout -b 20160425-HUE123</code><br /> There are some tools that with a keystroke combination can expand text to the current formatted date (ie: Typinator on Mac)<br /> <a href="https://cdn.gethue.com/uploads/2016/05/Screenshot-2016-05-04-13.22.14.jpg"><img src="https://cdn.gethue.com/uploads/2016/05/Screenshot-2016-05-04-13.22.14-1024x313.jpg"  /></a>
  </li>
  <li>
    After the developer is done with changing the code, she makes sure to have just one commit, so squashing all the others if she needed more that one commit. For instance, if you have three commits you want to squash together <code>git rebase -i HEAD~3</code>
  </li>
  <li>
    The commit message should include the same short id of the story. ie: <code>git commit -m "HUE-123 Bla bla bla"</code>. It's also a good practice to divide the code into "theoretical" modules, so if I work on the UI, let's say the "editor" module, i would do <code>git commit -m "HUE-123 [editor] Bla bla"</code>. That should be reflected as a tag or in the title of the original story too 🙂
  </li>
</ul>

<pre><code class="bash">#!/bin/bash

SUMMARY=$(curl -s https://issues.cloudera.org/rest/api/2/issue/HUE-${1} | jq -r '.fields | .summary')

git commit -m "HUE-${1} ${SUMMARY}"</code></pre>

</span>

A trick is also to use above script to automatically add the commit message. Then just do 'commit XXXX'.

<ul class="airy">
  <li>
    When committed, submit the code for review to <a href="http://review.cloudera.org/">http://review.cloudera.org/</a>. There are many tools for that, but we use <a href="https://www.reviewboard.org/" target="_blank" rel="noopener noreferrer">Reviewboard</a>. You can install it yourself or have it as SaaS. Everything can be <a href="https://gethue.com/rbtools-example-how-do-easily-do-code-reviews-with-review-board/" target="_blank" rel="noopener noreferrer">automated from the command line</a> so there's no need to create a diff, a new review etc.
  </li>
  <li>
    Keep the target review time under 10 hours. if there's at least one 'Ship it', the code gets into master
  </li>
  <li>
    In case of 'Ship it', from the local story branch, do a <code>git rebase origin/master</code>, fix eventual rebase issues, and then <code>git push origin HEAD:master</code><br /> <a href="https://cdn.gethue.com/uploads/2016/05/Screenshot-2016-05-04-13.24.34.jpg"><img src="https://cdn.gethue.com/uploads/2016/05/Screenshot-2016-05-04-13.24.34-1024x416.jpg"  /></a>
  </li>
  <li>
    Mark the story as resolved and paste into a comment the review URL + the commit URL of Github
  </li>
  <li>
    Here is a link to the jira <a href="https://issues.cloudera.org/browse/HUE-3767">HUE-3767</a> we used in this example
  </li>
  <li>
    Keep the stories small enough to go with rapid dev/review/push cycles
  </li>
  <li>
    Have fun!<br /> <a href="https://cdn.gethue.com/uploads/2015/11/2015-10-13-17.31.41.jpg"><img src="https://cdn.gethue.com/uploads/2015/11/2015-10-13-17.31.41-1024x768.jpg"  /></a>
  </li>
</ul>

Please feel free to comment or share your own development process!

&nbsp;

pps: for lightweight issues, Github [pull requests][1] are also welcomed!

 [1]: https://github.com/cloudera/hue/pulls
