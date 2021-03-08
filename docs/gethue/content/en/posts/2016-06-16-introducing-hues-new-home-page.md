---
title: Introducing Hue’s New Home Page
author: admin
type: post
date: 2016-06-16T17:54:03+00:00
url: /introducing-hues-new-home-page/
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
tags:
  - documents
  - home
  - Hue 3.10

---
With the latest release of [Hue 3.10][1] we've made some major improvements to the Home Page for Hue users.

<figure><a href="https://cdn.gethue.com/uploads/2016/06/Screenshot-2016-06-15-17.52.052-300x169.png"><img class="wp-image-4145" src="https://cdn.gethue.com/uploads/2016/06/Screenshot-2016-06-15-17.52.052-300x169.png" /></a><figcaption>Old Home Page</figcaption></figure>

<figure><a href="https://cdn.gethue.com/uploads/2016/06/Screenshot-2016-06-15-17.51.20-300x166.png"><img src="https://cdn.gethue.com/uploads/2016/06/Screenshot-2016-06-15-17.51.20-300x166.png" /></a><figcaption>New Home Page</figcaption></figure>

<h2 style="text-align: left;">
  Directory and File-based Document Management
</h2>

The first major improvement you'll notice is that all your Hue documents can now be managed via an intuitive directory and file-based interface.  Rather than utilizing the tag-based system from older versions of Hue, users can create their own directories and subdirectories and drag and drop documents within the simple filebrowser interface:

[<img src="https://cdn.gethue.com/uploads/2016/06/create_directory.gif" />][4]

Any previously existing Hue documents should be migrated over, and any previously tagged documents will be located within a subdirectory with the tag name.  Additionally, if any Hue examples have been installed then they can be accessed via a shared "examples" directory within the user's home directory.  Users can click on any of these documents to open them in their respective editor or app.

[<img src="https://cdn.gethue.com/uploads/2016/06/open_example.gif" />][5]

Additionally, users can create a new document from within any directory and once saved, it will be saved at the given path.

[<img src="https://cdn.gethue.com/uploads/2016/06/save_document.gif" />][6]

## New Home Page Features

### Contextual Menu and Bulk Actions

In addition to the action icons provided in the top-right menu, users can right-click on any directory or document to open a contextual menu to open, download, delete, or share a document/directory.

You can also select multiple documents by holding the Ctrl or Cmd key and clicking on the desired documents to perform bulk actions, such as dragging several documents into a folder or into the Trash.

[<img src="https://cdn.gethue.com/uploads/2016/06/Screenshot-2016-06-15-18.03.10-1024x345.png" />][7]

Note that sending items to the Trash will only send those items to the user's Trash folder.  To permanently delete documents, you can choose to purge them from the Trash folder.

### Import and Export Documents

Users can import and export documents or directories directly from the Home Page.  To export documents to a JSON file, select the document(s) that you wish to export, and either click "Download" from the contextual menu or from the icon menu.  Downloading a directory will also download the entire contents of the directory.

[<img src="https://cdn.gethue.com/uploads/2016/06/Screenshot-2016-06-15-18.04.072-1024x430.png" />][8]

To import a JSON file as documents, click the "Upload" icon button which will bring up a modal to select the JSON file to import.  Hue will attempt to retain any directory structure in the imported file, but if it fails to find the parent directory or if the current user is importing a different user's documents, then those documents will be imported into the current user's home directory.

[<img src="https://cdn.gethue.com/uploads/2016/06/import_documents.gif" />][9]

### Sharing folders and files

Users can easily access any shared documents from the Home Page document browser, as well as share their owned folders and documents with other Hue users.  An intuitive icon is displayed on any shared directories or documents to indicate that they are shared with the current user or shared with others.

Users can easily share a folder or document with other users or groups by selecting the desired item(s) and selecting "Share" in the contextual menu or in the top right icon menu.

[<img src="https://cdn.gethue.com/uploads/2016/06/Screenshot-2016-06-15-18.09.412-1024x407.png" />][10][<img src="https://cdn.gethue.com/uploads/2016/06/Screenshot-2016-06-15-18.15.282-1024x350.png" />][11]

### Searching

Quick searching for documents is also easy on the Home Page.  Simply click on the search icon from the top right menu and enter any relevant search terms; the search will return any matching documents accessible to the user, regardless of the current path level you're on.

[<img src="https://cdn.gethue.com/uploads/2016/06/search_documents.gif" />][12]

We think you'll love the new look and interface of Hue's home page.  If you have any questions, feel free to comment here or on the [hue-user][13] list or [@gethue][14]!

 [1]: https://gethue.com/hue-3-10-with-its-new-sql-editor-is-out/
 [2]: https://cdn.gethue.com/uploads/2016/06/Screenshot-2016-06-15-17.52.052.png
 [3]: https://cdn.gethue.com/uploads/2016/06/Screenshot-2016-06-15-17.51.20.png
 [4]: https://cdn.gethue.com/uploads/2016/06/create_directory.gif
 [5]: https://cdn.gethue.com/uploads/2016/06/open_example.gif
 [6]: https://cdn.gethue.com/uploads/2016/06/save_document.gif
 [7]: https://cdn.gethue.com/uploads/2016/06/Screenshot-2016-06-15-18.03.10.png
 [8]: https://cdn.gethue.com/uploads/2016/06/Screenshot-2016-06-15-18.04.072.png
 [9]: https://cdn.gethue.com/uploads/2016/06/import_documents.gif
 [10]: https://cdn.gethue.com/uploads/2016/06/Screenshot-2016-06-15-18.09.412.png
 [11]: https://cdn.gethue.com/uploads/2016/06/Screenshot-2016-06-15-18.15.282.png
 [12]: https://cdn.gethue.com/uploads/2016/06/search_documents.gif
 [13]: http://groups.google.com/a/cloudera.org/group/hue-user
 [14]: https://twitter.com/gethue
