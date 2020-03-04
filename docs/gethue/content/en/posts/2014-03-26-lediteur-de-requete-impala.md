---
title: L’éditeur de requête Impala
author: admin
type: post
date: 2014-03-26T06:47:28+00:00
url: /lediteur-de-requete-impala/
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

Dans les &eacute;pisodes pr&eacute;c&eacute;dents, nous avons pr&eacute;sent&eacute; comment planifier des workflows avec les&nbsp;[coordonnateurs de Oozie][1].&nbsp;Voyons maintenant &nbsp;un moyen rapide pour interroger des donn&eacute;es avec Impala.

<p id="docs-internal-guid-40e7f13f-6181-fb3b-54b1-99253b9abffe">
  Hue,&nbsp;marche avec&nbsp;<a href="https://github.com/cloudera/impala">Impala</a>&nbsp;depuis sa premi&egrave;re version et apporte des requ&ecirc;tes interactives rapides au sein de votre navigateur.&nbsp;Si vous n'etes pas familier avec&nbsp;<a href="http://blog.cloudera.com/blog/2012/10/cloudera-impala-real-time-queries-in-apache-hadoop-for-real/">Impala</a>&nbsp;, nous vous conseillons de jete un oeil a la documentation du plus rapide&nbsp;<a href="http://www.cloudera.com/content/support/en/documentation/cloudera-impala/cloudera-impala-documentation-v1-latest.html">moteur SQL</a>&nbsp;pour Hadoop.
</p>

# Impala App

La plupart du SQL de Hive est compatible avec Impala et nous allons comparer les requ&ecirc;tes d'[un &eacute;pisode][2]&nbsp;precedent avec les applications Impala et Hive.&nbsp;Notez que cette comparaison n'est pas 100% scientifique, mais elle montre ce qui se passerait en pratique.</p>

{{< youtube FwcVA_pgmNY >}}

Utiliser Impala &agrave; travers l'application de Hue est plus facile &agrave; bien des &eacute;gards que de l'utiliser &agrave; travers la ligne de commande du impala-shell.&nbsp;Par exemple, les noms de tables, bases de donn&eacute;es, des colonnes, des fonctions int&eacute;gr&eacute;es sont auto-completable et la coloration syntaxique montre les fautes de frappe potentielles dans vos requ&ecirc;tes.&nbsp;Plusieurs requ&ecirc;tes ou une partie s&eacute;lectionn&eacute;e d'une requ&ecirc;te peut &ecirc;tre ex&eacute;cut&eacute;e &agrave; partir de l'&eacute;diteur.&nbsp;Les requ&ecirc;tes param&eacute;tr&eacute;es sont pris en charge et l'utilisateur sera invit&eacute; a saisir des valeurs au moment de la soumission.&nbsp;Les requ&ecirc;tes Impala peuvent &ecirc;tre sauvegard&eacute;s et partag&eacute;s entre les utilisateurs ou supprim&eacute;es, puis restaur&eacute;es &agrave; partir de d&eacute;chets en cas d'erreurs.</p>

Impala utilise le m&ecirc;me Metastore de Hive afin que vous puissiez parcourir les tables avec le&nbsp;[Metastore Browser][3]&nbsp;.&nbsp;Vous pouvez &eacute;galement choisir une base de donn&eacute;es avec une liste d&eacute;roulante dans l'&eacute;diteur.&nbsp;Apr&egrave;s la pr&eacute;sentation, les progr&egrave;s et les journaux sont signal&eacute;s et vous pouvez naviguer sur le r&eacute;sultat avec d&eacute;filement infini ou t&eacute;l&eacute;charger les donn&eacute;es depuis votre navigateur.

# Comparaison de vitesse

Commen&ccedil;ons par les exemples de Hue car ils sont facilement accessibles.&nbsp;Ils sont tr&egrave;s petits mais montrent la vitesse de l'&eacute;clair d'Impala et l'inefficacit&eacute; de la s&eacute;rie de MapReduces cr&eacute;&eacute;s par Hive.

Assurez-vous que les exemples Hive et Impala soient install&eacute;s dans Hue puis dans chaque application, allez dans &laquo;&nbsp;Requ&ecirc;tes enregistr&eacute;es&nbsp;&raquo;, copier la requ&ecirc;te 'Sample: Top salaries &raquo; et soumettez la.

Ensuite, nous revenons &agrave; nos donn&eacute;es de Yelp.&nbsp;Prenons la requ&ecirc;te de&nbsp;[l'&eacute;pisode un][2]&nbsp;et ex&eacute;cuter la dans les deux applications:

<pre class="code">SELECT r.business_id, nom, SUM (froid) AS fra&icirc;cheur
de l'examen r JOIN affaires b
ON (r.business_id = b.business_id)
lorsque des cat&eacute;gories like '%% Restaurants &raquo;
ET `date` = '$ Date'
GROUP BY r. business_id, nom
ORDER BY fra&icirc;cheur DESC
LIMIT 10
</pre>

&nbsp;

Encore une fois, vous pouvez voir les avantages de l'Impala grace a&nbsp;[son l'architecture et optimisation][4]&nbsp;.

&nbsp;

# Conclusion

Ce message d&eacute;crit comment Impala permet une analyse de donn&eacute;es interactive et plus productif que le batch de Hive. Les r&eacute;sultats reviennent vite, et dans notre cas de donn&eacute;es de Yelp, instantan&eacute;ment.&nbsp;Impala et Hue combin&eacute;s sont une recette pour l'analyse rapide avec Hadoop.&nbsp;En outre, l'[API Python][5]&nbsp;de Hue&nbsp;peut aussi &ecirc;tre r&eacute;utilis&eacute;e si vous voulez construire votre propre client.</p>

La&nbsp;[VM de d&eacute;mo de Cloudera][6]&nbsp;avec ses tutoriels Hadoop est une excellente fa&ccedil;on de commencer avec Impala et Hue.&nbsp;Un prochain blog post d&eacute;crira comment utiliser les formats de fichiers les plus efficaces dans l'Impala.</p>

Comme d'habitude, n'h&eacute;sitez pas &agrave; commenter sur la&nbsp;[mailing list][7]&nbsp;ou sur la Twiter&nbsp;[@gethue][8]!

[1]: http://gethue.tumblr.com/post/61597968730/hadoop-tutorials-ii-3-schedule-hive-queries-with
[2]: http://gethue.tumblr.com/post/60376973455/hadoop-tutorials-ii-1-prepare-the-data-for-analysis
[3]: http://gethue.tumblr.com/post/56804308712/hadoop-tutorial-how-to-access-hive-in-pig-with
[4]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/Impala/latest/Installing-and-Using-Impala/ciiu_concepts.html
[5]: http://gethue.tumblr.com/post/49882746559/tutorial-executing-hive-or-impala-queries-with-python
[6]: https://ccp.cloudera.com/display/SUPPORT/Cloudera+QuickStart+VM
[7]: http://groups.google.com/a/cloudera.org/group/hue-user
[8]: https://twitter.com/gethue
