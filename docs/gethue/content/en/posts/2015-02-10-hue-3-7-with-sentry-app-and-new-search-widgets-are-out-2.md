---
title: La nouvelle version 3.7 de Hue avec l’application de Securite et de moteur de recherche est sortie!
author: admin
type: post
date: 2015-02-10T01:43:47+00:00
url: /hue-3-7-with-sentry-app-and-new-search-widgets-are-out-2/
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
Salut les Big Data Surfers!

L'équipe Hue est heureuse de délivrer Hue 3.7 et sa nouvelle [Application Sentry][1] et l'amélioration de l'[Application Search][2] !

Une [archive][3] est disponible ainsi que [la documentation][4] et les [notes de version][5]. Malgré le développement d'une nouvelle application complète, cette version est particulièrement riche en fonctionnalités. Ceci est en parti dû à tous les bons commentaires et les demandes que nous recevons!

<p style="text-align: center;">
  <a class="sf-button standard accent standard  dropshadow" style="color: #fff!important;" href="https://cdn.gethue.com/downloads/releases/3.7.1/hue-3.7.1.tgz" target="_blank" rel="noopener noreferrer"><span class="text">Télécharger la version 3.7.1</span></a>
</p>

&nbsp;

Voici une liste des principales améliorations:

**Sécurité**

[<img src="https://cdn.gethue.com/uploads/2014/10/hue-sentry-1024x541.png" />][6]

  * Nouvelle application pour [Sentry][7]
  * Edition groupée des rôles et privilèges
  * Visualisation / modification des rôles et des privilèges avec un arbre graphique
  * Support de l'équilivalent de WITH GRANT OPTION
  * Impersonation d'un utilisateur afin de valider rapidement ce qu'il peut voir
  * [Plus de détails ici ...][1] (en anglais)

&nbsp;

**Moteur de recherche**

[<img src="https://cdn.gethue.com/uploads/2014/10/hue-search-v2.1-1024x596.png"  />][8]

  * Trois nouveaux widgets
      * Carte avec degradés
      * Carte avec marqueur
      * Arbre à plusieurs niveaux
  * Visualisation de l'analyse des champs de l'index
  * Exclusion de facettes
  * [Plus de détails ici ...][2] (en anglais)

&nbsp;

**Oozie**

[<img src="https://cdn.gethue.com/uploads/2014/10/hue-oozie-1024x579.png" />][9]

  * Groupement des action Suspendre / Arrêter / Reprise du tableaux de bord
  * Tableaux de bord plus rapides
  * Reprises des coordinateurs échoués en group
  * [Plus de détails ici ...][10] (en anglais)

&nbsp;

**Job Browser**

Boutton pour arrêter des applications YARN

&nbsp;

****Explorateur de fichiers****

[<img src="https://cdn.gethue.com/uploads/2014/10/hue-fb-1024x571.png" />][11]

  * Édition des ACL de permission
  * Envoie de fichier par Drag & Drop
  * Historique de Navigation
  * Interface simplifiée
  * [Plus de détails ici ...][12] (en anglais)

&nbsp;

**HBase**

Ajout du support pour Kerberos. La prochaine étape sera l'impersonation!

&nbsp;

**Indexer**

Correction des problèmes avec Zookeeper qui pouvait ne pas pointer vers le bon Solr. L'application est toujours tres utile pour [installater les exemples][13] en un seul clic.

&nbsp;

**Hive / Impala**

[<img src="https://cdn.gethue.com/uploads/2014/10/hue-impala-charts-1024x573.png" />][14]

  * Support de l'authentication par LDAP
  * C[ryptage SSL avec HiveServer2][15]
  * Nouveaux graphiques
  * [Expiration automatique des requêtes][16]

&nbsp;

**SDK**

Nous essayons aussi de rendre le projet plus facile de développer (en anglais):

  * [Comment faires des revues de code][17]
  * [Comment exécuter les tests][18]
  * [Comment installer sur Ubuntu 14.04][19]
  * Comment configurer avec [tout Hadoop][20]

&nbsp;

&nbsp;

**Ce qui est prévu pour la suite?**

Les prochaines amélioration prévues apporteront un nouveau Editor de workflow pour Oozie, des performances plus rapides et une haute disponibilité plus facile a mettre en place (HA). Une application pour faire du Spark en Scala, Python ou SQL sera aussi une grande nouveauté!

&nbsp;

Comme d'habitude, n'hésitez pas à commenter et envoyer des commentaires sur la liste [d'utilisateur][21] ou à [@gethue][22] !

 [1]: https://gethue.com/apache-sentry-made-easy-with-the-new-hue-security-app/
 [2]: https://gethue.com/search-app-enhancements-explore-even-more-data/
 [3]: https://cdn.gethue.com/downloads/releases/3.7.1/hue-3.7.1.tgz
 [4]: http://cloudera.github.io/hue/docs-3.7.0/index.html
 [5]: http://cloudera.github.io/hue/docs-3.7.0/release-notes/release-notes-3.7.0.html
 [6]: https://cdn.gethue.com/uploads/2014/10/hue-sentry.png
 [7]: https://sentry.incubator.apache.org/
 [8]: https://cdn.gethue.com/uploads/2014/10/hue-search-v2.1.png
 [9]: https://cdn.gethue.com/uploads/2014/10/hue-oozie.png
 [10]: https://gethue.com/improved-oozie-dashboard-bulk-manipulate-your-jobs/
 [11]: https://cdn.gethue.com/uploads/2014/10/hue-fb.png
 [12]: https://gethue.com/file-browser-enhancements-hdfs-operations-made-easy/
 [13]: https://gethue.com/hadoop-tutorial-kerberos-security-and-sentry-authorization-for-solr-search-app/
 [14]: https://cdn.gethue.com/uploads/2014/10/hue-impala-charts.png
 [15]: https://gethue.com/hadoop-tutorial-ssl-encryption-between-hue-and-hive/
 [16]: https://gethue.com/hadoop-tutorial-hive-and-impala-queries-life-cycle/
 [17]: https://gethue.com/rbtools-example-how-do-easily-do-code-reviews-with-review-board/
 [18]: https://gethue.com/tutorial-how-to-run-the-hue-integration-tests/
 [19]: https://gethue.com/how-to-build-hue-on-ubuntu-14-04-trusty/
 [20]: https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/
 [21]: http://groups.google.com/a/cloudera.org/group/hue-user
 [22]: https://twitter.com/gethue
