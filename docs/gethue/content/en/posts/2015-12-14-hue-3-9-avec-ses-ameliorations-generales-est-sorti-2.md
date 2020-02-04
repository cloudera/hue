---
title: Hue 3.9 avec ses améliorations générales est sorti!
author: admin
type: post
date: 2015-12-14T13:19:28+00:00
url: /hue-3-9-avec-ses-ameliorations-generales-est-sorti-2/
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
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
categories:


---
Salut Big Data aficionados,

&nbsp;

L'équipe Hue est fière et remercie tous les contributeurs de Hue 3.9! [<img src="https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png" />][1]

L'objectif de cette nouvelle version a été d'améliorer l'expérience utilisateur générale (pas de nouvelle application ont été ajoutés) et la stabilité. Plus de [700 commits][2] depuis [3.8][3] ont été fait, en particulier sur le Notebook et Spark Job Server! Allez télécharger la [nouvelle version][4] et essayer la un coup!

<p style="text-align: center;">
  <a class="sf-button standard accent standard  dropshadow" style="color: #fff!important; font-size: 200%;" title="Click to download the tarball release" href="https://cdn.gethue.com/downloads/releases/3.9.0/hue-3.9.0.tgz" target="_blank" rel="noopener noreferrer"><br /> <span class="text">Télécharger</span><br /> </a>
</p>

Vous trouverez ci-dessous une description détaillée de ce qui est a été amélioré. Pour la list complète des changements, consultez les [notes de version][5].

&nbsp;

### Tutoriels

[Exploration des données d'utilisateur de vélo de San Francisco avec un tableau de bord dynamique][6]

[Construire en temps réel un tableau de bord de Tweets avec Solr et Spark][7]

&nbsp;

### Les principales améliorations

&nbsp;

**Spark (beta)**

[<img class="aligncenter wp-image-2984" src="https://cdn.gethue.com/uploads/2015/08/notebook-1024x505.png" />][8]

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Refonte de l'interface utilisateur Notebook
    </li>
    <li class="listitem">
      Support de la fermeture de sessions et spécification de ses propriétés
    </li>
    <li class="listitem">
      Support pour Spark 1.3, 1.4, 1.5
    </li>
    <li class="listitem">
      Impersonation de l'utilisateur
    </li>
    <li class="listitem">
      Support du shell R
    </li>
  </ul>

  <p>
    Pour en en savoir plus, voir les posts sur <a href="https://gethue.com/spark-notebook-and-livy-rest-job-server-improvements/">Spark Notebook</a> et la récente présentation de <a href="https://gethue.com/big-data-scala-by-the-bay-interactive-spark-in-your-browser/">Livy le Spark REST Job Server</a>.
  </p>
</div>

&nbsp;

**Recherche**

[<img class="aligncenter wp-image-2942" src="https://cdn.gethue.com/uploads/2015/08/search-full-mode-1024x504.png" />][9]

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Filtrage en direct lors du déplacement sur la carte
    </li>
    <li class="listitem">
      Actualisation de seulement les widgets qui ont changé, rafraîchissement toutes les N secondes disponible
    </li>
    <li class="listitem">
      Modification des documents indexés
    </li>
    <li class="listitem">
      Lien vers le document original
    </li>
    <li class="listitem">
      Importation et exportation des tableaux de bord
    </li>
    <li class="listitem">
      Partage des tableaux de bord
    </li>
    <li class="listitem">
      Sauvegarde et rechargement des définitions de la requête de recherche
    </li>
    <li class="listitem">
      Filtrage de la fenêtre de temps en mode fixe ou roulante
    </li>
    <li class="listitem">
      Support des codes de pays à 2 lettres sur la carte
    </li>
    <li class="listitem">
      Mode plein écran
    </li>
    <li class="listitem">
      <a href="https://gethue.com/enhance-search-results/">L'intégration simplifié de Moustache pour améliorer votre style de résultat</a>
    </li>
  </ul>

  <p>
    <a href="https://gethue.com/dynamic-search-dashboard-improvements-3/">Lire la suite dans ce post ...</a>
  </p>
</div>

&nbsp;

**Stabilité / performances**

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Correction de "deadlocks" / blocages pour les connexions Thrift vers Hive
    </li>
    <li class="listitem">
      Nouvelle série de tests d'intégrations
    </li>
    <li class="listitem">
      Ajouter d'options et metriques sur l'état de santé de Hue sous forme de JSON
    </li>
    <li class="listitem">
      Support de MariaDB pour RHEL7
    </li>
    <li class="listitem">
      Vérification de configuration pour confirmer que le moteur de MySql est bien InnoDB et non MyISAM
    </li>
    <li class="listitem">
      Page d'accueil plus rapide
    </li>
    <li class="listitem">
      Série de correction de bugs pour les bases de données d'Oracles et de ses migrations
    </li>
  </ul>
</div>

&nbsp;

**Sécurité**

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      La liste de chiffrement (cipher list) recommandée par Mozilla est définie par défaut
    </li>
    <li class="listitem">
      Le téléchargement de fichiers volumineux avec Kerberos HTTPFS remarche
    </li>
    <li class="listitem">
      L'ent<em>ê</em>te X-Frame-Options est spécifié pour toutes les réponses
    </li>
    <li class="listitem">
      <a href="https://gethue.com/configuring-hue-multiple-authentication-backends-and-ldap/">Support de multiples authentifications par ordre de priorité</a>
    </li>
    <li class="listitem">
      Ajout d'une option de configuration globale "ssl_validate" pour valider les certificats SSL de Hue vers les clients commen HDFS ou YARN
    </li>
    <li class="listitem">
      Par défaut, l'utilisation des cookies de session est sécurisée si HTTPS est activé
    </li>
  </ul>
</div>

&nbsp;

**Oozie**

[<img src="https://cdn.gethue.com/uploads/2015/08/ignore.png" />][10]

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Les opération des filtres de tableau de bord sont faites par Oozie
    </li>
    <li class="listitem">
      <a href="https://gethue.com/exporting-and-importing-oozie-workflows/">Intégration de l'import / export de flux de travail, des coordinateurs et des Bundles dans l'interface utilisateur</a>
    </li>
    <li class="listitem">
      Pagination des tables d'actions des coordinateurs
    </li>
    <li class="listitem">
      Mise à jour de temps d'un coordinateur directement depuis l'interface
    </li>
    <li class="listitem">
      Série d'améliorations à l'éditeur
    </li>
  </ul>

  <p>
    <a href="https://gethue.com/oozie-dashboard-improvements-in-hue-3-9/">Lire la suite dans ce post ...</a>
  </p>
</div>

&nbsp;

**SQL**

[<img class="aligncenter wp-image-2822" src="https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-29-15.44.21-1024x224.png" />][11]

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Le tableau des statistiques et termes les plus utilisés est disponibles directement depuis l'assistant
    </li>
    <li class="listitem">
      Sélection par <span class="emphasis">défaut</span> d'une base de données disponible la premiere fois
    </li>
    <li class="listitem">
      <a href="https://gethue.com/filter-sort-browse-hive-partitions-with-hues-metastore/">Offre de filtrage des partitions sur la liste de la page des partitions</a>
    </li>
    <li class="listitem">
      Les liens et noms de partitions sont maintenant toujours corrects
    </li>
    <li class="listitem">
      Les examples de donnée avec les tables partitionnées sont disponibles meme en mode "strict" de Hive
    </li>
  </ul>
</div>

&nbsp;

**HBase**

[<img class="aligncenter wp-image-2977" src="https://cdn.gethue.com/uploads/2015/08/Screenshot-2015-08-20-16.34.44-1024x491.png" alt="Capture d'écran 20/08/2015 16.34.44" width="818" height="392"  />][12]

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Téléchargement de donnée binaire dans les cellules
    </li>
    <li class="listitem">
      Une cellule peut <em>ê</em>tre vidée
    </li>
  </ul>

  <p>
    <a href="https://gethue.com/improved-hbase-cell-editor-history">Lire la suite dans ce post ...</a>
  </p>
</div>

&nbsp;

**Senbry**

[<img class="aligncenter wp-image-2991" src="https://cdn.gethue.com/uploads/2015/08/sentry-multi-cols-1024x490.png" />][13]

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Meilleur support des URI de Sentry
    </li>
    <li class="listitem">
      Support des privilèges COLONNE pour les autorisations plus fine sur les tables
    </li>
    <li class="listitem">
      Support en cas de crash de Sentry (HA)
    </li>
    <li class="listitem">
      Facilitation de la navigation entre les sections
    </li>
    <li class="listitem">
      Support de la nouvelle propriété sentry.hdfs.integration.path.prefixes HDFS-site.xml
    </li>
  </ul>
</div>

&nbsp;

**Indexeur pour Solr Search**

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Téléchargement direct des configurations sans nécessiter d'avoir la commande "solrctl" installée
    </li>
  </ul>
</div>

&nbsp;

**ZooKeeper**

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Création d'un module pour faciliter la modification des informations de ZooKeeper
    </li>
  </ul>
</div>

&nbsp;

**Pig**

[<img class="aligncenter wp-image-2902" src="https://cdn.gethue.com/uploads/2015/08/pig-editor-declare-1024x514.png" alt="pig-rédacteur déclarer" width="815" height="409"  />][14]

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Support des paramètres %default dans la présentation contextuelle de soumission de script
    </li>
    <li class="listitem">
      Ne montre plus les %parameters dans la présentation contextuelle de soumission de script
    </li>
    <li class="listitem">
      Génération automatique des crédentiels HCat
    </li>
  </ul>
</div>

&nbsp;

**Sqoop 2**

<div class="itemizedlist">
  <ul class="itemizedlist" type="disc">
    <li class="listitem">
      Support de l'authentification Kerberos
    </li>
  </ul>
</div>

&nbsp;

### Conférences

Ce fut un plaisir de présenter au Big Data Budapest Meetup,  [Big Data][15] Amsterdam, [Hadoop Summit de San Jose][16] et [Big Data][7] LA.

&nbsp;

### Nouvelles distributions

  * [Image Docker de Hue pour IBM Analytics][17]
  * [Big Data Insights IBM][18]
  * [HD3.0 Pivotal][19]
  * [Mise à jour HDP][20]

&nbsp;

### Équipe

Hummus et le yogourt étaient au menu en [Israël!][21]

&nbsp;

## **Pour la suite!**

&nbsp;

La prochaine version (3.10) se concentrera sur la version 1 du Notebook pour Spark et en ajoutant une indexation plus simple pour l'application Search de Solr.

La conception Hue 4 va également commencer avec l'objectif de devenir l'équivalent de "Excel pour Big Data". Un nouveau look, une unification de toutes les applications, des assistants pour l'ingestion des données ... vous permettra d'utiliser la plate-forme complète (Ingest, Spark, SQL, Recherche) dans une interface utilisateur unique!

&nbsp;

En avant / Onwards!

&nbsp;

Comme d'habitude merci à tous les contributeurs du projet et pour l'envoi de commentaires et de participer à la [liste utilisateur][22] et [@gethue!][23]

 [1]: https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png
 [2]: https://github.com/cloudera/hue/compare/release-3.8.0...release-3.9.0
 [3]: https://gethue.com/hue-3-8-with-an-oozie-editor-revamp-better-performances-improved-spark-ui-is-out/
 [4]: https://cdn.gethue.com/downloads/releases/3.9.0/hue-3.9.0.tgz
 [5]: http://cloudera.github.io/hue/docs-3.9.0/release-notes/release-notes-3.9.0.html
 [6]: https://gethue.com/bay-area-bikeshare-data-analysis-with-search-and-spark-notebook/
 [7]: https://gethue.com/big-data-day-la-solr-search-with-spark-for-big-data-analytics-in-action-with-hue/
 [8]: https://cdn.gethue.com/uploads/2015/08/notebook.png
 [9]: https://cdn.gethue.com/uploads/2015/08/search-full-mode.png
 [10]: https://cdn.gethue.com/uploads/2015/08/ignore.png
 [11]: https://cdn.gethue.com/uploads/2015/07/Screenshot-2015-07-29-15.44.21.png
 [12]: https://cdn.gethue.com/uploads/2015/08/Screenshot-2015-08-20-16.34.44.png
 [13]: https://cdn.gethue.com/uploads/2015/08/sentry-multi-cols.png
 [14]: https://cdn.gethue.com/uploads/2015/08/pig-editor-declare.png
 [15]: https://gethue.com/harness-the-power-of-spark-and-solr-in-hue-big-data-amsterdam-v-2-0-meeetup/
 [16]: https://gethue.com/hadoop-summit-san-jose-2015-interactively-query-and-search-your-big-data/
 [17]: https://github.com/ibmecod/bluemix-hue-filebrowser
 [18]: https://gethue.com/how-to-install-hue-3-on-ibm-biginsights-4-0-to-explore-big-data/
 [19]: https://gethue.com/install-hue-3-on-pivotal-hd-3-0/
 [20]: https://gethue.com/hadoop-hue-3-on-hdp-installation-tutorial/
 [21]: https://gethue.com/team-retreat-in-israel/
 [22]: http://groups.google.com/a/cloudera.org/group/hue-user
 [23]: https://twitter.com/gethue
