---
title: SSL Encryption between Hue and Hive
author: admin
type: post
date: 2014-09-22T18:20:36+00:00
url: /hadoop-tutorial-ssl-encryption-between-hue-and-hive/
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
slide_template:
  - default
categories:

---
_This blog post was originally published on the_ [_MapR blog_][1]_._

While big data security analytics promises to deliver great insights in the battle against cyber threats, the concept and the tools are still maturing. In this blog, I’ll simplify the topic of adopting security in Hadoop by showing you how to encrypt traffic between Hue and Hive.

[<img src="https://cdn.gethue.com/uploads/2014/09/hue-ssl-hive.jpg" />][2]

Hue can communicate with Hive over a channel encrypted with SSL. Let’s take a look at the interface and the handshake mechanism first before trying to secure it.

Note: HiveServer2 currently does not support SSL when using Kerberos

&nbsp;

The basic high-level idea concept behind the SSL protocol handshake mechanism is shown in the diagram shown below, where Hue is the SSL Client, and Hive is the SSL Server:

[<img src="https://cdn.gethue.com/uploads/2014/09/huehive_img1.png"  />][3]

a. SSL Client (Hue) opens a socket connection and connects to Hive. This is then encapsulated with a wrapper that encrypts and decrypts the data going over the socket with SSL.

b. Once Hive receives an incoming connection, it shows a certificate to Hue (which is like a public key saying it can be trusted).

c. Hue can then verify the authenticity of this certificate with a trusted certificate-issuing authority, or it can be skipped for self-signed certificates.

d. Hue encrypts messages using this public key and sends data to Hive.

e. Hive decrypts the message with its private key.

&nbsp;

The public/private keys always come in pairs and are used to encrypt/decrypt messages. These can be generated with the UNIX keytool command-line utility which is understood by the Java keystore library, or with the UNIX OpenSSL utility which is understood directly by the Python SSL library.

&nbsp;

The Hive-side uses Java keystore certificates and public/private keys and Hue’s Python code calls the SSL library implemented in C. Much of the complication arises in not having one uniform format which can be understood by all languages—Python, Java and C. For example, the SSL C library on the client side expects a private key from the SSL server, which is not a requirement in a pure java SSL client implementation. Using the Java keytool command, you cannot export a private key directly into the pem format understood by Python. You need an intermediate PKCS12 format.

&nbsp;

Let’s step through the procedure to create certificates and keys:

1) Generate keystore.jks containing private key (used by Hive to decrypt messages received from Hue over SSL) and public certificate (used by Hue to encrypt messages over SSL)

<pre><code class="bash">keytool -genkeypair -alias certificatekey -keyalg RSA -validity 7 -keystore

keystore.jks

</code></pre>

2) Generate certificate from keystore

<pre><code class="bash">keytool -export -alias certificatekey -keystore keystore.jks -rfc -file

cert.pem

</code></pre>

3) Export private key and certificate with openSSL for Hue's SSL library to ingest.

Exporting the private key from a jks file (Java keystore) needs an intermediate PKCS12:

a. Import the keystore from JKS to PKCS12

<pre><code class="bash">keytool -importkeystore -srckeystore keystore.jks -destkeystore keystore.p12

-srcstoretype JKS -deststoretype PKCS12 -srcstorepass mysecret -deststorepass

mysecret -srcalias certificatekey -destalias certificatekey -srckeypass

mykeypass -destkeypass mykeypass -noprompt

</code></pre>

b. Convert pkcs12 to pem using OpenSSL

<pre><code class="bash">openssl pkcs12 -in keystore.p12 -out keystore.pem -passin pass:mysecret

-passout pass:mysecret

</code></pre>

c. Strip the pass phrase so Python doesn't prompt for password while connecting to Hive

<pre><code class="bash">openssl rsa -in keystore.pem -out hue_private_keystore.pem

</code></pre>

&nbsp;

Then the following needs to be setup in Hue’s configuration file hue.ini under [beeswax] section:

<pre><code class="bash"> [[ssl]]

\# SSL communication enabled for this server. (optional since Hue 3.8)

enabled=true

\# Path to Certificate Authority certificates. (optional)

\## cacerts=/etc/hue/cacerts.pem

\# Choose whether Hue should validate certificates received from the server.

validate=false

</code></pre>

&nbsp;

Then make sure no custom authentication mechanism is turned on and configure your hive-site.xml with the following properties on Hive 0.13:

<pre><code class="xml"> <property>

  <name>hive.server2.use.SSL</name>

  <value>true</value>

</property>

<property>

  <name>hive.server2.keystore.path</name>

  <value>/path/to/keystore.jks</value>

</property>

<property>

  <name>hive.server2.keystore.password</name>

  <value>mysecret</value>

</property>

</code></pre>

&nbsp;

**Note**

On Hive 0.12, the property is _hive.server2.enable.SSL_ instead of _hive.server2.use.SSL_.

&nbsp;

That’s it—you’re done!

As usual feel free to comment and send feedback on the [hue-user][4] list or [@gethue][5]!

&nbsp;

**Suhas Satish**

Hadoop Ecosystem Software Developer, MapR

Suhas Satish is a Hadoop ecosystem software developer at MapR Technologies and has contributed to Apache Pig, Hue, Hive, Flume and Sqoop projects. Suhas has an MS in Computer Engineering from North Carolina State University and a B.Tech in Electronics & Communications Engineering from National Institute of Technology Karnataka, Surathkal, India.

 [1]: https://www.mapr.com/blog/ssl-encryption-between-hue-and-hive
 [2]: https://cdn.gethue.com/uploads/2014/09/hue-ssl-hive.jpg
 [3]: https://cdn.gethue.com/uploads/2014/09/huehive_img1.png
 [4]: http://groups.google.com/a/cloudera.org/group/hue-user
 [5]: https://twitter.com/gethue
