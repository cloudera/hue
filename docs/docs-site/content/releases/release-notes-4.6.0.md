---
title: "4.6.0"
date: 2019-12-05T18:28:08-07:00
draft: false
weight: -4050
tags: ['skipIndexing']
---

## Hue v4.6.0, released December 5th 2019

Hue is an open source SQL Cloud Assistant for developing and accessing [Databases & Data Warehouses](https://docs.gethue.com/administrator/configuration/connectors/)/Data Apps and collaboring: http://gethue.com


### Summary

The focus of this release was to keep building on top of 4.5 and modularize the tech stack, improve SQL integrations and prepare major upcoming features of Hue 5. In particular now:

* Python 3 support can be tested
* There is a new version of [gethue.com](gethue.com) and the content of [docs.gethue.com](docs.gethue.com) was revamped
* The new version of the Editor with multi execution contexts and more robustness is 66% done
* Build your own or improve [SQL parsers with highlighter](https://docs.gethue.com/developer/parsers/)

Read the complete list of improvements on [Hue 4.6 is out!](http://gethue.com/hue-4-6-and-its-improvements-are-out/).


### Notable Changes

* SQL
  * Apache Hive Tez improvements
  * Apache Hive LLAP improvements
  * Autocompletes
    * Tutorial on how to [improve/create a new SQL parser](https://docs.gethue.com/developer/parsers/) with [Highlighter](/how-to-improve-or-add-your-own-sql-syntax-highlighter/)
    * Skeletons of dedicated parsers for Apache Druid, Phoenix, Elastic Serch, Presto, KSQL, Calcite are present
  * Primary Keys, Partition Keys icons showing in the assists (Read more...)[/2019-11-13-sql-column-assist-icons/]
* Collaboration
  * The Sharing icons as well as sharing action are now showing-up in left assistant
  * Copy result to Clipboard now properly keeps the table formatting
* Cloud
  * [Tracing calls](/introducing-request-tracing-with-opentracing-and-jaeger-in-kubernetes/)
  * [Retrieving and searching Logs](/collecting-hue-metrics-with-prometheus-in-kubernetes/)
  * [Collecting health and performance Metrics](/collecting-and-querying-hue-logs-with-fluentd-in-kubernetes/)
  * [Azure ADLS v2 / ABFS v1](/integration-with-microsoft-azure-data-lake-store-gen2/) has been integrated
* Infra
  * Python 3: support is making progress and now can be beta tested. `py3-ci` [CI branch](https://circleci.com/gh/cloudera/hue/tree/py3-ci), how to compile it and send feedback:
  ```
  export PYTHON_VER=python3.6
  make apps
  ```
  * Javascript testing switched to Jest and now supports headless
  * [docs.gethue.com](docs.gethue.com) has been revamped
* Bugs
  * The erratic behaviour of the horizontal result scrollbar in the SQL Editor has been fixed
  * Several Dashboard layout issues and IE 11 support fixes
  * [HUE-8727](https://issues.cloudera.org/browse/HUE-8727) Prevent chrome autofill in the assist documents


### Compatibility

Runs on CentOS versions 6.8+, Red Hat Enterprise Linux (RHEL 6, 7), and Ubuntu 16.04 and 18.04.

Tested with CDH6 and CDP1. Specifically:

- Hadoop 3.0
- Hive 2.1 / 3.0
- Oozie 5.0
- HBase 2.0
- Pig 0.17
- Impala 3.0
- Solr 7.4
- Spark 2.2

Other versions should work, but not tested.


Supported Browsers:

Hue works with the two most recent versions of the following browsers.

* Chrome
* Firefox LTS
* Safari
* Internet Edge



Runs with Python 2.7+. 3.6+ is getting ready.

Note: CentOS 6 and RHEL 6 require EPEL python 2.7 package.


### List of 666+ Commits

* 8151b7c82c [HUE-8947](https://issues.cloudera.org/browse/HUE-8947) [docs] Perform 4.5 release
* ce7362e32e [HUE-8744](https://issues.cloudera.org/browse/HUE-8744) [k8s] Add cron jobs for running the email stats command


### Contributors

This Hue release is made possible thanks to the contribution from:

* Aaron Newton
* Aaron Peddle
* Aaron T. Myers
* abec
* Abraham Elmahrek
* Aditya Acharya
* Adrian Yavorskyy
* aig
* airokey
* Alex Breshears
* Alex Newman
* Alex (posi) Newman
* alheio
* alphaskade
* Ambreen Kazi
* Amit Kabra
* Andrei Savu
* Andrew Bayer
* Andrew Yao
* Andy Braslavskiy
* Ann McCown
* antbell
* Antonio Bellezza
* arahuja
* Ashu Pachauri
* Atupal
* Avindra Goolcharan
* bcwalrus
* bc Wong
* Ben Bishop
* Ben Gooley
* Ben White
* Bhargava Kalathuru
* Bruce Mitchener
* Bruno Mahé
* bschell
* bwang
* cconner
* Chris Conner
* Chris Stephens
* Christopher Conner
* Christopher McConnell
* Christopherwq Conner
* cmconner156
* Craig Minihan
* cwalet
* Daehan Kim
* dbeech
* denniszag
* dependabot[bot]
* Derek Chen-Becker
* Diego Sevilla Ruiz
* Dominik Gehl
* Eli Collins
* Enrico Berti
* Erick Tryzelaar
* Ewan Higgs
* fatherfox
* gdgt
* Gilad Wolff
* grundprinzip
* Grzegorz Kokosiński
* Guido Serra
* happywind
* Harsh
* Harsh J
* Hector Acosta
* Henry Robinson
* hueadmin
* Igor Wiedler
* ihacku
* Ilkka Turunen
* Istvan
* Ivan Dzikovsky
* Ivan Orlov
* Jack McCracken
* Jaguar Xiong
* Jakub Kukul
* Jarcek
* jdesjean
* Jean-Francois Desjeans Gauthier
* jeff.melching
* Jenny Kim
* jheyming
* jkm
* Joe Crobak
* Joey Echeverria
* Johan Ahlen
* Johan Åhlén
* Jon Natkins
* Jordan Moore
* Josh Walters
* Karissa McKelvey
* Kevin Wang
* Khwunchai Jaengsawang
* Kostas Sakellis
* krish
* Lars Francke
* Li Jiahong
* linchan-ms
* Linden Hillenbrand
* linwukang
* Luca Natali
* Luke Carmichael
* lvziling
* maiha
* Marcus McLaughlin
* Mariusz Strzelecki
* Martin Traverso
* Mathias Rangel Wulff
* Matías Javier Rossi
* Maulik Shah
* Max T
* Michael Prim
* Michal Ferlinski
* Michalis Kongtongk
* MoA
* Mobin Ranjbar
* motta
* mrmrs
* Mykhailo Kysliuk
* Nicolas Fouché
* Nicolas Landier
* NikolayZhebet
* Olaf Flebbe
* Oli Steadman
* OOp001
* Oren Mazor
* oxpa
* Pala M Muthaia Chettiar
* Patricia Sz
* Patrick Carlson
* Patrycja Szabłowska
* pat white
* Paul Battaglia
* Paul McCaughtry
* peddle
* Peter Slawski
* Philip Zeyliger
* Piotr Ackermann
* pkuwm
* Prachi Poddar
* Prakash Ranade
* Prasad Mujumdar
* Qi Xiao
* rainysia
* raphi
* Rentao Wu
* Renxia Wang
* Rick Bernotas
* Ricky Saltzer
* robrotheram
* Romain
* Romain Rigaux
* Roman Shaposhnik
* Roohi
* Roohi Syeda
* Rui Pereira
* Sai Chirravuri
* Santiago Ciciliani
* Scott Kahler
* Sean Mackrory
* Shahab Tajik
* Shawarma
* Shawn Van Ittersum
* shobull
* Shrijeet
* Shrijeet Paliwal
* Shuo Diao
* Siddhartha Sahu
* Simon Beale
* Simon Whittaker
* sky4star
* spaztic1215
* Stefano Palazzo
* Stephanie Bodoff
* Suhas Satish
* TAKLON STEPHEN WU
* Tamas Sule
* Tatsuo Kawasaki
* Taylor Ainsworth
* Thai Bui
* thinker0
* Thomas Aylott
* Thomas Poepping
* Tianjin Gu
* tjphilpot
* todaychi
* Todd Lipcon
* Tom Mulder
* travisle22
* Vadim Markovtsev
* van Orlov
* vinithra
* voyageth
* vybs
* Wang, Xiaozhe
* Weixia
* Weixia Xu
* William Bourque
* wilson
* Word
* Xavier Morera
* Xhxiong
* Xiao Kang
* Xingang Zhang
* xq262144
* Ying Chen
* Yixiao Lin
* Yoer
* Yuriy Hupalo
* ywheel
* Zachary York
* Zach York
* Zhang Bo
* Zhang Ruiqiang
* zhengkai
* Zhihai Xu
* z-york
* 小龙哥
* 白菜
* 鸿斌
