---
title: How to fix the MultipleObjectsReturned error in Hue
author: admin
type: post
date: 2014-03-14T17:47:00+00:00
url: /how-to-fix-the-multipleobjectsreturned-error-in-hue/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/79568564935/how-to-fix-the-multipleobjectsreturned-error-in-hue
tumblr_gethue_id:
  - 79568564935
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
  - Sidebar-2
sf_caption_position:
  - caption-right
slide_template:
  - default
sf_page_title_image:
  - 222
categories:
  - Development

---
When going on the Home page (/home) in Hue 3.0, this error could appear:

    MultipleObjectsReturned: get() returned more than one DocumentPermission - it returned 2! Lookup parameters were {'perms': 'read', 'doc': <Document: saved query Sample: Job loss sample>}

This is fixed in Hue 3.6 and here is a way to repair it:

1. Backup the Hue <a href="https://docs.gethue.com/administrator/administration/database/" target="_blank" rel="noopener noreferrer">database</a>.

2. Run the cleanup script:

    from desktop.models import DocumentPermission, Document

    for document in Document.objects.all():
      try:
        perm, created = DocumentPermission.objects.get_or_create(doc=document, perms=DocumentPermission.READ_PERM)
      except DocumentPermission.MultipleObjectsReturned:
        # We can delete duplicate perms of a document
        dups = DocumentPermission.objects.filter(doc=document, perms=DocumentPermission.READ_PERM)
        perm = dups[0]
        for dup in dups[1:]:
          print('Deleting duplicate %s' % dup)
          dup.delete()
