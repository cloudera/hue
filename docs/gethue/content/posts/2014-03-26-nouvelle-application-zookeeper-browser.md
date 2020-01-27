---
title: 'Nouvelle application: ZooKeeper Browser!'
author: admin
type: post
date: 2014-03-26T06:44:27+00:00
url: /nouvelle-application-zookeeper-browser/
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
  - left-sidebar
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

<p id="docs-internal-guid-63af2251-71ae-f7cf-e3d8-973b2294f38b">
  Bonjour les amoureux des animaux, dans <a href="http://gethue.tumblr.com/post/62087732649/hue-3-and-the-new-sqoop-and-zookeeper-apps-are-out">Hue 3</a> , une nouvelle amélioration a été ajoutée afin de rendre <a href="http://zookeeper.apache.org/">Apache Zookeeper</a> plus facile à utiliser: ZooKeeper Browser.
</p>

L'application n'est pas totalement nouvelle: il s'agit de l'upgrade de Hue 1 à Hue 3 de l' [interface utilisateur ZooKeeper][1] faite par Andrei lors de son Google Summer of Code, il ya 3 ans.

{{< youtube jvlKiZYf9Ys >}}

Les deux principales caractéristiques sont:

- Annonce des stats et des clients du cluster ZooKeeper
- Navigation et l'édition de la hiérarchie des ZNode

ZooKeeper Browser nécessite la [ZooKeeper REST][2] service. Voici comment le configurer:

D'abord obtenir et construire ZooKeeper:

<pre class="code">git clone <a href="https://github.com/apache/zookeeper">https://github.com/apache/zookeeper</a>
cd zookeeper
fourmis
BuildFile: / home / teinte / développement / soigneur / build.xml

initialisation:
    [mkdir] Created dir: / home / teinte / développement / zookeeper / construire / classes
    [mkdir] dir Crée: / home / teinte / développement / soigneur / build / lib
    [mkdir] Crée dir: / home / teinte / développement / soigneur / build / paquet / lib
    [mkdir] Crée dir: / home / teinte / développement / soigneur / build / test / lib

...</pre>

Puis démarrer le service REST:

<pre class="code">cd src / contrib / reste
nohup ant run &</pre>

Si ZooKeeper et le service REST ne sont pas sur la même machine que Hue, mettre à jour les [paramètres Hue][3] et spécifier les noms d'hôte et les ports corrects:

<pre class="code">[Soigneur]

  [[groupes]]

    [[[par défaut]]]
      # ensemble de Zookeeper. Comma liste de Host / Port séparé.
      # par exemple localhost: 2181, localhost: 2182, localhost: 2183
      # # host_ports = localhost: 2181

      # L'URL du service REST contrib
      # # rest_url = http://localhost:9998</pre>

Et voilà, openez [Navigateur ZooKeeper][4] !

Comme d'habitude n'hésitez pas à commenter sur le [groupe de message][5] ou sur [@gethue][6] !

[1]: https://github.com/andreisavu/hue/tree/zookeeper-browser/
[2]: https://github.com/apache/zookeeper/tree/trunk/src/contrib/rest
[3]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L591
[4]: http://127.0.0.1:8888/zookeeper/
[5]: http://groups.google.com/a/cloudera.org/group/hue-user
[6]: http://twitter.com/gethue
