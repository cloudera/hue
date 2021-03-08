---
title: Improved dashboards layouts in Hue 4.3
author: admin
type: post
date: 2018-08-17T18:43:06+00:00
url: /improved-dashboard-layout/
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

---
Aloha dashboard rockers!

In Hue 4.3 you can find a completely revamped way of building your usual [dashboards][1]. Long gone are the strict columns and rows constraints, welcome the drag and drop auto positioning! We also added several other functionalities, the most important ones being:

<h2 style="margin-top: 50px;">
  Disappearance of the 'Edit mode'
</h2>

<div class="wp-caption aligncenter" style="margin-top: 30px; margin-bottom: 30px;">
  <p>
    <img data-gifffer="https://cdn.gethue.com/uploads/2018/08/dashboard_layout_edit.gif"  />
  </p>

  <p class="wp-caption-text">
    The pencil icon is now a plus
  </p>
</div>

In the previous versions of Hue there were two well distinct modes: a display dashboard to display your data and a version where you would have clear options to add new widgets, create columns, remove charts, etc..

This distinction was adding overhead to the UX of the dashboard, so we decided to remove the friction and have a dashboard where you could always drag in new widgets, move them around and change their settings.

The pencil icon of the top toolbar changed into a plus button that toggles the widgets toolbar.

&nbsp;

<h2 style="margin-top: 50px;">
  Smarter drag and drop
</h2>

<div class="wp-caption aligncenter" style="margin-top: 30px; margin-bottom: 30px;">
  <p>
    <img data-gifffer="https://cdn.gethue.com/uploads/2018/08/dashboard_layout_dnd.gif"  />
  </p>

  <p class="wp-caption-text">
    Drag and hover to create new rows or columns
  </p>
</div>

There's no rigid column/row system anymore. Just drag a new widget on top or bottom of an existing one to add a new row, or on the sides to automatically split the available space into equal columns.

Each widget can be horizontally resized too, and the siblings will be automatically resized to fit into the same row.

&nbsp;

<h2 style="margin-top: 50px;">
  Noise reduction
</h2>

<div class="wp-caption aligncenter" style="margin-bottom: 30px;">
  <p>
    <img data-gifffer="https://cdn.gethue.com/uploads/2018/08/dashboard_layout_dimensions.gif"  />
  </p>

  <p class="wp-caption-text">
    The redesigned dimensions editor
  </p>
</div>

With the improved edit flow we also got rid of a lot of visual noise that would make your data shine less. The widget left side icons (to switch between viz and tabular data and download the widget data) appear only when you hover the widget itself, and the same goes for the dimensions editor, that has been revamped visually as well.

&nbsp;

We hope that these new improvements will help you better understand and display your data. As always, if you have any questions or feedback, feel free to comment here, on the [hue-user][2] list or [@gethue][3]!

 [1]: https://gethue.com/search-dashboards/
 [2]: http://groups.google.com/a/cloudera.org/group/hue-user
 [3]: https://twitter.com/gethue
