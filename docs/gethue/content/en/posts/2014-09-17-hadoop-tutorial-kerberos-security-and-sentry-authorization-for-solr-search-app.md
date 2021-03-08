---
title: Kerberos security and Sentry authorization for Solr Search App
author: admin
type: post
date: 2014-09-17T11:56:20+00:00
url: /hadoop-tutorial-kerberos-security-and-sentry-authorization-for-solr-search-app/
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
This blog post details how to use Kerberos and Sentry in the Hue [Search Application][1]. If you only want to use Kerberos, just skip the paragraphs about Sentry.

&nbsp;

[Kerberos][2] enables you to authenticate users in your Hadoop cluster. For example, it guarantees that it is really the user ‘bob’ and not ‘joe’ that is submitting a job, listing files or doing a search. Next step is configuring what the user can access, this is called [authorization][3]. [Sentry][4] is the secure way to define who can see, query, add data in the Solr collections/indexes. This is only possible as we guarantee the usernames performing the actions with Kerberos.

&nbsp;

Hue comes with a set of collections and examples ready to be installed. However, with Kerberos, this requires a bit more than just [one click][5].

First, make sure that you have a [kerberized Cluster][6] (and it particular [Solr Search for Hue][7]) with [Sentry configured][8].

Make sure you use the secure version of solrconfig.xml:

<pre><code class="bash">solrctl instancedir -generate foosecure

cp foosecure/conf/solrconfig.xml.secure solr_configs_twitter_demo/conf/solrconfig.xml

solrctl instancedir -update twitter_demo solr_configs_twitter_demo

solrctl collection -reload twitter_demo

</code></pre>

Then, create the collection. The command should work as-is if you have the proper Solr environment variables.

<pre><code class="bash">cd $HUE_HOME/apps/search/examples/bin

./create_collections.sh

</code></pre>

&nbsp;

You should then see the collections:

<pre><code class="bash">solrctl instancedir -list

jobs_demo

log_analytics_demo

twitter_demo

yelp_demo

</code></pre>

&nbsp;

The next step is to create the Solr cores. To keep it simple, we will just use one collection, the twitter demo. When creating the core

<pre><code class="bash">sudo -u systest solrctl collection -create twitter_demo -s 1</code></pre>

if using Sentry, you will probably see this error the first time:

<pre><code class="bash">Error: A call to SolrCloud WEB APIs failed: HTTP/1.1 401 Unauthorized

Server: Apache-Coyote/1.1

WWW-Authenticate: Negotiate

Set-Cookie: hadoop.auth=; Version=1; Path=/; Expires=Thu, 01-Jan-1970 00:00:00 GMT; HttpOnly

Content-Type: text/html;charset=utf-8

Content-Length: 997

Date: Thu, 11 Sep 2014 16:32:17 GMT</pre>

<pre>HTTP/1.1 401 Unauthorized

Server: Apache-Coyote/1.1

WWW-Authenticate: Negotiate YGwGCSqGSIb3EgECAgIAb10wW6ADAgEFoQMCAQ+iTzBNoAMCARCiRgRE62zOpPwr+KLoFKdUX2I6FtbN0DyxSA5a8n4BSZRJMTf413TEXzJbVh3/G7jWiMasIIzeETrd0Bv8suBsuKS/HdqG068=

Set-Cookie: hadoop.auth="u=systest&p=systest@ENT.CLOUDERA.COM&t=kerberos&e=1410489137684&s=qAkcQr4ZPBkn5Ewg/Ugz/CqgLkU="; Version=1; Path=/; Expires=Fri, 12-Sep-2014 02:32:17 GMT; HttpOnly

Content-Type: application/xml;charset=UTF-8

Transfer-Encoding: chunked

Date: Thu, 11 Sep 2014 16:32:17 GMT

<?xml version="1.0" encoding="UTF-8"?>

<response>

<lst name="responseHeader">

<int name="status">

401</int>

<int name="QTime">

18</int>

</lst>

<lst name="error">

<str name="msg">

org.apache.sentry.binding.solr.authz.SentrySolrAuthorizationException: User systest does not have privileges for admin</str>

<int name="code">

401</int>

</lst>

</code></pre>

&nbsp;

This is because by default our ‘systest’ user does not have permissions to create the core. ‘systest’ belongs to the ‘admin’ Unix/LDAP group and we need to create a Sentry group that includes the privileges named ‘admin’. Our ‘systest’ user needs to belongs to the group that contains this role.

&nbsp;

In order to do this, we need to update:

<pre><code class="bash">/user/solr/sentry/sentry-provider.ini</code></pre>

&nbsp;

with something similar to this:

<pre><code class="bash">[groups]

admin = admin_role

analyst = query_role

[roles]

admin_role = collection=admin->action=\*, collection=twitter_demo->action=\*

query_role = collection=twitter_demo->action=query

</code></pre>

&nbsp;

‘systest’ belongs to the LDAP ‘admin’ group. ‘admin’ is assigned the ‘eng_role’ role with the ‘admin’ privilege. Regular analyst users belong to the LDAP ‘analyst’ group that contains the Sentry ‘read_only’ role and its ‘query’ permission for the twitter collection. Here is the list of available [permissions][9].

&nbsp;

**Note**

The upcoming Hue 3.7 has a new Sentry App that lets you forget about sentry-provider.ini and enables you to configure the above in a Web UI. Moreover, Solr Sentry support we be integrated in Hue as soon as its API becomes available.

&nbsp;

Then it is time to create the core and upload some data. Update the [post.sh][10]  command to make it work with Kerberos.

Replace ‘curl’ by:

<pre><code class="bash">curl -negotiate -u: foo:bar</code></pre>

&nbsp;

and make sure that you use the real hostname in the URL:

<pre><code class="bash">URL=http://hue-c5-sentry.ent.cloudera.com:8983/solr</code></pre>

&nbsp;

A quick way to test is is to run the indexing command:

<pre><code class="bash">sudo -u systest curl -negotiate -u: foo:bar http://hue-c5-sentry.ent.cloudera.com:8983/solr/twitter_demo/update -data-binary @../collections/solr_configs_twitter_demo/index_data.csv -H 'Content-type:text/csv'</code></pre>

&nbsp;

And that’s it! The collection with its data will appear into Solr and Hue. Depending on its group, the user can or cannot modify the collection.

[<img src="https://cdn.gethue.com/uploads/2014/09/hue-collections-1024x488.png" />][11]

&nbsp;

Your organization can now leverage the exploration capacity of the Search app with fine grained security! Next versions will come up with field level security and a nice UI for configuring it (no more sentry-provider.ini :).

&nbsp;

As usual feel free to comment on the [hue-user][12] list or [@gethue][13]!

 [1]: https://gethue.com/hadoop-search-dynamic-search-dashboards-with-solr/
 [2]: http://en.wikipedia.org/wiki/Kerberos_%28protocol%29
 [3]: http://en.wikipedia.org/wiki/Authorization
 [4]: https://sentry.incubator.apache.org/
 [5]: https://gethue.com/tutorial-live-demo-of-search-on-hadoop/
 [6]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH5/latest/CDH5-Security-Guide/CDH5-Security-Guide.html
 [7]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH5/latest/CDH5-Security-Guide/cdh5sg_search_security.html#concept_jrk_lzc_fm_unique_2
 [8]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM4Ent/latest/Cloudera-Manager-Managing-Clusters/cmmc_sentry_search_config.html
 [9]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/Search/latest/Cloudera-Search-User-Guide/csug_sentry.html#concept_wc2_yhp_wk_unique_1
 [10]: https://github.com/cloudera/hue/blob/master/apps/search/examples/bin/post.sh
 [11]: https://cdn.gethue.com/uploads/2014/09/hue-collections.png
 [12]: http://groups.google.com/a/cloudera.org/group/hue-user
 [13]: https://twitter.com/gethue
