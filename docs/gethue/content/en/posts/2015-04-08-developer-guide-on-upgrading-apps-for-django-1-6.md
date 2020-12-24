---
title: Developer Guide on Upgrading Apps for Hue 3.8
author: admin
type: post
date: 2015-04-08T16:38:21+00:00
url: /developer-guide-on-upgrading-apps-for-django-1-6/
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
sf_detail_image:
  - 2346
categories:
  - Development

---
The upcoming Hue 3.8 internals have gone through some major upgrades to improve performance, robustness, and security. The major change stems from upgrading [Django][1] from 1.4.5 to 1.6.10, which comes with a significant amount performance enhancements, bug fixes, and the removal of deprecated features.

This post details how Hue developers that are building against the Hue SDK can upgrade their applications to work with Hue 3.8.

[<img class="aligncenter  wp-image-2346" src="https://cdn.gethue.com/uploads/2015/03/django-logo-positive-1024x357.png" />][2]

# Python version

Python 2.6.5 is now the minimum version, 2.6.0 is [not enough anymore][3].

# Django Upgrade

Hue was upgraded from Django 1.4.5 to Django 1.6.10. While the Django release notes for [1.5][4] and [1.6][5] go into extensive detail on how to upgrade, here are the main issues we encountered while upgrading Hue.

### Json

We backported Django 1.7’s [JsonResponse][6] to simplify responding with Json records. So views that used to be written as:

<pre><code class="python">def view(request):

value = { “x”: “y” }

HttpResponse(json.dumps(value))

</code></pre>

Can now be written as:

<pre><code class="python">def view(request):

value = { “x”: “y” }

return JsonResponse(value)

</code></pre>

One thing to note though is that Django now by default will raise an error if a non-dictionary is serialized. This is to prevent against [attack against older browsers][7]. Here is how to disable this error:

<pre><code class="python">def view(request):

value = [“x”, “y”]

return JsonResponse(value, safe=False)

</code></pre>

We recommend that developers migrate over to returning objects. Hue itself should be completely transitioned by 3.8.0.

### Urls and Reverse

Django’s `django.core.urlresolvers.reverse` (and therefore the `url` function in mako scripts) now automatically escapes arguments. So so uses of these functions should be changed from:

<pre><code class="python"><a href="${ url('useradmin:useradmin.views.edit_user', username=urllib.quote(user.username)) }">...</a>

</code></pre>

To:

<pre><code class="python"><a href="${ url('useradmin:useradmin.views.edit_user', username=user.username) }">...</a>

</code></pre>

### StreamingHttpResponse

In order to return a generator from a view, it is now required to use `StreamingHttpResponse`. When testing, change code from

<pre><code class="python"> csv_response = self.c.post(reverse('search:download'), {

'csv': True,

'collection': json.dumps(self._get_collection_param(self.collection)),

'query': json.dumps(QUERY)

})

csv_response_content = csv_response.content

</code></pre>

To:

<pre><code class="python">csv_response = self.c.post(reverse('search:download'), {

'csv': True,

'collection': json.dumps(self._get_collection_param(self.collection)),

'query': json.dumps(QUERY)

})

csv_response_content = ".join(csv_response.streaming_content)

</code></pre>

&nbsp;

# Static Files

As described in [NGINX-post][8], Hue now can serve serves static files with a separate webserver like NGINX. This can substantially cut down the number of requests that the Hue frontend needs to perform in order to render a page:

<table>
  <tr>
    <td>
      <a href="https://cdn.gethue.com/uploads/2015/03/without-nginx.png"><img class="aligncenter wp-image-2337" src="https://cdn.gethue.com/uploads/2015/03/without-nginx.png" /></a>
    </td>

    <td>
      <a href="https://cdn.gethue.com/uploads/2015/03/with-nginx.png"><img class="aligncenter wp-image-2338" src="https://cdn.gethue.com/uploads/2015/03/with-nginx.png" /></a>
    </td>
  </tr>
</table>

This change will break applications using the old way of serving static files. It will also cause conflicts to any user back porting patches that touch static files from Hue 3.8.0 and above to older versions of Hue.

In order to make the transition, do:

  * Move static files from <code>/apps/$name/static</code> to <code>/apps/$name/src/$name/static</code>
  * Update <code>.mako</code> files to change from:
    <pre><code class="python"><link rel=”stylesheet” href=”/metastore/static/css/metastore.css”></code></pre>

    To:

    <pre><code class="python"><link rel=”stylesheet” href=”${ static(‘metastore/css/metastore.css’) }”></code></pre>

  * Update the “ICON” in apps/$name/src/help/settings.py from:
    <pre><code class="python">ICON = “/help/static/art/icon_help_24.png”

    </code></pre>

    To:

    <pre><code class="python">ICON = “help/art/icon_help_24.png”

    </code></pre>

  * Update any Python python templates from:
    <pre><code class="python">def view(request):

    data = {‘image’: “/help/static/art/icon_help_24.png”}

    return render(“template.mako”, request, data)

    </code></pre>

    To:

    <pre><code class="python">from django.contrib.staticfiles.storage import staticfiles_storage

    …

    def view(request):

    data = {‘image’: staticfiles_storage.url(“/help/static/art/icon_help_24.png”) }

    return render(“template.mako”, request, data)

    </code></pre>

Finally, in order to run Hue with `debug=False`, it is now required to first run either `make apps` or `./build/env/bin/hue collectstatic` in order to gather all the files into the `build/static` directory. This is not necessary for `debug=True`, where hue will serve the static files directly from the `/apps/$name/src/$name/static` directory.

&nbsp;

# Next!

[Django 1.8][9] was released this month! This is the second LTS release and 1.4 support will drop in 6 months. The major dependencies of 1.8 is that it would require Python 2.7, which is not the default Python version on older LTS OS still used nowadays.

&nbsp;

As usual feel free to comment on the [hue-user][10] list or [@gethue][11]!

 [1]: https://www.djangoproject.com/
 [2]: https://cdn.gethue.com/uploads/2015/03/django-logo-positive.png
 [3]: http://stackoverflow.com/questions/19365230/django-init-keywords-must-be-strings-error-while-running-runserver
 [4]: "https://docs.djangoproject.com/en/1.7/releases/1.5/
 [5]: https://docs.djangoproject.com/en/1.7/releases/1.6/
 [6]: "https://docs.djangoproject.com/en/1.7/ref/request-response/#jsonresponse-objects
 [7]: https://docs.djangoproject.com/en/1.7/ref/request-response/#serializing-non-dictionary-objects
 [8]: #
 [9]: https://docs.djangoproject.com/en/1.8/releases/1.8/
 [10]: http://groups.google.com/a/cloudera.org/group/hue-user
 [11]: https://twitter.com/gethue
