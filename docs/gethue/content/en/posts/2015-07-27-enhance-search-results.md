---
title: Enhance your Search HTML results with Mustache!
author: admin
type: post
date: 2015-07-27T14:02:49+00:00
url: /enhance-search-results/
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
The Search app in Hue is getting [better and better][1]!

On the next Hue release (or already on [Github's master][2]) you will be able to add additional functions to Hue's version of [Mustache][3] so you call functions directly in the HTML display.

Let's see how to use it!

In our example we add a dashboard using the Yelp Demo data with an HTML result widget, like this

[<img src="https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-27-15.29.47-1024x684.png"  />][4]

We want to create a couple of functions to make our results prettier: a graphical star rating and a [static Google Map][5] of the restaurant per each review that we have.

On the CSS/JS tab we can specify something the new Mustache functions 'hue_fn_renderStars' and 'hue_fn_renderMap':

<pre><code class="html">

<script>

viewModel.additionalMustache = function (item) {

if (Mustache == "undefined") {

return;

}

item.hue_fn_renderStars = function () {

return function (val) {

var stars = parseInt(Mustache.render(val, item));

var html = ";

for (var i=0;i<stars;i++){

html += '<i class="fa fa-star"></i>';

}

return html;

}

};

item.hue_fn_renderMap = function () {

return function (val) {

var coords = Mustache.render(val, item);

return '<img src="https://maps.googleapis.com/maps/api/staticmap?center=' + coords + '&zoom=14&size=300x300&markers=color:red%7C' + coords + '">';

}

};

}

</script>

</code></pre>

it's very important to prefix the name of the additional Mustache functions with 'hue_fn_' so Hue can pick them up and process them.

On the HTML tab we write this:

<pre><code class="html">

<div class="row-fluid">

<div class="row-fluid">

<div class="span10">

<h4>{{name}} {{#renderStars}}{{stars}}{{/renderStars}}</h4>

<span class="muted">{{text}}</span>

</div>

<div class="span2">{{#renderMap}}{{latitude}},{{longitude}}{{/renderMap}}<br/>{{full_address}}</div>

</div>

<br>

</div>

</code></pre>

As you can see, the newly added functions can be called with {{#renderStars}}{{/renderStars}} and {{#renderMap}}{{/renderMap}}

And just with these few lines of code the display of our results got much better!

[<img src="https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-27-15.51.21-1024x684.png"  />][6]

To access the string that is in between the function declaration in the HTML template you should refer to **Mustache.render(val, item)**.

For instance, if you want to do a conditional function like 'if' and test for a variable inside it, you can do something like

<pre><code class="html">

<script>

viewModel.additionalMustache = function (item) {

if (Mustache == "undefined") {

return;

}

item.hue_fn_if = function () {

return function (val) {

var isTrue = $.trim(Mustache.render(val, item)) == 'true';

return isTrue ? "The condition is true!" : "No, it's false";

}

};

}

</script>

</code></pre>

and use it in the HTML tab with

<pre><code class="html">

{{#if}}{{field_to_test}}{{/if}}

</code></pre>

With the HTML result widget the sky is the limit! 🙂

As usual feel free to comment on the [hue-user][7] list or [@gethue][8]!

 [1]: https://gethue.com/build-a-real-time-analytic-dashboard-with-solr-search-and-spark-streaming/
 [2]: https://github.com/cloudera/hue
 [3]: https://github.com/janl/mustache.js/
 [4]: https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-27-15.29.47.png
 [5]: https://developers.google.com/maps/documentation/staticmaps/intro
 [6]: https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-27-15.51.21.png
 [7]: http://groups.google.com/a/cloudera.org/group/hue-user
 [8]: https://twitter.com/gethue
