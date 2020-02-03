---
title: 'Hadoop Tutoriel: comment créer des tables d’exemple dans HBase'
author: admin
type: post
date: 2014-03-26T06:49:41+00:00
url: /hadoop-tutoriel-comment-creer-des-tables-dexemple-dans-hbase/
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

<p id="docs-internal-guid-7c74e5e3-7999-5a0b-77ef-ac77803cb105">
  <a href="http://gethue.tumblr.com/post/55581863077/hue-2-5-and-its-hbase-app-is-out">Hue 2.5</a>&nbsp;est livr&eacute; avec une autre nouvelle application pour rendre Apache Hadoop plus facile &agrave; utiliser: HBase Browser pour&nbsp;<a href="http://hbase.apache.org/">Apache HBase</a>,&nbsp;la principale base de donn&eacute;es cl&eacute;/valeur pour Hadoop.&nbsp;Cet article est le premier &eacute;pisode d'une s&eacute;rie de 3 d&eacute;crivant la nouvelle exp&eacute;rience utilisateur apport&eacute;e par l'application.&nbsp;Nous allons commencer par vous d&eacute;crire comment cr&eacute;er des tables d'&eacute;chantillons avec diff&eacute;rents sch&eacute;mas de HBase.
</p></p>

# Tutoriel

Lors de la construction du nouveau navigateur de HBase, nous avons voulu tester l'application sur diff&eacute;rentes tables de HBase.&nbsp;Il est difficile de trouver sur Internet un sch&eacute;ma et des donn&eacute;es pr&ecirc;t &agrave; utiliser.&nbsp;Par cons&eacute;quent, bas&eacute;&nbsp;sur les cas de utilisations les plus courantes, nous avons cr&eacute;&eacute; nos nos propres sch&eacute;mas de HBase et avons d&eacute;cid&eacute; de les partager afin d'aider tous ceux qui souhaitent commencer avec HBase.</p>

Ce how-to d&eacute;crit comment cr&eacute;er une table tr&egrave;s simple qui compte le nombre de votes par candidat par jour.&nbsp;Ensuite, la partie 2 se concentre sur la cr&eacute;ation d'une table HBase avec beaucoup de colonnes et la partie 3 sur l'insertion et la visualisation de donn&eacute;es binaires.</p>

{{< youtube j7wOdT_6J-8 >}}</p>

# Configuration

L'application Navigateur HBase est adapt&eacute;e pour la navigation rapidement sur d'&eacute;normes tables et pour acc&eacute;der &agrave; n'importe quel contenu.&nbsp;Vous pouvez &eacute;galement cr&eacute;er de nouvelles tables, ajouter des donn&eacute;es, modifier des cellules existantes et filtrer les donn&eacute;es avec la barre de recherche autocompletant.</p>

La premi&egrave;re &eacute;tape consiste &agrave; installer HBase dans votre cluster Hadoop.&nbsp;Nous vous recommandons d'utiliser les&nbsp;[paquets][1]&nbsp;CDH&nbsp;.&nbsp;HBase navigateur n&eacute;cessite le&nbsp;[service Thrift 1][2]&nbsp;d&eacute;marr&eacute;.</p>

Ensuite, prenez l'application &agrave; partir d'une [version][3]{.trackLink}&nbsp;de Hue ou avec la version du&nbsp;[pacquet][4]&nbsp;.&nbsp;CDH 4.4 (arrivant d&eacute;but Septembre) apportera une v1 stable.&nbsp;Apr&egrave;s l'installation, si le HBase master ne fonctionne pas sur le m&ecirc;me h&ocirc;te que Hue, il faut pointer l'application vers lui en mettant &agrave; jour le&nbsp;[hue.ini][5]&nbsp;et red&eacute;marrer Hue.</p>

Ensuite, allez &agrave;&nbsp;[http://127.0.0.1:8888/hbase/&nbsp;][6]pour v&eacute;rifier que tout est correctement configur&eacute;!&nbsp;Nous montrons dans la vid&eacute;o comment cr&eacute;er une table et ajouter des colonnes en seulement quelques clics.&nbsp;Dans les &eacute;tapes suivantes, nous montrons comment cr&eacute;er et remplir un v&eacute;ritable exemple de table.</p>

Les donn&eacute;es et les scripts exemples sont publi&eacute;s sur&nbsp;[github][7]&nbsp;.&nbsp;Dans un terminal, utiliser&nbsp;[git][8]&nbsp;pour r&eacute;cup&eacute;rer le d&eacute;p&ocirc;t:

<pre class="code">cd / tmp
git clone <a href="https://github.com/romainr/hadoop-tutorials-examples.git">https://github.com/romainr/hadoop-tutorials-examples.git</a>
cd HBASE-tables
</pre></p>

# Table d'analyse

Les objectifs de ces donn&eacute;es est de montrer la recherche et la disposition intelligente dans HBase Browser.</p>

Cette table contient plus de 1000 colonnes de texte.&nbsp;L'id&eacute;e est d'avoir des compteurs pour 3 domaines Web de 3 pays pour chaque heure de la journ&eacute;e.&nbsp;Les donn&eacute;es sont ensuite agr&eacute;g&eacute;es par jour et pour tous les pays.

<img alt="image" height="88px;" src="https://lh6.googleusercontent.com/6ETWVbvV06zSHbrDglMlqaMfJB-HMrHpJYF27xTFbbQB88jdKRSlVCIjkYl0EYRFFm31iCp-PN-7q7_cNBKQd_820Cqkv674V7e9MPV00N_T_nGm7jv2R_O8" width="800px;" />

Sch&eacute;ma de la table</p>

Comment faire pour cr&eacute;er la table HBase et ins&eacute;rer quelques donn&eacute;es:</p>

1. G&eacute;n&eacute;rer des noms de colonnes et des donn&eacute;es avec&nbsp;[create_schemas.py][9]&nbsp;.&nbsp;Lancez-le avec ./create_schemas.py

2. Uploader les donn&eacute;es date /tmp/hbase-analytics.tsv &agrave; HDFS avec l'explorateur de fichiers

3. Avec HBase Browser cr&eacute;er la table un "Analytics" avec 3 colonnes family "hour"', "day","total"

4. Charger les donn&eacute;es dans la table avec la&nbsp;[commande d'importation en vrac de HBase][10]&nbsp;.

Ceci va d&eacute;clencher un job MapReduce et afficher la&nbsp;[progression][11]&nbsp;de l'importation.</p>

C'est tout!&nbsp;Allez ouvrir la table d'analyse dans&nbsp;[le navigateur HBase][12]&nbsp;!</p>

# Table binaire

Cette seconde tableaux portent principalement sur les cellules de donn&eacute;es de grandes, de divers formats, ce qui d&eacute;montre la pr&eacute;visualisation et l'&eacute;dition de donn&eacute;es dans HBase Browser.</p>

Nous utilisons l'API de l'application pour ins&eacute;rer dans HBase certaines cellules de diff&eacute;rents types de contenu, par exemple du texte, du JSON, des photos, du binaires ...</p>

1. D'abord cr&eacute;er une table &laquo;event&raquo; avec une colonne family 'doc'.

2. Puis cd dans le r&eacute;pertoire racine de Hue

3. cd /usr/share/hue

4. /opt/cloudera/parcels/CDH-4.X/share/hue&nbsp;(si vous utilisez les parcels)

Et aller dans le shell build/env/bin/hue shell&nbsp;et lancer&nbsp;[locad_binary.py:][13]</p>

Avec l'API HBase ins&eacute;rer des donn&eacute;es textuelles:</p>

<pre class="code">from hbase.api import HbaseApi

HbaseApi().putRow('Cluster', 'events', 'hue-20130801', {'doc:txt': 'Hue is awesome!'})
HbaseApi().putRow('Cluster', 'events', 'hue-20130801', {'doc:json': '{"user": "hue", "coolness": "extra"}'})
HbaseApi().putRow('Cluster', 'events', 'hue-20130802', {'doc:version': 'I like HBase'})
HbaseApi().putRow('Cluster', 'events', 'hue-20130802', {'doc:version': 'I LOVE HBase'})
</pre></p>

Ensuite, ins&eacute;rer une image, et une page HTML et PDF:

<pre class="code">root='/tmp/hadoop-tutorials-examples'

HbaseApi().putRow('Cluster', 'events', 'hue-20130801', {'doc:img': open(root + '/hbase-tables/data/hue-logo.png', "rb").read()})
HbaseApi().putRow('Cluster', 'events', 'hue-20130801', {'doc:html': open(root + '/hbase-tables/data/gethue.com.html', "rb").read()})
HbaseApi().putRow('Cluster', 'events', 'hue-20130801', {'doc:pdf': open(root + '/hbase-tables/data/gethue.pdf', "rb").read()})
</pre></p>

Notez que les noms de colonnes ne comptent pas pour la d&eacute;tection de type.&nbsp;Allez voir la table "[events][14]" et jouer avec!</p>

# Conclusion

Ces deux sch&eacute;mas et de donn&eacute;es permettent &agrave; l'utilisateur de facilement d&eacute;marrer avec HBase.&nbsp;Cette premi&egrave;re version de HBase Browser apporte une nouvelle fa&ccedil;on d'explorer rapidement et rechercher des lignes et des colonnes.&nbsp;Les nouvelles versions supporteront des bulks loads afin de lib&eacute;rer compl&egrave;tement l'utilisateur de la ligne de commande.

La nouvelle application de navigation de HBase sera d&eacute;mo-&eacute;e sur ces deux tableaux dans les prochains posts, alors restez branch&eacute;s!

[1]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH4/latest/CDH4-Installation-Guide/cdh4ig_topic_20_2.html
[2]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH4/latest/CDH4-Installation-Guide/cdh4ig_topic_20_5.html#topic_20_5_4_unique_1
[3]: https://cdn.gethue.com/downloads/releases/hbase/hue-hbase-2.5.0.tgz
[4]: http://nightly.cloudera.com/cdh4/
[5]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L505
[6]: http://127.0.0.1:8888/hbase/
[7]: https://github.com/romainr/hadoop-tutorials-examples/tree/master/hbase-tables
[8]: http://git-scm.com/
[9]: https://raw.github.com/romainr/hadoop-tutorials-examples/master/hbase-tables/create_schemas.py
[10]: https://raw.github.com/romainr/hadoop-tutorials-examples/master/hbase-tables/load_data.sh
[11]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/hbase-tables/load_data.log
[12]: http://127.0.0.1:8888/hbase/#Cluster/analytics
[13]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/hbase-tables/load_binary.py
[14]: http://127.0.0.1:8888/hbase/#Cluster/events
