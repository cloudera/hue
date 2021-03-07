---
title: Updated SAML 2.0 Support
author: admin
type: post
date: 2014-11-22T00:56:36+00:00
url: /updated-saml-2-0-support/
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
Hue has been shipping SAML 2.0 authentication for quite some time. SAML 2.0 is an alternative to [LDAP][1] which lets you provide [single sign on][2] (SSO) in your company so that users can use the same login/password in all the systems. Unfortunately our support for SAML 2.0 was limited to a few small use cases.

In the upcoming Hue 3.8.0 / CDH 5.3.0, we now support all of the main [SAML 2.0][3] web profile features. In addition to allowing for single login, Hue now lets you perform:

  * Single-Logout
  * Signed requests and responses
  * Use an Alternative NameID

Along the way we fixed a number of bugs in Hue ([HUE-2458][4]) and contributed back [a number of fixes][5] to the awesome Python libraries [PySAML2][6] and [djangosaml2][7]. With these changes, Hue now is able to use these upstream packages instead of our old fork of these repositories. Here’s below an updated version of the SAML 2.0 guide.

Have any questions? Feel free to contact us on [hue-user][8] or [@gethue][9]!

* * *

## **The Basics**

In SAML 2.0, there are 2 basic components: the Service Provider (SP) and Identity Provider (IdP). The typical flow from SP to IdP is made obvious in following image.

&nbsp;

[<img src="https://cdn.gethue.com/uploads/2014/11/WHL7QgcaoXi8PB71tkNHeqFSin4UzdPtvJdcX6-YauDxnP3tlTzUpDXM-RkO6twS07JEH1Xka1F-OfodIjCSr2E7ueyKRxb0tL8tHq0njdh1_ecoVYDv9min.png"  />][10]

&nbsp;

SAML architecture from <http://en.wikipedia.org/wiki/SAML_2.0.>

Hue acts as a service provider with an assertion consumer service (ACS). It communicates with the IdP to authenticate users. Hue also provides a couple of URLs that enable communication with the IdP:

  * “/saml2/metadata”
  * “/saml2/acs”

The IdP will contact the metadata URL for information on the SP. For example, the ACS URL is described in metadata. The ACS URL is the consumer of assertions from the IdP. The IdP will redirect users to the ACS URL once it has authenticated them.

### **Users**

When a user logs into Hue through the SAML backend, a new user is created in Hue if it does already not exist. This logic is almost the same as the LdapBackend. It is also configurable via the create_users_on_login parameter.

## **Demo**

The following is a demo of how to setup Hue to communicate via SAML with a Shibboleth IdP.

### **Environment**

This demo is performed on CentOS 6.4 and assumes the following projects have been installed and configured:

  * [Shibboleth 2.4.0][11] – IdP
  * [OpenDS 2.2.1][12] – Authentication service
  * [Tomcat 6][13] – Server for IdP

Shibboleth IdP is installed to “/opt/shibboleth-idp” and has the following custom configurations:

  * Release the [UID][14] attribute with assertions.
  * Available over SSL on port [8443][15].
  * Provide authentication via [LDAP][16] through OpenDS.
  * Connect to a [relying party][17] that contains metadata about the SP. In this case, the relying party is Hue and its metadata URL is “/saml2/metadata”.
  * Use the [UsernamePassword][18] handler. It provides very obvious feedback that all components have been configured appropriately.
  * Available to all [IPs][19].

OpenDS was installed and 2000 users were automatically generated. Then, a user “test” was added with the password “password”.

### **Preparing Hue**

The libraries that support SAML in Hue must be installed:

<pre>build/env/bin/pip install djangosaml2</pre>

The above commands will also install:

  * Paste
  * WebOb
  * argparse
  * cffi
  * cryptography
  * decorator
  * pyOpenSSL
  * pycparser
  * pycrypto
  * pysaml2
  * python-dateutil
  * python-memcached
  * pytz
  * repoze.who
  * requests
  * six
  * wsgiref
  * zope.interface

Note: The SAML libraries are dependent on xmlsec1 being available on the machine. This will be need to be installed and readily available for Hue to use.

### **Configuring Hue**

Hue must be configured as a SP and use the SAML authentication backend.

#### **1. Hue as a Service Provider**

In the SAML 2.0 architecture, Hue acts as the SP. As such, it must be configured to communicate with the IdP in the hue.ini:

<pre>[libsaml]
xmlsec_binary=/opt/local/bin/xmlsec1
metadata_file=/tmp/metadata.xml
key_file=/tmp/key.pem
cert_file=/tmp/cert.pem</pre>

The key_file and cert_file can be copied from the Shibboleth IdP credentials directory (“/opt/shibboleth-idp/credentials/”). The files idp.key and kdp.crt correspond to cert_file and key_file, respectively. These files should already be in PEM format, so for purposes of this demo, they are renamed to key.pem and cert.pem.

The metadata_file is set to the file containing the IdP metadata (“/tmp/metadata.xml”). This can be created from the XML response of “http://<SHIBBOLETH HOST>:8443/idp/shibboleth/”. The XML itself may require some massaging. For example, in some fields, the port 8443 is missing from certain URLs.

The table below describes the available parameters for SAML in the hue.ini.

<pre>Parameter                  Description</pre>

<pre>xmlsec_binary                Xmlsec1 binary path. This program should be executable by the user running Hue.
create_users_on_login        Create users received in assertion response upon successful authentication and login.
required_attributes          Required attributes to ask for from IdP.
optional_attributes          Optional attributes to ask for from IdP.
metadata_file                IdP metadata in the form of a file. This is generally an XML file containing metadata that the Identity Provider generates.
key_file                     Private key to encrypt metadata with.
cert_file                    Signed certificate to send along with encrypted metadata.
user_attribute_mapping       A mapping from attributes in the response from the IdP to django user attributes.</pre>

Hue SAML configuration parameters.

#### **2. SAML Backend for Logging-in**

The SAML authentication backend must be used so that users can login and be created:

<pre>[desktop]
  [[auth]]
  backend=libsaml.backend.SAML2Backend</pre>

### **SAML and Hue in Action**

Now that Hue has been setup to work with the SAML IdP, attempting to visit any page redirects to Shibboleth’s login screen:

[<img src="https://cdn.gethue.com/uploads/2014/11/GwmNGDewG9NVYixw20Nu8vudVgaMkSKkmDGunCmyv-blzp1k6UHMHuEMGUeRHMu2LyMFQfzDjL50t6trylgTkPWLRpAr6-dMLv5f8gzjXuBwc6kMeysMnnSL.png"  />][20]

Shibboleth login screen after attempting to access /about.

After logging in, Hue is readily available and visible!

## **Summary**

Providing SSO support through SAML helps enterprises by enabling centralized authentication. From a user’s perspective, life is easier because it removes the burden of password management. After a user has logged in, they adhere to the same [permissions][21] and rules as other users.

Have any suggestions? Feel free to tell us what you think through [hue-user][22] or at [@gethue][23].

 [1]: https://gethue.com/how-ldap-and-saml-integration-with-hue-work/
 [2]: https://gethue.com/single-sign-on-in-hue-with-twitter-and-oauth/ "single sign-on"
 [3]: http://en.wikipedia.org/wiki/Security_Assertion_Markup_Language
 [4]: https://issues.cloudera.org/browse/HUE-2458
 [5]: https://issues.cloudera.org/browse/HUE-2458?focusedCommentId=25115&page=com.atlassian.jira.plugin.system.issuetabpanels:comment-tabpanel#comment-25115
 [6]: https://github.com/rohe/pysaml2
 [7]: https://bitbucket.org/lgs/djangosaml2
 [8]: https://groups.google.com/a/cloudera.org/forum/?fromgroups#!forum/hue-user
 [9]: https://twitter.com/gethue
 [10]: https://cdn.gethue.com/uploads/2014/11/WHL7QgcaoXi8PB71tkNHeqFSin4UzdPtvJdcX6-YauDxnP3tlTzUpDXM-RkO6twS07JEH1Xka1F-OfodIjCSr2E7ueyKRxb0tL8tHq0njdh1_ecoVYDv9min.png
 [11]: http://shibboleth.net/
 [12]: http://opends.java.net/
 [13]: http://tomcat.apache.org/download-60.cgi
 [14]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/hue-saml/shibboleth-conf/attribute-filter.xml#L26
 [15]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/hue-saml/tomcat6-conf/server.xml#L94
 [16]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/hue-saml/shibboleth-conf/login.config#L25
 [17]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/hue-saml/shibboleth-conf/relying-party.xml#L83
 [18]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/hue-saml/shibboleth-conf/handler.xml#L134
 [19]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/hue-saml/tomcat6-conf/web.xml#L117
 [20]: https://cdn.gethue.com/uploads/2014/11/GwmNGDewG9NVYixw20Nu8vudVgaMkSKkmDGunCmyv-blzp1k6UHMHuEMGUeRHMu2LyMFQfzDjL50t6trylgTkPWLRpAr6-dMLv5f8gzjXuBwc6kMeysMnnSL.png
 [21]: http://blog.cloudera.com/blog/2012/12/managing-permissions-in-hue/
 [22]: https://groups.google.com/a/cloudera.org/forum/?fromgroups#%21forum/hue-user
 [23]: https://twitter.com/gethue/
