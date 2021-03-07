---
title: HUE security improvements
author: admin
type: post
date: 2016-09-22T05:09:58+00:00
url: /hue-security-improvements/
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
sf_author_info:
  - 1
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
categories:

---
Hello HUE admin,

Recently we have added many security options in HUE. These are turned on by default when possible.

This document describes some of the fixes and enables Hue administrators to enforce and manage secure HUE installation. Whenever a browser requests a page from a HUE web server, HUE responds with the content along with HTTP Response Headers. Some of these headers contain content meta data such as the content-encoding, cache-control, status error codes, etc. Along with these are also HTTP security headers that tell your browser how to behave when handling HUE's content. For example, by using the strict-transport-security you can force the browser to communicate solely over HTTPS.

### Content-Security-Policy: header

The new Content-Security-Policy HTTP response header helps you reduce XSS risks on modern browsers by declaring what dynamic resources are allowed to load via a HTTP Header. (Read more here: <https://content-security-policy.com/>)

<pre><code class="bash">

[desktop]

secure_content_security_policy="script-src 'self' 'unsafe-inline' 'unsafe-eval' \*.google-analytics.com \*.doubleclick.net \*.mathjax.org data:;img-src 'self' \*.google-analytics.com \*.doubleclick.net http://\*.tile.osm.org \*.tile.osm.org \*.gstatic.com data:;style-src 'self' 'unsafe-inline';connect-src 'self';child-src 'self' data:;object-src 'none'"

#In HUE 3.11 and higher it is enabled by default.

</code></pre>

If you want to turn off content-security-policy header then use following value. <span style="color: #ff0000;">(Beware use it on your own risk)</span>

<pre><code class="bash">

[desktop]

secure_content_security_policy=""

#(Beware use it on your own risk)

</code></pre>

If you want to disable declaring what dynamic resources are allowed to load via a HTTP Header then you can use following value. <span style="color: #ff0000;">(Use it on your own risk)</span>

<pre><code class="bash">

[desktop]

secure_content_security_policy="default-src 'self' 'unsafe-eval' 'unsafe-inline' data: *;"

#(Use it on your own risk)

</code></pre>

[<img src="https://cdn.gethue.com/uploads/2016/09/block-content-1024x400.png" />

][1] Example of image content blocked

### Server: header

HUE now minimizes disclosure of web server information to minimize insight about web server it's version or other details. No change is needed from end user. Produces following HTTP response header :

<pre><code class="bash">

Server:apache

</code></pre>

### These HTTP response headers are generated after above security fixes.

<pre><code class="bash">

x-content-type-options:nosniff

X-Frame-Options:SAMEORIGIN

x-xss-protection:1; mode=block

Content-Security-Policy:script-src 'self' 'unsafe-inline' 'unsafe-eval' \*.google-analytics.com \*.doubleclick.net \*.mathjax.org data:;img-src 'self' \*.google-analytics.com \*.doubleclick.net http://\*.tile.osm.org *.tile.osm.org data:;style-src 'self' 'unsafe-inline';connect-src 'self';child-src 'self' data:;object-src 'none'

Strict-Transport-Security:max-age=31536000; includeSubDomains

Server:apache

</code></pre>

### X-Content-Type-Options: header

Some browsers will try to guess the content types of the assets that they fetch, overriding the Content-Type header. To prevent the browser from guessing the content type, and force it to always use the type provided in the Content-Type header, you can pass the X-Content-Type-Options: nosniff header.

<pre><code class="bash">

[desktop]

secure_content_type_nosniff=true

#In HUE 3.11 and higher it is enabled by default.

</code></pre>

### X-XSS-Protection: header

Some browsers have ability to block content that appears to be an XSS attack. They work by looking for Javascript content in the GET or POST parameters of a page. To enable the XSS filter in the browser, and force it to always block suspected XSS attacks, you can pass the X-XSS-Protection: 1; mode=block header.

<pre><code class="bash">

[desktop]

secure_browser_xss_filter=true

#In HUE 3.11 and higher it is enabled by default.

</code></pre>

[

][2] [<img src="https://cdn.gethue.com/uploads/2016/09/security-response-header.png" />][2]

<p style="text-align: center;">
  Example of the new headers received with above options
</p>

### Strict-Transport-Security: header

If your HUE site offers both HTTP and HTTPS connections, most users will end up with an unsecured connection by default. For best security, you should redirect all HTTP connections to HTTPS. For sites that should only be accessed over HTTPS, you can instruct newer browsers to refuse to connect to your domain name via an insecure connection (for a given period of time) by setting the “Strict-Transport-Security” header. This reduces your exposure to some SSL-stripping man-in-the-middle (MITM) attacks. _In HUE it is now enabled by default to switch to https if https is enabled._

### Delivers csrftoken and session cookies with secure bit set

HUE now delivers csrftoken and session cookies with secure bit set if possible. When a secure flag is used the cookie will only be sent over HTTPS.

[<img src="https://cdn.gethue.com/uploads/2016/09/cookie-secured.png" />][3]

Session cookie with secure bit while csrftoken is not

### Supports Wildcard certificates

Hue now supports [Wildcard certificates][4]. It adds the missing functionality of validating wildcard certificates and certificates with SANs (subjectAlternativeName).

A single wildcard certificate for _*.example.com_, will secure all these domains:

  * payment.example.com
  * contact.example.com
  * login-secure.example.com
  * www.example.com

Instead of getting separate certificates for sub domains, you can use a single certificate for all main domains and sub domains and save your money.

Because the wildcard only covers one level of subdomains (the asterisk doesn't match full stops), these domains would not be valid for the certificate:

  * test.login.example.com

### Fixed Arbitrary host header acceptance

Fixed Arbitrary host header acceptance in Hue. Now one can set host/domain names that the Hue server can serve.

allowed_hosts="host.domain,host2.domain,host3.domain"

<pre><code class="bash">

[desktop]

allowed_hosts="*.domain"

\# your own fqdn example: allowed_hosts="*.hadoop.cloudera.com"

\# or specific example: allowed_hosts="hue1.hadoop.cloudera.com,hue2.hadoop.cloudera.com"

</code></pre>

### Fixed Denial-of-service possibility by filling session store

Django CVE-2015-5143 <a class="external-link" title="Follow link" href="http://www.cvedetails.com/cve/CVE-2015-5143/" rel="nofollow">http://www.cvedetails.com/cve/CVE-2015-5143/</a>

### Fixed The utils.html.strip_tags function in Django can cause a denial of service

Django CVE-2015-2316 <a class="external-link" title="Follow link" href="http://www.cvedetails.com/cve/CVE-2015-2316/" rel="nofollow">http://www.cvedetails.com/cve/CVE-2015-2316/</a>

###

 [1]: https://cdn.gethue.com/uploads/2016/09/block-content.png
 [2]: https://cdn.gethue.com/uploads/2016/09/security-response-header.png
 [3]: https://cdn.gethue.com/uploads/2016/09/cookie-secured.png
 [4]: https://en.wikipedia.org/wiki/Wildcard_certificate
