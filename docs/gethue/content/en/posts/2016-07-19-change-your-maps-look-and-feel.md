---
title: Change your maps look and feel
author: admin
type: post
date: 2016-07-19T14:22:05+00:00
url: /change-your-maps-look-and-feel/
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

---
Did you know that you can change the look and feel of your Hue maps just by specifying two extra variables on the <a href="https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L114" target="_blank" rel="noopener noreferrer">Hue configuration</a>?

[<img src="https://cdn.gethue.com/uploads/2016/07/Screenshot-2016-07-18-21.15.19-1024x590.jpg"  />][1]

Here above the default style of Hue's maps; we use the open source library <a href="http://leafletjs.com/" target="_blank" rel="noopener noreferrer">Leaflet</a> to draw them.

They also did a great job putting together a list of map providers that can be used in Hue as well: <a href="https://leaflet-extras.github.io/leaflet-providers/preview/" target="_blank" rel="noopener noreferrer">https://leaflet-extras.github.io/leaflet-providers/preview/</a>.

[<img src="https://cdn.gethue.com/uploads/2016/07/Screenshot-2016-07-18-21.23.35-1024x660.jpg"  />][2]

Let's display the Esri.WorldImagery in Hue!

The properties we need to tweak are `leaflet_tile_layer` and `leaflet_tile_layer_attribution`, that can be configured in the hue.ini file:

<pre><code class="bash">

[desktop]

leaflet_tile_layer=https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}

leaflet_tile_layer_attribution='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'

</code></pre>

The values are exactly the same taken from the Leaflet providers demo.

With the recent security improvements in Hue, we need to whitelist the tile domain `server.arcgisonline.com` as well like and put it instead of `*.tile.osm.org`

<pre><code class="bash">

[desktop]

secure_content_security_policy="script-src 'self' 'unsafe-inline' 'unsafe-eval' \*.google-analytics.com \*.doubleclick.net \*.mathjax.org data:;img-src 'self' \*.google-analytics.com *.doubleclick.net server.arcgisonline.com data:;style-src 'self' 'unsafe-inline';connect-src 'self';child-src 'none';object-src 'none'"

</code></pre>

Et voila, when we restart Hue, we'll have the world imagery in every app that uses maps!

[<img src="https://cdn.gethue.com/uploads/2016/07/Screenshot-2016-07-18-21.26.53-1024x575.jpg"  />][3]

If you have any questions, feel free to comment here or on the [hue-user][4] list or [@gethue][5]

 [1]: https://cdn.gethue.com/uploads/2016/07/Screenshot-2016-07-18-21.15.19.jpg
 [2]: https://cdn.gethue.com/uploads/2016/07/Screenshot-2016-07-18-21.23.35.jpg
 [3]: https://cdn.gethue.com/uploads/2016/07/Screenshot-2016-07-18-21.26.53.jpg
 [4]: http://groups.google.com/a/cloudera.org/group/hue-user
 [5]: https://twitter.com/gethue
