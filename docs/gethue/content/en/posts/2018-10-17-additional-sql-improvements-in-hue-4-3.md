---
title: 'Additional SQL improvements: Built-in Impala language reference, Improved column samples, Dark Mode'
author: admin
type: post
date: 2018-10-17T14:57:54+00:00
url: /additional-sql-improvements-in-hue-4-3/
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

---
Hi SQL enthusiasts!

We've made quite some improvements to the SQL experience in [Hue 4.3][1], in a previous [post][2] we showed some of the new exploration improvements and now we'd like to show some additional new features in the editor.

After the introduction of the UDF reference panel we've received requests to also include documentation for SQL syntax. It's quite common to look at the [language reference][3] while writing certain statements and it's annoying to have to have multiple windows open. So, to give you the best experience possible we decided to include the complete Impala SQL language reference in Hue!

## Built-in Impala language reference

You can find the Language Reference in the right assist panel. The right panel itself has a new look with icons on the left hand side and can be minimised by clicking the active icon.

The filter input on top will only filter on the topic titles in this initial version. Below is an example on how to find documentation about joins in select statements.

<div class="wp-caption aligncenter">
  <p>
    <img width="766" height="421" data-gifffer="https://cdn.gethue.com/uploads/2018/10/impala_lang_ref_joins.gif"  />
  </p>

  <p class="wp-caption-text">
    The new language reference panel
  </p>
</div>

While editing a statement there's a quicker way to find the language reference for the current statement type, just right-click the first word and the reference appears in a popover below.

[<img src="https://cdn.gethue.com/uploads/2018/10/impala_lang_ref_context.png"/>][4]

## Improved column samples

It's quite handy to be able to look at column samples while writing a query to see what type of values you can expect. Hue now has the ability to perform some operations on the sample data, you can now view distinct values as well as min and max values. Expect to see more operations in coming releases.

<div class="wp-caption aligncenter">
  <p>
    <img width="766" height="523" data-gifffer="https://cdn.gethue.com/uploads/2018/10/sample_context_operations.gif"  />
  </p>

  <p class="wp-caption-text">
    Show distinct sample values
  </p>
</div>

## Editor dark mode

We've introduced a dark mode for the editor! Initially this mode is limited to the actual editor area and we're considering extending this to cover all of Hue.

<figure><a href="https://cdn.gethue.com/uploads/2018/10/editor_dark_mode.png"><img src="https://cdn.gethue.com/uploads/2018/10/editor_dark_mode.png"/></a><figcaption>The new dark mode</figcaption></figure>

To toggle the dark mode you can either press `Ctrl-Alt-T` or `Command-Option-T` on Mac while the editor has focus. Alternatively you can control this through the settings menu which is shown by pressing `Ctrl-,` or `Command-,` on Mac.

We hope that these new improvements will help you write awesome queries. As always, if you have any questions or feedback, feel free to comment here, on the [hue-user][6] list or [@gethue][7]!

 [1]: https://gethue.com/hue-4-3-and-its-app-building-improvements-are-out/
 [2]: https://gethue.com/improved-sql-exploration-in-hue-4-3/
 [3]: https://impala.apache.org/impala-docs.html
 [4]: https://cdn.gethue.com/uploads/2018/10/impala_lang_ref_context.png
 [5]: https://cdn.gethue.com/uploads/2018/10/editor_dark_mode.png
 [6]: http://groups.google.com/a/cloudera.org/group/hue-user
 [7]: https://twitter.com/gethue
