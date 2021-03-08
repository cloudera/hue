---
title: Configure Hue with HTTPS / SSL
author: admin
type: post
date: 2015-01-16T02:26:14+00:00
url: /configure-hue-with-https-ssl/
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
SSL / HTTPS is often not simple. Here is some light in addition to the [Cloudera Security guide][1] that should help.

&nbsp;

## SSL between your browser and Hue

To configure Hue to use HTTPS we need a self signed SSL certificate that does not require a passphrase.

Here is how to generate a private key and a self-signed certificate for the Hue server:

<pre><code class="bash">openssl genrsa 4096 > server.key

openssl req -new -x509 -nodes -sha1 -key server.key > server.cert

</code></pre>

**

Note**: answer the questions that follow (complete example below). Entering the hostname for the server is important.

**Note:** you will have to tell your browser to "trust" the self signed server certificate

&nbsp;

Then in the Hue configuration in CM or in the [hue.ini][2]:

  * Check Enable HTTPS
  * Enter path to server.cert in Local Path to SSL Certificate (ssl_certificate)
  * Enter path to server.key in Local Path to SSL Private Key (ssl_private_key)

Make sure Hue is setting the [cookie as secure][3].

**Note**: when using a load balanced you might need to set in certain case [secure_proxy_ssl_header][4].

&nbsp;

[<img src="https://cdn.gethue.com/uploads/2015/01/hue-with-https-1024x573.png" />][5]

&nbsp;

Here is an example of creation of a certificate for enabling SSL:

<pre><code class="bash">

[root@cehd1 hue]# pwd

/home/hue

[root@cehd1 hue]# ls

cacerts  cert  key

</code></pre>

Generate a private key for the server:

<pre><code class="bash">[root@cehd1 hue]# openssl genrsa -out key/server.key 4096</code></pre>

Generate a "certificate request" for the server:

<pre><code class="bash">[root@cehd1 hue] openssl req -new -key key/server.key -out request/server.csr</code></pre>

You are about to be asked to enter information that will be incorporated into your certificate request. What you are about to enter is what is called a Distinguished Name or a DN.

There are quite a few fields but you can leave some blank. For some fields there will be a default value, if you enter '.', the field will be left blank.

<pre><code class="bash">Country Name (2 letter code) [XX]:US

State or Province Name (full name) []:Colorado

Locality Name (eg, city) [Default City]:Denver

Organization Name (eg, company) [Default Company Ltd]:Cloudera

Organizational Unit Name (eg, section) []:COE

Common Name (eg, your name or your server's hostname) []:test.lab

Email Address []:

Please enter the following 'extra' attributes to be sent with your certificate request

A challenge password []:  ## note this was left

An optional company name []:

</code></pre>

Self-sign the request, creating a certificate for the server:

<pre><code class="bash">[root@cehd1 hue] openssl x509 -req -days 365 -in request/server.csr -signkey key/server.key -out cert/server.crt

Signature ok

subject=/C=US/ST=Colorado/L=<wbr />Denver/O=Cloudera/OU=COE/CN=test.lab

Getting Private key

</code></pre>

<pre><code class="bash">[root@cehd1 hue]# ls -lR

.

total 16

drwxr-xr-x 2 hue  root 4096 Jul 16 18:04 cacerts

drwxr-xr-x 2 root root 4096 Jul 31 10:02 cert

drwxr-xr-x 2 root root 4096 Jul 31 09:46 key

drwxr-xr-x 2 root root 4096 Jul 31 10:00 request

./cacerts:

total 4

-rw-r-r- 1 hue root 2036 Jul 16 18:04 win2k8x64-ad2-ca.pem

./cert:

total 4

-rw-r-r- 1 root root 1907 Jul 31 10:02 server.crt

./key:

total 4

-rw-r-r- 1 root root 3243 Jul 31 09:49 server.key

./request:

total 4

-rw-r-r- 1 root root 1704 Jul 31 10:00 server.csr

</code></pre>

&nbsp;

## SSL between Hue and the Hadoop components

The above was for having the Web browser use SSL when talking with Hue. In order to have Hue use SSL for talking to YARN, Hive, HDFS, ... we need another property: REQUESTS_CA_BUNDLE as described in [HUE-2082][6] (and sometimes more in the case of [Hive][7] for example).

&nbsp;

I discovered that Hue's truststore (the file pointed to by REQUESTS_CA_BUNDLE) has to contain the certificate not only of the NameNode, but of other nodes as well. I don't know exactly which other nodes, but I suspect it's every node that has a DataNode role. It's easiest just to assume that the certs for all nodes need to be in the Hue truststore.

This is because we're using self-signed test certs, not CA-signed certs. If we were using CA-signed certs, we could just put the CA cert chain in the Hue truststore.

Also, the Hue truststore has to be in PEM file format. At Cloudera we are using the JKS format for Hadoop SSL. So in order to populate the Hue truststore, you have to extract the certificates from the JKS keystores and convert them to PEM format. Here are the commands for doing that, given a JKS keystore called hadoop-server.keystore, on a host named foo-1.ent.cloudera.com:

<div class="preformatted panel">
  <div class="preformattedContent panelContent">
    <p>
      <pre><code class="bash">keytool -exportcert -keystore hadoop-server.keystore -alias foo-1.cloudera.com \<br /> -storepass cloudera -file foo-1.cert<br /> openssl x509 -inform der -in foo-1.cert > foo-1.pem<br /> </code></pre>
    </p>

    <p>
      Once you've done this for each host in the cluster, you can concatenate the .pem files into one .pem file which can serve as the Hue truststore:
    </p>

    <div class="preformatted panel">
      <div class="preformattedContent panelContent">
        <p>
          <pre><code class="bash">cat foo-1.pem foo-2.pem ... > huetrust.pem</code></pre>
        </p>
      </div>
    </div>

    <p>
      After running it, set REQUESTS_CA_BUNDLE in the Hue environment safety valve to /etc/hadoop/ssl-conf/huetrust.pem
    </p>

    <p>
      <a href="https://cdn.gethue.com/uploads/2015/01/hue-contact-https.png"><img src="https://cdn.gethue.com/uploads/2015/01/hue-contact-https-1024x570.png" /></a>
    </p>

    <p>
      &nbsp;
    </p>

    <p>
      Here is an interesting <a href="http://www.akadia.com/services/ssh_test_certificate.html">link</a> if you want to read more about generating SSL certificates.
    </p>

    <p>
      &nbsp;
    </p>

    <p>
      As usual feel free to comment and send feedback on the <a href="http://groups.google.com/a/cloudera.org/group/hue-user">hue-user</a> list or <a href="https://twitter.com/gethue">@gethue</a>!
    </p>

    <p>
      &nbsp;
    </p>

    <p>
      &nbsp;
    </p>

    <p>
      &nbsp;
    </p>
  </div>
</div>

 [1]: http://www.cloudera.com/content/cloudera/en/documentation/core/latest/topics/cm_sg_create_deploy_certs.html?scroll=xd_583c10bfdbd326ba--6eed2fb8-14349d04bee--7723
 [2]: https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/
 [3]: https://gethue.com/recent-security-enhancements/
 [4]: https://docs.djangoproject.com/en/1.7/ref/settings/#secure-proxy-ssl-header
 [5]: https://cdn.gethue.com/uploads/2015/01/hue-with-https.png
 [6]: https://issues.cloudera.org/browse/HUE-2082
 [7]: https://gethue.com/hadoop-tutorial-ssl-encryption-between-hue-and-hive/
