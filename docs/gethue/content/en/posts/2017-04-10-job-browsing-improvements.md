---
title: Job Browsing Improvements
author: admin
type: post
date: 2017-04-10T21:21:46+00:00
url: /job-browsing-improvements/
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
sf_page_title_bg:
  - none
sf_page_title_text_style:
  - light
sf_background_image_size:
  - cover
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
categories:
---

[Hue 3.12][1] comes with two significant job browsing improvements that make the navigation among thousands of jobs much simpler. Here is a demo describing the changes in detail.

{{< youtube 8yxtIt77GaY >}}

### Extended Oozie Dashboard Filtering

With this improvement, you can search for:

- Jobs with partial match on either the _Name_ or *Submitter* of the job.
- Results across all pages and not just the page you are in.
- The one single job among thousands of submitted jobs by entering the complete ID.

### Job Browser Start Time Filter

This filter allows to user the easily navigate to the older jobs, especially if the total job count is greater than 1000 (current limit). Yarn returns the oldest jobs by default and not the most recent ones. This improvement will help the user to workaround this limitation by only getting the jobs run in the last 'n' days|hours|minutes.

&nbsp;

[<img src="https://cdn.gethue.com/uploads/2017/03/new-jb-filter.png"/>][2]

###

As always, feel free to suggest new improvements or comment on the [hue-user][3] list or [@gethue][4]!

[1]: https://gethue.com/hue-3-12-the-improved-editor-for-sql-developers-and-analysts-is-out/
[2]: https://cdn.gethue.com/uploads/2017/03/new-jb-filter.png
[3]: http://groups.google.com/a/cloudera.org/group/hue-user
[4]: https://twitter.com/gethue
