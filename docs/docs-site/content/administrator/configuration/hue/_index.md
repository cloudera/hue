---
title: "Hue"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 1
---

This section is about configuring the Hue server itself.
These configuration variables are under the `[desktop]` section in
the `hue.ini` configuration file.

## Specifying the HTTP port

Hue uses CherryPy web server.  You can use the following options to
change the IP address and port that the web server listens on.
The default setting is port 8888 on all configured IP addresses.

    # Webserver listens on this address and port
    http_host=0.0.0.0
    http_port=8888

[Gunicorn](https://gunicorn.org/) support is planned to come in via [HUE-8739](https://issues.cloudera.org/browse/HUE-8739).

## Specifying the Secret Key

For security, you should also specify the secret key that is used for secure
hashing in the session store. Enter a long series of random characters
(30 to 60 characters is recommended).

    secret_key=jFE93j;2[290-eiw.KEiwN2s3['d;/.q[eIW^y#e=+Iei*@Mn<qW5o

NOTE: If you don't specify a secret key, your session cookies will not be
secure. Hue will run but it will also display error messages telling you to
set the secret key.

## Disabling some apps

In the Hue ini configuration file, in the [desktop] section, you can enter the names of the app to hide:

<pre>
[desktop]
# Comma separated list of apps to not load at server startup.
app_blacklist=beeswax,impala,security,filebrowser,jobbrowser,rdbms,jobsub,pig,hbase,sqoop,zookeeper,metastore,spark,oozie,indexer
</pre>

[Read more about it here](http://gethue.com/mini-how-to-disabling-some-apps-from-showing-up/).

## Authentication

By default, the first user who logs in to Hue can choose any
username and password and becomes an administrator automatically.  This
user can create other user and administrator accounts. User information is
stored in the Django database in the Django backend.

The authentication system is pluggable. For more information, see the [SDK Documentation](../sdk/sdk.html).

List of some of the possible authentications:
### Username / Password
### LDAP
### SAML

[Read more about it](http://gethue.com/updated-saml-2-0-support/).

### OpenId Connect
### Multiple Authentication Backends

For example, to enable Hue to first attempt LDAP directory lookup before falling back to the database-backed user model, we can update the hue.ini configuration file or Hue safety valve in Cloudera Manager with a list containing first the LdapBackend followed by either the ModelBackend or custom AllowFirstUserDjangoBackend (permits first login and relies on user model for all subsequent authentication):

<pre>
[desktop]
  [[auth]]
  backend=desktop.auth.backend.LdapBackend,desktop.auth.backend.AllowFirstUserDjangoBackend
</pre>

This tells Hue to first check against the configured LDAP directory service, and if the username is not found in the directory, then attempt to authenticate the user with the Django user manager.

[Read more about it here](http://gethue.com/configuring-hue-multiple-authentication-backends-and-ldap/).


## Change your maps look and feel

The properties we need to tweak are leaflet_tile_layer and leaflet_tile_layer_attribution, that can be configured in the hue.ini file:

<pre>
[desktop]
leaflet_tile_layer=https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}
leaflet_tile_layer_attribution='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
</pre>

[Read more about it here](http://gethue.com/change-your-maps-look-and-feel/).

## Configure a Proxy

We explained how to run Hue with NGINX serving the static files or under Apache. If you use another proxy, you might need to set these options:

<pre>
  [desktop]
  # Enable X-Forwarded-Host header if the load balancer requires it.
  use_x_forwarded_host=false

  # Support for HTTPS termination at the load-balancer level with SECURE_PROXY_SSL_HEADER.
  secure_proxy_ssl_header=false
</pre>

## Configuring SSL

You can configure Hue to serve over HTTPS.

1. Configure Hue to use your private key by adding the following
options to the `hue.ini` configuration file:

    ssl_certificate=/path/to/certificate
    ssl_private_key=/path/to/key

2. Ideally, you would have an appropriate key signed by a Certificate Authority.
If you're just testing, you can create a self-signed key using the `openssl`
command that may be installed on your system:

Create a key:

    openssl genrsa 1024 > host.key

Create a self-signed certificate:

    openssl req -new -x509 -nodes -sha1 -key host.key > host.cert


<div class="note">
Self-signed Certificates and File Uploads

To upload files using the Hue File Browser over HTTPS requires
using a proper SSL Certificate.  Self-signed certificates don't
work.
</div>

Note: The security vulnerability SWEET32 is also called Birthday attacks against TLS ciphers with 64bit block size and it is assigned CVE-2016-2183. This is due to legacy block ciphers
having block size of 64 bits are vulnerable to a practical collision attack when used in CBC mode.

DES/3DES are the only ciphers has block size of 64-bit. One way to config Hue not to use them:
<pre>
  [desktop]
  ssl_cipher_list=DEFAULT:!DES:!3DES
</pre>

## SASL

When getting a bigger result set from Hive/Impala or bigger files like images from HBase, the response requires to increase
the buffer size of SASL lib for thrift sasl communication.

<pre>
  [desktop]
  # This property specifies the maximum size of the receive buffer in bytes in thrift sasl communication,
  # default value is 2097152 (2 MB), which equals to (2 * 1024 * 1024)
  sasl_max_buffer=2097152
</pre>

## User Admin Configuration
In the `[useradmin]` section of the configuration file, you can
_optionally_ specify the following:

default_user_group::
  The name of a default group that is suggested when creating a
  user manually. If the LdapBackend or PamBackend are configured
  for doing user authentication, new users will automatically be
  members of the default group.


## Banner
You can add a custom banner to the Hue Web UI by applying HTML directly to the property, banner_top_html. For example:

    banner_top_html=<H4>My company's custom Hue Web UI banner</H4>

## Splash Screen
You can customize a splash screen on the login page by applying HTML directly to the property, login_splash_html. For example:

    [desktop]
    [[custom]]
    login_splash_html=WARNING: You are required to have authorization before you proceed.


## Custom Logo

There is also the possibility to change the logo for further personalization.

    [desktop]
    [[custom]]
    # SVG code to replace the default Hue logo in the top bar and sign in screen
    # e.g. <image xlink:href="/static/desktop/art/hue-logo-mini-white.png" x="0" y="0" height="40" width="160" />
    logo_svg=

You can go crazy and write there any SVG code you want. Please keep in mind your SVG should be designed to fit in a 160×40 pixels space. To have the same ‘hearts logo' you can see above, you can type this code

    [desktop]
    [[custom]]
    logo_svg='<g><path stroke="null" id="svg_1" d="m44.41215,11.43463c-4.05017,-10.71473 -17.19753,-5.90773 -18.41353,-0.5567c-1.672,-5.70253 -14.497,-9.95663 -18.411,0.5643c-4.35797,11.71793 16.891,22.23443 18.41163,23.95773c1.5181,-1.36927 22.7696,-12.43803 18.4129,-23.96533z" fill="#ffffff"/> <path stroke="null" id="svg_2" d="m98.41246,10.43463c-4.05016,-10.71473 -17.19753,-5.90773 -18.41353,-0.5567c-1.672,-5.70253 -14.497,-9.95663 -18.411,0.5643c-4.35796,11.71793 16.891,22.23443 18.41164,23.95773c1.5181,-1.36927 22.76959,-12.43803 18.41289,-23.96533z" fill="#FF5A79"/> <path stroke="null" id="svg_3" d="m154.41215,11.43463c-4.05016,-10.71473 -17.19753,-5.90773 -18.41353,-0.5567c-1.672,-5.70253 -14.497,-9.95663 -18.411,0.5643c-4.35796,11.71793 16.891,22.23443 18.41164,23.95773c1.5181,-1.36927 22.76959,-12.43803 18.41289,-23.96533z" fill="#ffffff"/> </g>'

Read more about it in [Hue with a custom logo](http://gethue.com/hue-with-a-custom-logo/) post.


## Storing passwords in file script

This [article details how to store passwords in a script](http://gethue.com/storing-passwords-in-script-rather-than-hue-ini-files/) launched from the OS rather than have clear text passwords in the hue*.ini files.

Some passwords go in Hue ini configuration file making them easily visible to Hue admin user or by users of cluster management software. You can use the password_script feature to prevent passwords from being visible.

## Idle session timeout

Hue now offers a new property, idle_session_timeout, that can be configured in the hue.ini file:

    [desktop]
    [[auth]]
    idle_session_timeout=600

When idle_session_timeout is set, users will automatically be logged out after N (e.g. – 600) seconds of inactivity and be prompted to login again:

[Read more about it here](http://gethue.com/introducing-the-new-login-modal-and-idle-session-timeout/).

## Auditing

Read more about [Auditing User Administration Operations with Hue and Cloudera Navigator](http://gethue.com/auditing-user-administration-operations-with-hue-and-cloudera-navigator-2/).
