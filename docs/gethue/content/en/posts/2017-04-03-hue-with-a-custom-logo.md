---
title: Hue with a custom logo!
author: admin
type: post
date: 2017-04-03T14:37:49+00:00
url: /hue-with-a-custom-logo/
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
We have seen in this [previous blog post][1] that there's a way to customize the top banner in Hue. In Hue 3.12 there's also the possibility to change the logo for further personalization!

[<img src="https://cdn.gethue.com/uploads/2016/12/Screenshot-2016-12-28-11.35.57-1024x610.png" />][2]

That's a perfect setting to show your company logo up there. Depending on if you are using <a href="https://gethue.com/hadoop-tutorial-how-to-create-a-real-hadoop-cluster-in-10-minutes/" target="_blank" rel="noopener noreferrer">Cloudera Manager</a> or not, you should either add a safety valve or edit a .ini file to use this feature. For details on how to change the configuration, <a href="https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/" target="_blank" rel="noopener noreferrer">read here</a>. In the desktop/custom section of the ini file you can find the logo_svg property:

<pre><code class="bash">[desktop]

[[custom]]

\# SVG code to replace the default Hue logo in the top bar and sign in screen

\# e.g. <image xlink:href="/static/desktop/art/hue-logo-mini-white.png" x="0" y="0" height="40" width="160" />

\## logo_svg=

</code></pre>

You can go crazy and write there any SVG code you want. Please keep in mind your SVG should be designed to fit in a 160x40 pixels space. To have the same 'hearts logo' you can see above, you can type this code

<pre><code class="bash">[desktop]

[[custom]]

logo_svg='<g><path stroke="null" id="svg_1" d="m44.41215,11.43463c-4.05017,-10.71473 -17.19753,-5.90773 -18.41353,-0.5567c-1.672,-5.70253 -14.497,-9.95663 -18.411,0.5643c-4.35797,11.71793 16.891,22.23443 18.41163,23.95773c1.5181,-1.36927 22.7696,-12.43803 18.4129,-23.96533z" fill="#ffffff"/> <path stroke="null" id="svg_2" d="m98.41246,10.43463c-4.05016,-10.71473 -17.19753,-5.90773 -18.41353,-0.5567c-1.672,-5.70253 -14.497,-9.95663 -18.411,0.5643c-4.35796,11.71793 16.891,22.23443 18.41164,23.95773c1.5181,-1.36927 22.76959,-12.43803 18.41289,-23.96533z" fill="#FF5A79"/> <path stroke="null" id="svg_3" d="m154.41215,11.43463c-4.05016,-10.71473 -17.19753,-5.90773 -18.41353,-0.5567c-1.672,-5.70253 -14.497,-9.95663 -18.411,0.5643c-4.35796,11.71793 16.891,22.23443 18.41164,23.95773c1.5181,-1.36927 22.76959,-12.43803 18.41289,-23.96533z" fill="#ffffff"/> </g>'

</code></pre>

There are some online tools that can help you with designing/importing the logo. For instance, <a href="http://editor.method.ac/" target="_blank" rel="noopener noreferrer">http://editor.method.ac/</a> allows you to get the SVG code right away

[<img src="https://cdn.gethue.com/uploads/2016/12/Screenshot-2016-12-28-11.43.37-1024x570.png" />][3]

Please bear in mind you should write all the SVG on one line, so you can use <a href="http://www.textfixer.com/tools/remove-line-breaks.php" target="_blank" rel="noopener noreferrer">this tool</a> to remove line breaks.

Now go and customize your Hue! As usual feel free to comment on the [hue-user][4] list or [@gethue][5]!

 [1]: https://gethue.com/add-a-top-banner-to-hue/
 [2]: https://cdn.gethue.com/uploads/2016/12/Screenshot-2016-12-28-11.35.57.png
 [3]: https://cdn.gethue.com/uploads/2016/12/Screenshot-2016-12-28-11.43.37.png
 [4]: http://groups.google.com/a/cloudera.org/group/hue-user
 [5]: https://twitter.com/gethue
