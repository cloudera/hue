---
title: SSO for REST APIs with your custom JWT authentication
author: Hue Team
type: post
date: 2021-09-14T00:00:00+00:00
url: /blog/2021-09-14-sso-for-rest-apis-with-your-custom-jwt-authentication
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
  - Version 4.11
  - Development

---
<p align="center"> Leveraging Hue as an API Service </p>

The Hue SQL Editor allows you to query any Database or Data Warehouse. Initially Hue had private APIs which could be used by the Hue UI only (because they could've changed, auth cookie based, lot of historical parameters etc). 

For example, if anyone had set up their own Hue instance, then it was very difficult for any other external services to use the APIs which Hue provides.

## Rest API

With the [introduction of Public APIs](https://docs.gethue.com/developer/api/rest/), any external service can see Hue as an API server and use all the end user functionalities under the hood via [JWT Authentication](https://docs.gethue.com/developer/api/rest/#authentication).

For authentication, we use [djangorestframework-simplejwt](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/) to generate a Hue JWT which can be passed as a Bearer token to access the APIs. This is what powers the Hue web components such as [SQL Scratchpad](https://docs.gethue.com/developer/components/scratchpad/)!

## Custom Authentication

But now let's think of a scenario where an external service or application wants to generate and use their own JWT for authentication? Maybe for easier injection of  [Scratchpad component](https://docs.gethue.com/developer/components/scratchpad/) into a separate web app? Or the external service wanting to generate their own JWT with their own specifications?

To resolve this issue, we implemented an option of custom JWT authentication (thanks to [Django REST Framework](https://www.django-rest-framework.org/api-guide/authentication/#custom-authentication) custom pluggability)!

Basically if it's enabled, then Hue will accept your JWT in the request headers and let you access the public APIs, provided the signature is valid ;)

![Custom JWT Architecture Diagram](https://cdn.gethue.com/uploads/2021/09/custom_jwt_authentication.png)

- Your web service sends the JWT as bearer token in request headers of the API called.
- Custom auth in Hue first fetches the public key from the auth server and then using it, decodes the JWT to extract the user information.
- To access external services like Impala etc. via Hue, the JWT is further passed on to Impala for it to decode and let your external web service access Impala via Hue seamlessly.

To enable the auth backend, make the following changes in the `hue.ini`:

    [desktop]
    [[auth]]
    [[[jwt]]]
    is_enabled=true
    key_server_url=https://ext_authz:8000
    issuer=<your_external_app>
    audience=hue

Also, if you want to allow Hue to send JWT to external services like Impala etc., enable the following flag in `hue.ini`:

    [desktop]
    use_thrift_http_jwt=true

By default, this auth backend only supports the **RSA256 algorithm** for the JWT signature verification.

But nothing is set in stone! and if you wish to have your own implementation of the custom auth (having customized connection with external auth server or using different signing algorithm etc.), then you can follow the [Django REST Framework](https://www.django-rest-framework.org/api-guide/authentication/#custom-authentication) custom pluggability and add like this [dummy auth](https://github.com/cloudera/hue/blob/d75c8fc7b307fc67ef9a2a58e36cfb4ace6cd461/desktop/core/src/desktop/auth/api_authentications.py#L119).

And then, add it in `hue.ini` (comma separated and in order of priority if multiple auth backends present):

    [desktop]
    [[auth]]
    api_auth=<you_own_custom_auth_backend>

With this flexibility of sending your own JWT to access Hue REST APIs, there is no need to rebuild a client/server for submitting queries,  uploading S3 files, collecting more SQL metadata etc. and you get more APIs for free down the road ;)

</br>
</br>

Any [feedback](https://github.com/cloudera/hue/issues) or question is highly welcomed! Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!

Onwards!

Harsh from the Hue Team
