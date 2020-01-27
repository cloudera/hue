---
title: 'Hadoop tutoriel: comment accéder à Hive depuis Pig avec HCatalog et Hue'
author: admin
type: post
date: 2014-03-26T06:50:43+00:00
url: /hadoop-tutoriel-comment-acceder-a-hive-depuis-pig-avec-hcatalog-et-hue/
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
  - right-sidebar
sf_left_sidebar:
  - Sidebar-1
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
slide_template:
  - default
categories:
---

### Ce blog est sur ​​l'acc&egrave;s du Metastore de Hive avec Hue, l'open source Hadoop UI et &eacute;claircir une certaine confusion sur l'utilsation de HCatalog. {.subhead}</p>

# Qu'est ce HCatalog?

<a href="http://hive.apache.org/docs/hcat_r0.5.0/" target="_blank" rel="noopener noreferrer">Apache HCatalog</a>&nbsp;est un projet permettant au application autres que Hive d'acc&eacute;der a ses tables.&nbsp;Vous pouvez ensuite charger directement les tables avec Pig ou MapReduce sans avoir &agrave; vous soucier de re-d&eacute;finir les sch&eacute;mas d'entr&eacute;e, de l'emplacement des donn&eacute;es ou leur duplication.</p>

Hue est livr&eacute; avec une application pour acc&eacute;der &agrave; la metastore de Hive au sein de votre navigateur: Metastore Browser.&nbsp;Bases de donn&eacute;es et les tables peuvent &ecirc;tre parcourus &agrave; travers et cr&eacute;&eacute;s ou supprim&eacute;s avec des assistants.</p>

Les assistants ont &eacute;t&eacute; d&eacute;montr&eacute;es dans le pr&eacute;c&eacute;dent tutoriel sur la fa&ccedil;on d'&nbsp;[analyser les donn&eacute;es de Yelp][1]&nbsp;.&nbsp;Hue utilise&nbsp;[HiveServer2][2]&nbsp;pour acc&eacute;der au Hive Metastore au lieu de HCatalog.&nbsp;C'est parce que HiveServer2 est le nouveau serveur concurrent s&eacute;curis&eacute;e et multi-usages pour la Hive et il inclut d&eacute;j&agrave; une riche et rapide API pour contacter le metastore.</p>

Des connecteurs pour HCatalog sont cependant utiles pour acc&eacute;der aux donn&eacute;es de Hive depuis Pig.&nbsp;Voici une d&eacute;mo sur l'acc&egrave;s &agrave; l'exemple des tables de Hive depuis&nbsp;[Pig][3].</p>

Voici un r&eacute;sum&eacute; vid&eacute;o (en anglais) des nouvelles fonctionnalit&eacute;s:

{{< youtube FgozGP1JdI0 >}}</p>

# Tutoriel

Vous devez d'abord installer HCatalog partir&nbsp;[ici][4]&nbsp;ou Cloudera Manager.&nbsp;Si vous utilisez un cluster non pseudo-distribu&eacute; (par exemple, pas sur une machine virtuelle de d&eacute;monstration) faire en sorte que le Metastore de Hive est&nbsp;[&agrave; distance][5]&nbsp;ou vous aurez une erreur comme ci-dessous.&nbsp;Ensuite, transf&eacute;rez les 3 jars de /usr/lib/HCatalog/share/HCatalog/ et tous ceux de Hive &agrave; partir de /usr/lib/hive/lib dans la Pig sharelib de Oozie situ&eacute;e dans /user/oozie/share/lib/pig.&nbsp;Cela peut &ecirc;tre fait en quelques clics, tout en &eacute;tant connect&eacute; en tant que utilsateur &laquo;oozie&raquo; ou &laquo;HDFS&raquo; dans le Navigateur de fichiers.</p>

M&eacute;fiez-vous, tous les jars seront inclus dans tous les scripts de Pig, ce qui pourrait ne pas &ecirc;tre n&eacute;cessaire.&nbsp;Une autre solution serait de transf&eacute;rer ces jars dans votre r&eacute;pertoire home HDFS et ensuite inclure le chemin vers le r&eacute;pertoire avec une propri&eacute;t&eacute; Hadoop 'oozie.libpath' dans la section 'Propri&eacute;t&eacute;s' de l'&eacute;diteur de Pig.</p>

Ensuite, assurez-vous que les exemples de Beeswaz sont install&eacute;s (&eacute;tape n &deg; 2 &agrave; l'Assistant de d&eacute;marrage rapide) et d'ouvrir l'&eacute;diteur de Pig et de calculer le&nbsp;[salaire moyen][6]&nbsp;dans le tableau (&eacute;quivalent de cette &nbsp;[requ&ecirc;te][7]&nbsp;Hive):</p>

<pre class="code">- Tableau des charges 'sample_07'
sample_07 = LOAD 'sample_07' en utilisant org.apache.hcatalog.pig.HCatLoader ();

- Calculer le salaire moyen de la table
salaires = GROUPE sample_07 tous;
out = FOREACH salaires GENERATE AVG (sample_07. salaire);
vider;
</pre></p>

Comme HCatalog a besoin d'acc&eacute;der au metastore, nous devons pr&eacute;ciser la hive-site.xml.&nbsp;Allez dans &laquo;Propri&eacute;t&eacute;s&raquo;, &laquo;Ressources&raquo; et ajouter un &laquo;Fichier&raquo; pointant vers la hive-site.xml upload&eacute;&nbsp;sur le HDFS.</p>

Puis soumettre le script en appuyant sur CTRL + ENTRER!&nbsp;Le r&eacute;sultat (47963,62637362637)

appara&icirc;tra &agrave; la fin des logs.</p>

Notez que nous n'avons pas besoin de red&eacute;finir le sch&eacute;ma ca 'il est automatiquement capt&eacute; par le loader.&nbsp;Si vous utilisez l'Application Oozie, vous pouvez maintenant utiliser librement HCatalog dans vos actions Pig.</p>

**Attention!**

Si vous obtenez ce message d'erreur, cela signifie que votre metastore appartient &agrave; l'utilisateur Hive et n'est pas configur&eacute; en remote.

<pre class="code">Cannot get a connection, pool error Could not create a validated object, cause: A read-only user or a user in a read-only database is not permitted to disable read-only mode on a connection.

2013-07-24 23: 20:04,969 [main] INFO DataNucleus.Persistence - DataNucleus Persistance usine initialis&eacute; pour datastore URL = "jdbc: derby:; databaseName = / var / lib / ruche / metastore / metastore_db; create = true" driver = "org.apache.derby . jdbc.EmbeddedDriver "username =" APP "
</pre></p>

<pre class="code">sudo rm /var/lib/hive/metastore/metastore_db/*lck
sudo chmod 777 -R /var/lib/hive/metastore/metastore_db
</pre></p>

De m&ecirc;me que HCatLoader, utilisez&nbsp;[HCatStorer][8]&nbsp;pour mettre &agrave; jour la table, par exemple:

<pre class="code">STORE alias INTO 'sample_07' USING org.apache.hcatalog.pig.HCatStorer();
</pre></p>

# R&eacute;sum&eacute;

Nous avons vu que Hue fait permet d'acceder le Hive Metastore facilement et prend en charge les connecteurs HCatalog pour Pig.&nbsp;Hue 3,0 simplifiera encore plus en copiant automatiquement les fichiers jar n&eacute;cessaires eten rendant les noms de table&nbsp;[auto-completant][9]&nbsp;!

Comme d'habitude, nous nous r&eacute;jouissons de vos commentaires sur le&nbsp;[groupe d'utilisateurs][10]&nbsp;!

[1]: http://blog.cloudera.com/blog/2013/04/demo-analyzing-data-with-hue-and-hive/
[2]: http://blog.cloudera.com/blog/2013/07/how-hiveserver2-brings-security-and-concurrency-to-apache-hive/
[3]: http://gethue.tumblr.com/post/51559235973/tutorial-apache-pig-editor-in-hue-2-3
[4]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH4/latest/CDH4-Installation-Guide/cdh4ig_topic_19.html
[5]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH4/latest/CDH4-Installation-Guide/cdh4ig_hive_metastore_configure.html
[6]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/hcatalog/avg_salary.pig
[7]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/hcatalog/avg_salary.hql
[8]: http://hive.apache.org/docs/hcat_r0.5.0/loadstore.html#HCatStorer
[9]: https://issues.cloudera.org/browse/HUE-1409
[10]: http://groups.google.com/a/cloudera.org/group/hue-user
