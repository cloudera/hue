---
title: Single sign-on in Hue with Twitter and OAuth
author: admin
type: post
date: 2013-05-13T14:01:00+00:00
url: /single-sign-on-in-hue-with-twitter-and-oauth/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/50341521241/single-sign-on-in-hue-with-twitter-and-oauth
tumblr_gethue_id:
  - 50341521241
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
slide_template:
  - default
categories:
  - Development

---
<p id="docs-internal-guid-55127576-85f6-b214-bad6-7ce289139d16">
  <span>This post talks about</span><a href="https://gethue.com"><span>Hue</span></a><span>, an open source web-based interface that makes</span><a href="http://hadoop.apache.org/"><span>Apache Hadoop</span></a><span> easier to use.</span>
</p>

<span>Hue’s target is the Hadoop user experience and lets users focus on big data processing. In the previous posts we focused on some </span>[new features][1] <span>and how to quickly analyze your </span>[data][2] <span>with the Hive editor.</span>

This time, we are going to follow-up on Hue authentication mechanisms. We previously described a [list of backends][3] like LDAP, AllowAll (improved recently in the latest [2.3 release][4] with [HUE-962][5]) and this post will show how you can use your Twitter account for login-in into Hue. We are using Twitter as an example but could have picked Facebook Connect (they both use [Open Authentication][6]).

## <span>Creating a Twitter Application</span>

<span>First, we need to create a new Twitter application by going to the </span>[<span>developer platform page</span>][7]<span>. Provide some details about the application like the name and description. In order to avoid trouble later, do not forget to specify a placeholder URL in the ‘Callback URL’ field. This actually can be any URL and will prevent you from hitting a known </span>[<span>bug</span>][8] <span>later.</span>

<img alt="image" src="https://lh4.googleusercontent.com/klb8aZu27bNA_kiqiVwqki5Nmde9CCmMebny8RzfSn12abiJyBvJrJidKADkFxKFOjImxJQXdHtpCOqigN1y6r7Nn2CO2V4A0PyF_v8iVm7Wk-ibmZHbsMix" width="665px;" height="945px;" />

<span>Creating a new application</span>

<img alt="image" src="https://lh6.googleusercontent.com/qpQIsLPFY5wl7tt_ZlJzYGPMyv_ZsPKGhCsk6aWJaiZsohtdWmLE8OQmYC30szScvzfdc1QK2InweIHATnt5WzDqB6jS46NdvcjAiCAg39M-dfvpoxTG42oz" width="676px;" height="720px;" />

<span>The Twitter application page</span>

&nbsp;

## <span>Open Authentication communication</span>

<span>After creating your account, here is how Hue is going to interact with it through its new OAuth Backend (which implements Twitter </span>[<span>OAuth</span>][9] <span>version 1.0). </span>

&nbsp;

  1. <span>When the user clicks on the ‘Sign in’ button, Hue will perform its </span>[<span>first call </span>][10]<span>to Twitter for a request token. Hue sends both its key and secret and a URL callback and gets back a request token (OAuth token + secret). </span>
  2. <span>The user is then redirected to Twitter (with only the OAuth token) which will ask him to authorize Hue to use his Twitter account. After this validation, Twitter redirects the user to Hue with the call back. </span>
  3. <span>Hue sends the OAuth token and secret to Twitter and logs in the user if Twitter validated them.</span>

<img alt="image" src="https://lh4.googleusercontent.com/FnQkDxPdbI0_-NcxfUnbGGgWyZ3k0dRmxzY55qKSOBdN8R1jqoqTnWUygEd4zQvPvI7Bi5fFQgDnvz3IhX_UJRFhQk0_Iw6Rn4I87mC4QsyBtoQXxpH3PQx0" width="476px;" height="264px;" />

<span>OAuth Sign in page of Hue</span>

<img alt="image" src="https://lh3.googleusercontent.com/V4lR8X636Kk0EFM9oc6P5opTmgoGHxuMgUUhRH7MAtLBUclSUPL0Lbb6Xc4TLawdkgPIb986vDsip5vKbQCFNbQCGp4K4NDqYkNLN9MfEp1gVF0J35UFCRDG" width="632px;" height="283px;" />

<span>Authorizing Hue to use your Twitter account</span>

<img alt="image" src="https://lh6.googleusercontent.com/0YeCJYIqAbmbtnt6SXl1EZjuoo7f0u8qW93INUGlLgVu1CyUmd57Dryv9Mj9oZHk3hQV1RFPXm9cAMstnLyGf_J-_UC8YkNNuRvybPfWzh0IvFPu2WmkSsRs" width="612px;" height="345px;" />

<span>Logged-in user</span>

&nbsp;

<span>All this process is transparent to the user. You only have to click once to log in (twice if the Hue session has been terminated). Hue automatically uses your twitter username as login.</span>

&nbsp;

## <span>Do it yourself</span>

<span>Hue 2.3 ships with a new OAuthBackend (added in </span>[HUE-966][11]<span>). Hue leverages the great </span>[OAuth2 Python][12] <span>lib and the </span>[httplib2][13]<span>.</span>

<span>In order to configure Hue for this example, in hue.ini, specify the OAuth backend and the consumer key and secret which are appear on your “The Twitter application page” (cf. above section): </span>

&nbsp;

<pre class="code">[desktop]

 # Configuration options for user authentication into the web application
 # ------------------------------------------------------------------------

 [[auth]]

    backend=desktop.auth.backend.OAuthBackend

 # Configuration options for using OAuth login
 # ------------------------------------------------------------------------

 [[oauth]]

    # The Consumer key of the application
    consumer_key=XXXXXXXXXXXXXXXXXXXXX

    # The Consumer secret of the application
    consumer_secret=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX</pre>

## Conclusion

<span>Hue ships with various backends and offers a pluggable system which is easy to customize to your needs. In practice you could extend it to reuse your company login system and provide a </span>[<span>single sign-on</span>][14] <span>experience to your Hue users.</span>

<span>Moreover, the user’s OAuth token can be saved into the user profile and be used for interacting safely with the service. For example, the Twitter token could let Hue fetch the user’s tweets and followers and display them directly into Hue. If the app asked for more permissions, it would even be possible to send some tweets or direct messages.</span>

<span>Hue is seeing a continuous growth in </span>[activity][15] <span>and is on track for providing a lot of new features and fixes in 2.4. Coming posts are going to focus on some </span>[demos][16] <span>of common data analysis scenarios made easier with Hue. In the meantime, feel free to participate on the </span>[group][17]<span>!</span>

 [1]: http://blog.cloudera.com/blog/2013/03/whats-new-in-hue-2-2/
 [2]: http://blog.cloudera.com/blog/2013/03/how-to-analyze-twitter-data-with-hue/
 [3]: http://blog.cloudera.com/blog/2012/12/managing-permissions-in-hue/
 [4]: http://gethue.tumblr.com/post/49863621004/hue-2-3-0-apr-15th-2013
 [5]: https://issues.cloudera.org/browse/HUE-962
 [6]: http://oauth.net/
 [7]: https://dev.twitter.com/apps/new
 [8]: https://dev.twitter.com/discussions/392
 [9]: https://dev.twitter.com/docs/auth/oauth
 [10]: https://dev.twitter.com/docs/api/1/post/oauth/request_token
 [11]: https://issues.cloudera.org/browse/HUE-966
 [12]: https://github.com/simplegeo/python-oauth2
 [13]: http://code.google.com/p/httplib2/
 [14]: http://en.wikipedia.org/wiki/Single_sign-on
 [15]: http://www.meetup.com/San-Francisco-Bay-Area-Hue-Users/
 [16]: http://blog.cloudera.com/blog/2013/04/demo-hdfs-file-operations-made-easy-with-hue/
 [17]: https://groups.google.com/a/cloudera.org/forum/?fromgroups#%21forum/hue-user
