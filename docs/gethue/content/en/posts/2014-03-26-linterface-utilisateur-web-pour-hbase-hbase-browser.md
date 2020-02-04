---
title: 'L’interface utilisateur Web pour HBase: HBase Browser'
author: admin
type: post
date: 2014-03-26T06:48:30+00:00
url: /linterface-utilisateur-web-pour-hbase-hbase-browser/
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

Dans ce post, nous allons jeter un oeil &agrave; la nouvelle application de navigation de HBase ajout&eacute; &agrave; Hue 2.5 et consid&eacute;rablement am&eacute;lior&eacute;e depuis.&nbsp;<span>Pour obtenir Hue navigateur HBase, t</span><span>&eacute;l</span><span>&eacute;charger</span><span>&nbsp;Hue</span><span>&nbsp;</span>[nightly.cloudera.com/cdh4][1]<span>&nbsp;</span><span>ou construisez le directement &agrave; partir de github:&nbsp;</span><https://github.com/cloudera/hue><span>.</span>

Pr&eacute;-requis avant de commencer:

1.&nbsp;Avoir Hue construit ou install&eacute;

2.&nbsp;Avoir HBase et Thrift service 1 lanc&eacute; (Thrift peut &ecirc;tre configur&eacute; &agrave; travers Cloudera Manager ou&nbsp;<a href="http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH4/latest/CDH4-Installation-Guide/cdh4ig_topic_20_5.html#topic_20_5_4_unique_1" target="_blank" rel="noopener noreferrer">manuellement</a>)

3.&nbsp;Configurez votre liste de clusters HBase dans&nbsp;<a href="https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L467" target="_blank" rel="noopener noreferrer">hue.ini</a>&nbsp;pour pointer vers le Port/ IP de&nbsp;<span>Thrift</span>

Dans cette vid&eacute;o, nous d<span>&eacute;monstons</span><span>&nbsp;deux principales caract&eacute;ristiques de cette application. Let's go!</span></p>

{{< youtube jmcwYCxSwq0 >}}

## SmartView

Le SmartView est la vue principale.&nbsp;<span>Sur le c&ocirc;t&eacute; gauche se trouvent les row keys et au-dessus des rows une liste de contr&ocirc;les apparait sur la droite.&nbsp;Cliquez sur une ligne pour la s&eacute;lectionner, et une fois s&eacute;lectionn&eacute;, vous pouvez effectuer des op&eacute;rations de traitement par lots, des tris de colonne, ou faire n'importe quelle quantit&eacute; d'op&eacute;rations de base de donn&eacute;es standard.&nbsp;Pour explorer une rang&eacute;e, simplement d&eacute;filer vers la droite. La ligne et ses cellules est charg</span><span>&eacute;e dynamiquement</span><span>&nbsp;jusqu'&agrave; la fin afin d'etre permformante.</span>

&nbsp;

### Ajout de donn&eacute;es

Pour remplir initialement une table, vous pouvez ins&eacute;rer une nouvelle ligne ou faire transfert group&eacute; CSV / TSV / etc. ou entrer des donn&eacute;es dans directement dans votre table.

<img alt="image" height="191px;" src="https://lh4.googleusercontent.com/rSmhp0hTq4xtod8SsoIn1A8tp7omHB46j0xtpnmtOQAHzn1PHw1C0rN7Yq8CBq0WOeSh_GVfFWB1P0mKsGGWIpAnGr-mxxJRIR3uW4exevkS5_mKBG0xIbJW" width="441px;" />

Sur le c&ocirc;t&eacute; droit de suite est un signe &laquo;+&raquo; qui vous permet d'ins&eacute;rer des colonnes dans votre ligne.<img alt="image" height="68px;" src="https://lh3.googleusercontent.com/2ag5vH82l_6FyCmlBHnQUYCQ8qxsKVQTRoBU_l8oSErvO_4FWKyTyAP5MaZejkLNOy2SQVSNjo47Kq_c2pQB1t67nFB24npZVmONUf3MVivNly7HJutVS7rM" width="800px;" /><img alt="image" height="309px;" src="https://lh4.googleusercontent.com/3aMhyC8qDYdNf98Ge8qbD2EPXzCiL62lCWxHpzhfiYfZPj1F-nAgu3IhbuDYQpTVz1OCqaMDC1WDZ617YfiTsZDafbhHjXufv_f9yyXJbk95fMLNlywLZkHS" width="616px;" /></p>

### Mutation des donn&eacute;es

Pour modifier une cellule, il suffit de cliquer pour modifier directement dans la cellule:

<img alt="image" height="177px;" src="https://lh4.googleusercontent.com/ADTmywVLvEGPordZoEdsOIFkzCWlgc6lG6hrQdtAzT74nHgXqmyto4tPEqqrNmwk0pu709EnP_VIPAgvFPhlPT7NYSDj4LCbApRmw1z-mPyad2jMehWXiZAb" width="290px;" />

Si vous avez besoin de plus de contr&ocirc;le ou de donn&eacute;es relatives &agrave; votre cellule, cliquez sur "Full Editor".

<img alt="image" height="639px;" src="https://lh4.googleusercontent.com/irYJEB6muPCT5Oj3x-LJvMZIhSskXJhIJUsnYL00VpaoYKNTI8NnL09WsmzkxuryFWQpETnUb6EfRkT3ZrrTu7-yAXRDmDCG940Ssh-wbJhaGYt3Sj4txn4T" width="620px;" />

Dans l'&eacute;diteur complet, vous pouvez consulter l'historique des cellules ou t&eacute;l&eacute;charger les donn&eacute;es binaires dans la cellule.&nbsp;Les donn&eacute;es binaires de certains types MIME sont d&eacute;tect&eacute;s, ce qui signifie que vous pouvez visualiser et &eacute;diter des images, des fichiers PDF, JSON, XML et d'autres types directement dans votre navigateur!

<img alt="image" height="371px;" src="https://lh5.googleusercontent.com/N5MqnAhIPQ5D7KSU-ulHTLS0mGFZqC22ciwKGeWhntzpYx4bvqCSvcTc3xCYfCCP6HuxNTr7FlEVMowbSIJ_1nOt36wOXzNpvC-Bhy3gRXve4rIS-Ei6t_By" width="635px;" />

&nbsp;

Planant au-dessus d'une cellule r&eacute;v&egrave;le &eacute;galement certains autres contr&ocirc;les (tels que le bouton de suppression ou l'horodatage).&nbsp;Cliquez sur le titre pour s&eacute;lectionner quelques et effectuer des op&eacute;rations de traitement par lots:

<img alt="image" height="153px;" src="https://lh3.googleusercontent.com/ECcsG6M0zGESG4vuHO8KvgsxrGPbZ5cEhbFxjq2uPhgKzUS-8eTaPq3W2P-rSm13fLxEnEMJY1yFJ8pb2IBmy2KwhGgdFjqQUOTQhQV0sWsxnPFPxpjvoe3T" width="497px;" />

Si vous avez besoin de quelques exemples de donn&eacute;es pour d&eacute;marrer et explorer, consultez ce tutoriel: <a href="http://gethue.tumblr.com/post/58181985680/hadoop-tutorial-how-to-create-example-tables-in-hbase" target="_blank" rel="noopener noreferrer">cr</a><span>&eacute;</span><a href="http://gethue.tumblr.com/post/58181985680/hadoop-tutorial-how-to-create-example-tables-in-hbase" target="_blank" rel="noopener noreferrer">er des tables dans HBase</a><span>.</span></p>

### Barre de Recherche intelligente

Le "Barre de Recherche intelligente" est un outil sophistiqu&eacute; qui vous aide dans votre recherche de donn&eacute;es.&nbsp;La barre prend en charge un certain nombre d'op&eacute;rations.&nbsp;Les plus &eacute;l&eacute;mentaires comprennent la recherche et filtrer des colonnes.&nbsp;Ici, je suis s&eacute;lectionne deux lignes avec:

<pre class="code">domain.100, domain.200</pre>

<img alt="image" height="339px;" src="https://lh4.googleusercontent.com/2swltMjM0iwMfsN5oL4CAGJvg_2ZEow_swIfUbUqfugC6WfwY7zSlCBeejTTH9u7ixy5w01KKJv4YEoh3ipGTQQrm0PZGgRxXyuqlD4XKS39w3NMVxSHGrx5" width="705px;" />

Apres avoir soumis une requ&ecirc;te, les deux lignes que je cherchais apparaissent.&nbsp;Si je veux r&eacute;cup&eacute;rer les lignes apr&egrave;s l'un d'eux, je dois faire un scan.&nbsp;C'est aussi simple que d'&eacute;crire un &laquo;+&raquo; suivi par le nombre de lignes que vous souhaitez chercher.&nbsp;En tapant:

<pre class="code">domain.100, domain.200 +5</pre>

HBase Browser &eacute;cup&egrave;re domain.100 et domain.200 suivi des 5 prochaines lignes.&nbsp;Si jamais vous &ecirc;tes confus au sujet de vos r&eacute;sultats, vous pouvez regarder en bas et la barre de requ&ecirc;te et aussi cliquer pour modifier votre requ&ecirc;te.

Le Smart Search prend &eacute;galement en charge le filtrage de colonne.&nbsp;Sur chaque ligne, je peux sp&eacute;cifier les colonnes ou les familles sp&eacute;cifiques que je veux r&eacute;cup&eacute;rer.&nbsp;Avec:

<pre class="code">domain.100 [column_family:]&nbsp;&nbsp;&nbsp;</pre>

Je peux choisir une famille unique, ou des colonnes de diff&eacute;rentes familles comme ceci:

<pre class="code">domain.100 [family1:, family2:, famille3: column_a]</pre>

Faire cela va limiter mes r&eacute;sultats les colonnes sp&eacute;cifi&eacute;es.&nbsp;Si vous souhaitez restreindre les familles de colonnes seulement, le m&ecirc;me effet peut &ecirc;tre obtenu avec les filtres sur le droit.&nbsp;Il suffit de cliquer pour activer un filtre. &nbsp;

Enfin, nous allons essayer certains filtres de colonne plus complexes.&nbsp;Je peux interroger des colonnes:

<pre class="code">domain.100 [column_a]</pre>

Cela va multiplier ma requ&ecirc;te sur toutes les familles de la colonne.&nbsp;Je peux aussi faire des pr&eacute;fixes et des scans:

<pre class="code">&nbsp;&nbsp;&nbsp; domain.100 [famille: pr&eacute;fixe * +3]</pre>

Cela va me chercher toutes les colonnes qui commencent par le pr&eacute;fixe \* dans la limite de 3 r&eacute;sultats.&nbsp;Enfin, je peux filtrer sur une plage:

<pre class="code">domain.100 [famille: column1 &agrave; column100]</pre>

Cela va me chercher toutes les colonnes de la &laquo;famille:&laquo; qui sont lexicographique> = column1 mais <= column100.&nbsp;La premi&egrave;re colonne ("column1") doit &ecirc;tre une colonne valide, mais la second peut juste &ecirc;tre une ligne de texte pour la comparaison.

Le Smart Search prend &eacute;galement en charge le filtrage sur les lignes pr&eacute;fix<span>&eacute;</span><span>es.&nbsp;Pour s&eacute;lectionner une ligne pr&eacute;fix&eacute;e, il suffit de taper la cl&eacute; de la ligne suivie par une &eacute;toile \*.&nbsp;Le pr&eacute;fixe doit &ecirc;tre soulign&eacute; comme n'importe quel autre mot cl&eacute; searchbar.&nbsp;Une analyse de pr&eacute;fixe est effectu&eacute;e exactement comme un scan r&eacute;gulier, mais avec une rang&eacute;e pr&eacute;fix&eacute;e.</span></p>

<pre class="code">domain.10 * +10</pre>

Enfin, comme une nouvelle fonctionnalit&eacute;, vous pouvez &eacute;galement profiter pleinement du&nbsp;[filtrage HBase][2], en tapant votre cha&icirc;ne de filtre entre accolades.&nbsp;HBase Browser autocompletes vos filtres pour vous afin que vous n'avez pas &agrave; regarder vers le haut &agrave; chaque fois.&nbsp;Vous pouvez appliquer des filtres &agrave; des lignes ou des scans.

<pre class="code">domain.1000 {ColumnPrefixFilter ('100-') ET ColumnCountGetFilter (3)}</pre>

Ce poste ne couvre que quelques fonctions de base de la Smart Search.&nbsp;Vous pouvez profiter du langage d'interrogation en se r&eacute;f&eacute;rant au menu d'aide lors de l'utilisation de l'application.&nbsp;Il s'agit notamment de pr&eacute;fixe de colonne, colonnes, plage de colonnes, etc. Rappelez-vous que si vous avez besoin d'aide avec la barre de recherche, vous pouvez utiliser le menu d'aide qui s'affiche lors de la frappe, qui proposera des prochaines &eacute;tapes pour compl&eacute;ter votre requ&ecirc;te.</p>

## Et voila!

N'h&eacute;sitez pas &agrave; essayer l'application &agrave;&nbsp;[gethue.com][3].&nbsp;Faites-nous savoir ce que vous pensez sur le&nbsp;[groupe d'utilisateurs de Hue][4]&nbsp;!

Les futures fonctionnalit&eacute;s pr<span>&eacute;vues sont</span><span>:&nbsp;</span><span>support de&nbsp;</span><span>Thrift 2, la s&eacute;curit&eacute; Kerberos et le chargement de donn&eacute;es group&eacute;es!</span>

[1]: http://nightly.cloudera.com/cdh4/
[2]: denied:about:blank
[3]: https://gethue.com/
[4]: https://groups.google.com/a/cloudera.org/forum/#!forum/hue-user
