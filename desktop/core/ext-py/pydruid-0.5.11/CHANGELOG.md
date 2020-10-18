## Change Log

### 0.5.8 (2020/01/10 19:52 +00:00)
- [#180](https://github.com/druid-io/pydruid/pull/180) [dbapi] Added ssl certificate (#180) (@TechGeekD)

### 0.5.7 (2019/10/07 20:15 +00:00)
- [#172](https://github.com/druid-io/pydruid/pull/172) [dbapi] Fixing type ordering (#172) (@john-bodley)
- [#174](https://github.com/druid-io/pydruid/pull/174) [parameters] Fix empty parameter check (#174) (@john-bodley)
- [#178](https://github.com/druid-io/pydruid/pull/178) [api] Remove duplicate line (#178) (@john-bodley)
- [#176](https://github.com/druid-io/pydruid/pull/176) Black + various pre-commit hooks (#176) (@mistercrunch)
- [#170](https://github.com/druid-io/pydruid/pull/170) Updated bound filter to latest Druid API specs (#170) (@wjdecorte)

### 0.5.6 (2019/07/04 05:54 +00:00)
- [#171](https://github.com/druid-io/pydruid/pull/171) [dbapi] Fixing pyformat parameters (#171) (@john-bodley)
- [#163](https://github.com/druid-io/pydruid/pull/163) Added http_client parameter to AsyncPyDruid class init to specify which client to use (#163) (@wjdecorte)
- [#168](https://github.com/druid-io/pydruid/pull/168) [dbapi] Fixing header description (#168) (@john-bodley)
- [#167](https://github.com/druid-io/pydruid/pull/167) Add README.md to pypi (#167) (@mistercrunch)

### 0.5.4 (2019/06/10 01:40 +00:00)
- [#146](https://github.com/druid-io/pydruid/pull/146) Add proxies support to BaseDruidClient (#146) (@jobar)
- [#165](https://github.com/druid-io/pydruid/pull/165) CHANGELOG 0.5.0 to 0.5.3 (#165) (@mistercrunch)
- [#159](https://github.com/druid-io/pydruid/pull/159) F timeout issue 140 (#159) (@wjdecorte)
- [#161](https://github.com/druid-io/pydruid/pull/161) Parse actual response body for HTTP error (#161) (@haltwise)
- [#139](https://github.com/druid-io/pydruid/pull/139) SubQueries Support (#139) (@pantlavanya)
- [#164](https://github.com/druid-io/pydruid/pull/164) Add Trove classifiers for supported Python versions. (#164) (@jezdez)

### 0.5.3 (2019/05/29 21:23 +00:00)
- [#153](https://github.com/druid-io/pydruid/pull/153) Registered lookups (#153) (@srggrs)
- [#156](https://github.com/druid-io/pydruid/pull/156) Support for search and like filters (#156) (@Makesh-Gmak)
- [#149](https://github.com/druid-io/pydruid/pull/149) Add support for Druid Basic Auth to SQLAlchemy (#149) (@donbowman)
- [#155](https://github.com/druid-io/pydruid/pull/155) [api] Adding support for headers (#155) (@john-bodley)

### pydruid-0.5.2 (2019/03/08 01:16 +00:00)
- [#150](https://github.com/druid-io/pydruid/pull/150) Improve error message (#150) (@betodealmeida)

### pydruid-0.5.1 (2019/03/05 17:11 +00:00)
- [#152](https://github.com/druid-io/pydruid/pull/152) Pass context to Druid (#152) (@betodealmeida)
- [#148](https://github.com/druid-io/pydruid/pull/148) scan query: use columns instead of dimensions (#148) (@adelcast)
- [#147](https://github.com/druid-io/pydruid/pull/147) Update console.py (#147) (@john-bodley)
- [#145](https://github.com/druid-io/pydruid/pull/145) Dummy version number for master branch + RELEASE.md docs (#145) (@mistercrunch)

### 0.5.0 (2018/11/28 06:16 +00:00)
- [#144](https://github.com/druid-io/pydruid/pull/144) [db-api] Performance improvements (#144) (@john-bodley)
- [#142](https://github.com/druid-io/pydruid/pull/142) [prompt_toolkit] Enforcing pre-2.0 (#142) (@john-bodley)
- [#141](https://github.com/druid-io/pydruid/pull/141) [console] Updating filters/keywords (#141) (@john-bodley)
- [#143](https://github.com/druid-io/pydruid/pull/143) [travis] Pinning flake8 (#143) (@john-bodley)
- [#138](https://github.com/druid-io/pydruid/pull/138) Reserve original column sequence in SQL when reading data (#138) (@xqliu)
- [#132](https://github.com/druid-io/pydruid/pull/132) [cli] add an quit/exit/bye commands (#132) (@mistercrunch)

### pydruid-0.4.4 (2018/06/21 18:25 +00:00)
- [#133](https://github.com/druid-io/pydruid/pull/133) Fix empty result (#133) (@betodealmeida)

### pydruid-0.4.3 (2018/05/18 18:22 +00:00)
- [#131](https://github.com/druid-io/pydruid/pull/131) Support hyperUnique type (#131) (@betodealmeida)
- [#127](https://github.com/druid-io/pydruid/pull/127) Implement Filtered DimensionSpecs (#127) (@jeffreythewang)

### 0.4.2 (2018/04/03 00:23 +00:00)
- [#121](https://github.com/druid-io/pydruid/pull/121) Surface HTML errors (#121) (@betodealmeida)
- [#76](https://github.com/druid-io/pydruid/pull/76) Filters extraction function (#76) (@gaetano-guerriero)
- [#119](https://github.com/druid-io/pydruid/pull/119) fix access to class name when raising connection error (#119) (@danfrankj)

### pydruid-0.4.1 (2018/02/08 00:20 +00:00)
- [#120](https://github.com/druid-io/pydruid/pull/120) Remove 'enum' package requirements (#120) (@mistercrunch)
- [#118](https://github.com/druid-io/pydruid/pull/118) Add shortcuts to CLI (#118) (@betodealmeida)
- [#117](https://github.com/druid-io/pydruid/pull/117) Small fixes (#117) (@betodealmeida)
- [#116](https://github.com/druid-io/pydruid/pull/116) Get b64encoding correct for python 2 & 3 (#116) (@boorad)

### pydruid-0.4.0 (2018/01/30 18:59 +00:00)
- [#100](https://github.com/druid-io/pydruid/pull/100) thetaSketchEstimate fix py2.* (#100) (@Dylan1312)
- [#80](https://github.com/druid-io/pydruid/pull/80) Methode for http basic auth with username and password added (#80) (@DPiontek)
- [#113](https://github.com/druid-io/pydruid/pull/113) Check if connection is closed before execute (#113) (@betodealmeida)
- [#108](https://github.com/druid-io/pydruid/pull/108) Add support for 'scan' queries (#108) (@mistercrunch)
- [#111](https://github.com/druid-io/pydruid/pull/111) Linting with flake8 (#111) (@mistercrunch)
- [#112](https://github.com/druid-io/pydruid/pull/112) Fix reserved keyword (#112) (@betodealmeida)
- [#110](https://github.com/druid-io/pydruid/pull/110) Merge druiddb into pydruid (#110) (@betodealmeida)
- [#107](https://github.com/druid-io/pydruid/pull/107) Implement pandas export for 'select' queries (#107) (@mistercrunch)
- [#106](https://github.com/druid-io/pydruid/pull/106) [py2] fix str check in parse_datasource (#106) (@mistercrunch)
- [#103](https://github.com/druid-io/pydruid/pull/103) Add a way to add context->queryid. (#103) (@lionaneesh)
- [#87](https://github.com/druid-io/pydruid/pull/87) Support for 'interval' filter (#87) (@var23rav)
- [#74](https://github.com/druid-io/pydruid/pull/74) Support for Union datasource (#74) (@RichRadics)
- [#72](https://github.com/druid-io/pydruid/pull/72) thetaSketch support (#72) (@RichRadics)
- [#77](https://github.com/druid-io/pydruid/pull/77) Add LICENSE to MANIFEST.in (#77) (@pmlandwehr)
- [#66](https://github.com/druid-io/pydruid/pull/66) __str__ returns dict (#66) (@onesuper)
- [#82](https://github.com/druid-io/pydruid/pull/82) Add columnComparison filter support (#82) (@erikdubbelboer)
- [#73](https://github.com/druid-io/pydruid/pull/73) Add new Greatest and Least post aggregators (#73) (@erikdubbelboer)
- [#84](https://github.com/druid-io/pydruid/pull/84) Add min and max aggregators for long and double (#84) (@azymnis)

### pydruid-0.3.1 (2016/12/22 21:55 +00:00)
- [#70](https://github.com/druid-io/pydruid/pull/70) Prepare for 0.3.1 release. (#70) (@gianm)
- [#68](https://github.com/druid-io/pydruid/pull/68) add quantile and quantiles post aggregators support (#68) (@hexchain)
- [#69](https://github.com/druid-io/pydruid/pull/69) query: add support for search query (#69) (@hexchain)
- [#60](https://github.com/druid-io/pydruid/pull/60) Add support for bound filter (#60) (@psalaberria002)
- [#67](https://github.com/druid-io/pydruid/pull/67) Add merge option to segment_metadata (#67) (@noppanit)
- [#62](https://github.com/druid-io/pydruid/pull/62) Bugfix when building `not` filter multiple times (#62) (@dakra)
- [#58](https://github.com/druid-io/pydruid/pull/58) Don't raise exception when filter/having/dimension is None (#58) (@dakra)
- [#53](https://github.com/druid-io/pydruid/pull/53) only import pandas when `export_pandas` gets called (#53) (@dakra)
- [#54](https://github.com/druid-io/pydruid/pull/54) Adds support for "in" filter (#54) (@se7entyse7en)
- [#57](https://github.com/druid-io/pydruid/pull/57) Add `analysisTypes` to segment metadata query (#57) (@drcrallen)
- [#55](https://github.com/druid-io/pydruid/pull/55) allow `descending` attribute in timeseries query (#55) (@dakra)

### pydruid-0.3.0 (2016/05/24 17:09 +00:00)
- [9a802a3](https://github.com/druid-io/pydruid/commit/9a802a3c45a1126fcb7961a32ef41f74543d06b3) bump version to 0.3.0 (@xvrl)
- [#50](https://github.com/druid-io/pydruid/pull/50) Add JavaScript aggregator support (#50) (@sologoub)
- [#51](https://github.com/druid-io/pydruid/pull/51) bugfix nested `and`/`or` filters inside `not` (#51) (@dakra)
- [#52](https://github.com/druid-io/pydruid/pull/52) Adding support for regex filter (#52) (@mistercrunch)
- [d0763f1](https://github.com/druid-io/pydruid/commit/d0763f1a17b324ef91d2fe6b20b2264500185e47) add `NamespaceLookupExtraction` (@dakra)
- [1bf68ae](https://github.com/druid-io/pydruid/commit/1bf68ae9f9bd99bbcbe4625c5a3a5d7bb78691f0) add `TimeFormatExtraction` (@dakra)
- [#45](https://github.com/druid-io/pydruid/pull/45) Merge pull request #45 from dakra/nested-filter-aggregates (@dakra)
- [#39](https://github.com/druid-io/pydruid/pull/39) Merge pull request #39 from DreamLab/async_support (@DreamLab)
- [166983e](https://github.com/druid-io/pydruid/commit/166983ececa9f6ea4ab242dbf39619731388886e) * added support for asynchronous client (@turu)
- [#47](https://github.com/druid-io/pydruid/pull/47) Merge pull request #47 from dakra/ne-dimension (@dakra)
- [#46](https://github.com/druid-io/pydruid/pull/46) Merge pull request #46 from dakra/or-filter (@dakra)
- [5290823](https://github.com/druid-io/pydruid/commit/5290823cbcad223fd56300487b7051835acb5be5) add __ne__ to `Dimension` so you can `filter = Dimension('dim') != val` (@dakra)
- [415d954](https://github.com/druid-io/pydruid/commit/415d954d68c9e58cb28ab393e43d92bbdf0517f9) add support for `and`,`or` filters with more then 2 values. (@dakra)
- [8b08a91](https://github.com/druid-io/pydruid/commit/8b08a91816e67724b7497fba998db9a4b89f1446) add support for nested filtered aggregators (@dakra)
- [#40](https://github.com/druid-io/pydruid/pull/40) Merge pull request #40 from se7entyse7en/dimensions_specs (@se7entyse7en)
- [#41](https://github.com/druid-io/pydruid/pull/41) Merge pull request #41 from se7entyse7en/hyperuniquecardinality_postaggregator (@se7entyse7en)
- [9b3aaad](https://github.com/druid-io/pydruid/commit/9b3aaad624e6de6185997c3c2e2660b8c21807b8) Added support for HyperUniqueCardinality (@se7entyse7en)
- [9e1ef9e](https://github.com/druid-io/pydruid/commit/9e1ef9eff193a65cce7ff53c4a96bc1930150a69) Added tests for dimensions module (@se7entyse7en)
- [382d610](https://github.com/druid-io/pydruid/commit/382d610aa18daf297ae14c918fc2f72729e2b0d1) Handled dimensions building in PyDruid client (@se7entyse7en)
- [fe0eaac](https://github.com/druid-io/pydruid/commit/fe0eaac2cffcccbe0043aa9aee2f5baf50fe73de) Added dimensions specs and some extraction functions (@se7entyse7en)
- [#38](https://github.com/druid-io/pydruid/pull/38) Merge pull request #38 from nmckoy/js-filter (@nmckoy)
- [10a8340](https://github.com/druid-io/pydruid/commit/10a8340af24eddbab955acbb304e18a24c418e1a) camel case JavaScript (@nmckoy)
- [e1604d6](https://github.com/druid-io/pydruid/commit/e1604d6219d293530e0d7bc0a869fe41f90f79a7) support javascript filter (@nmckoy)
- [#37](https://github.com/druid-io/pydruid/pull/37) Merge pull request #37 from gianm/cardinality (@gianm)
- [fa2ecf9](https://github.com/druid-io/pydruid/commit/fa2ecf9f83d0bfb01324dad6c58281e131919216) Bump version to 0.2.4 (@gianm)
- [c37b7d4](https://github.com/druid-io/pydruid/commit/c37b7d4d2620c1eccdc7d525a772dbb6869a81a0) Cardinality aggregator (@gianm)

### pydruid-0.2.3 (2015/10/25 17:23 +00:00)
- [e9d6648](https://github.com/druid-io/pydruid/commit/e9d6648bb2ac1fbbda07151f01a4ccf070a4ea14) version 0.2.3 (@xvrl)
- [#36](https://github.com/druid-io/pydruid/pull/36) Merge pull request #36 from druid-io/update-links (@druid-io)
- [4481ac5](https://github.com/druid-io/pydruid/commit/4481ac5087fff1005823a1b99805d741c63dc625) update links (@xvrl)
- [0300447](https://github.com/druid-io/pydruid/commit/03004471d0fd8b586bf6be3fff3232fa84361350) clean up .gitignore (@xvrl)
- [af4d5ec](https://github.com/druid-io/pydruid/commit/af4d5ec6cdacbb2f6e3bcd9b04df028977614d56) s/bard/broker/ (@xvrl)
- [#35](https://github.com/druid-io/pydruid/pull/35) Merge pull request #35 from se7entyse7en/filters_tests (@se7entyse7en)
- [e629e8b](https://github.com/druid-io/pydruid/commit/e629e8ba1586f443b2b4efa635ec3f808ebedddb) Fixed error raised in Filter class for invalid type (@se7entyse7en)
- [74435d2](https://github.com/druid-io/pydruid/commit/74435d223d776f6b34e267dff2e3bfe933d0f00e) Added tests for filters module (@se7entyse7en)
- [#28](https://github.com/druid-io/pydruid/pull/28) Merge pull request #28 from se7entyse7en/filtered_aggregation (@se7entyse7en)
- [8b8b138](https://github.com/druid-io/pydruid/commit/8b8b1387900521040ba166dd735f8a50174a87d4) Added tests for filtered aggregation (@se7entyse7en)
- [85bc393](https://github.com/druid-io/pydruid/commit/85bc39361390f414ff505459a4048553e24db337) Added support for filtered aggregator (@se7entyse7en)
- [#34](https://github.com/druid-io/pydruid/pull/34) Merge pull request #34 from se7entyse7en/travis_integration (@se7entyse7en)
- [#32](https://github.com/druid-io/pydruid/pull/32) Merge pull request #32 from se7entyse7en/some_tests (@se7entyse7en)
- [5b8e9fe](https://github.com/druid-io/pydruid/commit/5b8e9fefb7b5acbb1dcc224b4932dd6b6901bb8e) Added travis configuration file (@se7entyse7en)
- [261efdb](https://github.com/druid-io/pydruid/commit/261efdb6cf93eda51566e66d563414c50db8f49d) Added test_aggregators (@se7entyse7en)
- [00bb0b0](https://github.com/druid-io/pydruid/commit/00bb0b0da45ac1462ada2bfde32a4cd6f0092218) Removed unused import in test_query_utils (@se7entyse7en)
- [d6af01d](https://github.com/druid-io/pydruid/commit/d6af01db9a265ae477e143bc7f30cf4814815dd6) Fixed flake8 F403 errors in test_query_utils (@se7entyse7en)
- [deb7299](https://github.com/druid-io/pydruid/commit/deb729999bc98433f00e3b5cc171ff881f285ad7) Fixed pep8 E302 errors in test_query_utils (@se7entyse7en)
- [3e9a100](https://github.com/druid-io/pydruid/commit/3e9a1009370c00ed9dbcbe623dfb932ef8bb867f) Fixed flake8 F403 errors in test_client (@se7entyse7en)
- [c169777](https://github.com/druid-io/pydruid/commit/c169777397d3dee7d4b26e761f485523351eaacd) Added some items to .gitignore for emacs (@se7entyse7en)
- [41c1190](https://github.com/druid-io/pydruid/commit/41c1190214ed7cc5289846ace7957f514d236b98) Fixed pep8 E711 errors in test_client (@se7entyse7en)
- [c009bca](https://github.com/druid-io/pydruid/commit/c009bca263083499853fed1efd1946623fe2722d) Fixed test_client so that it doesn't fail if pandas is not installed given that it is optional (@se7entyse7en)

### pydruid-0.2.2 (2015/07/24 23:12 +00:00)
- [5636a9e](https://github.com/druid-io/pydruid/commit/5636a9eb47238ff213c982cce33fec83c8a8e182) version 0.2.2, fix pypi version conflict (@xvrl)

### pydruid-0.2.1 (2015/07/24 18:00 +00:00)
- [41ea841](https://github.com/druid-io/pydruid/commit/41ea841eb54f5b30776c6ba0bd7f414adcc002e4) update version to 0.2.1 and fix license string (@xvrl)
- [#24](https://github.com/druid-io/pydruid/pull/24) Merge pull request #24 from mistercrunch/limit_spec (@mistercrunch)
- [#21](https://github.com/druid-io/pydruid/pull/21) Merge pull request #21 from griffy/master (@griffy)
- [616a93e](https://github.com/druid-io/pydruid/commit/616a93e81488503967501ae6b799ec7f0b113005) Fix regressions introduced by support for Python 3 and add initial test coverage (@griffy)
- [97397d3](https://github.com/druid-io/pydruid/commit/97397d3ca84e1f9903752f04c06ad0375d5767c1) Adding limitSpec support to groupby query (@mistercrunch)
- [#19](https://github.com/druid-io/pydruid/pull/19) Merge pull request #19 from graphaelli/simplejson-optional (@graphaelli)
- [faccbc0](https://github.com/druid-io/pydruid/commit/faccbc00dac4cd3e9da1b27febb69d0f21e28f40) make simplejson optional, except on python < 2.6 (@graphaelli)
- [#18](https://github.com/druid-io/pydruid/pull/18) Merge pull request #18 from griffy/master (@griffy)
- [28eeae4](https://github.com/druid-io/pydruid/commit/28eeae465c22b4362dad3e77c8fcc21833b25407) Add support for Python 3 (@griffy)
- [#17](https://github.com/druid-io/pydruid/pull/17) Merge pull request #17 from mruwnik/allow_setting_of_context_options (@mruwnik)
- [f2d1a24](https://github.com/druid-io/pydruid/commit/f2d1a24e24a81286973975356c14f7f40a0d667b) Allow the setting of context properties in queries (@mruwnik)
- [#15](https://github.com/druid-io/pydruid/pull/15) Merge pull request #15 from seanv507/druid_error_output (@seanv507)
- [#14](https://github.com/druid-io/pydruid/pull/14) Merge pull request #14 from seanv507/having (@seanv507)
- [93b65be](https://github.com/druid-io/pydruid/commit/93b65bea3c1e592e94d649a97fc1a60557091f31) report druid error (@seanv507)
- [4226a66](https://github.com/druid-io/pydruid/commit/4226a66c47242348113a2882bf8090ec5e3723e5) fixed aggregation equalTo and simplified and or nesting (@seanv507)
- [92275bf](https://github.com/druid-io/pydruid/commit/92275bf64d7c3f0b4cbfb6179ecd9cf5bfa0b5d7) added having clause to groupby queries (@seanv507)
- [#13](https://github.com/druid-io/pydruid/pull/13) Merge pull request #13 from whitehats/new_query_types (@whitehats)
- [602cc04](https://github.com/druid-io/pydruid/commit/602cc04ca4e527203b34790cbe16f49817ecb4cb) queryType 'select' (@KenjiTakahashi)
- [#12](https://github.com/druid-io/pydruid/pull/12) Merge pull request #12 from davideanastasia/hyperunique (@davideanastasia)
- [090eb03](https://github.com/druid-io/pydruid/commit/090eb032884a3652affaeeb18f6ea40cc66f6db9) Add support for HyperUnique aggregator (@davideanastasia)

### pydruid-0.2.0 (2014/04/14 20:07 +00:00)
- [#10](https://github.com/druid-io/pydruid/pull/10) Merge pull request #10 from metamx/use-relative-paths (@metamx)
- [ffebcb8](https://github.com/druid-io/pydruid/commit/ffebcb89361a59d79600416ac2d6525ef06d9248) restored updated intro, with restructered heads and info on finding more examples
- [d5e84a7](https://github.com/druid-io/pydruid/commit/d5e84a7cbc8d4ce966f403d96db2cd488d53d0e4) intro now focused just on PyDruid class
- [1667132](https://github.com/druid-io/pydruid/commit/1667132f312f7507bebd53caa4e584f16d178e3b) ignoring these generated files
- [e51391a](https://github.com/druid-io/pydruid/commit/e51391a6df968ab9e43015b4e07191f99d722cb4) rm this intruder, a file specific to Mac OSX
- [4192010](https://github.com/druid-io/pydruid/commit/4192010223a86f35532c0a33ae71b01f83421b62) rm this intruder, a file specific to Mac OSX
- [af7c90f](https://github.com/druid-io/pydruid/commit/af7c90f4f600e117a807566b4deae227efb01cf4) substituting relative paths for local paths
- [752772d](https://github.com/druid-io/pydruid/commit/752772d142ee2c1999562b880b4260f8c5dcf59e) Update README.md (@dganguli)
- [f91a5dc](https://github.com/druid-io/pydruid/commit/f91a5dca2da29f02e737a793bcec8b7af4e19f50) Update README.md (@dganguli)
- [#8](https://github.com/druid-io/pydruid/pull/8) Merge pull request #8 from metamx/igalpd (@metamx)
- [c1b3423](https://github.com/druid-io/pydruid/commit/c1b3423c5f48448c2717b688fcb9fca747e37185) changed 'bard' to 'druid'
- [c4ba739](https://github.com/druid-io/pydruid/commit/c4ba739734b20ad8693ee185ae351615ad38ed74) Update README.md (@dganguli)
- [b398f45](https://github.com/druid-io/pydruid/commit/b398f45f896dac31a91bca548499286ecebc9789) Update README.md (@dganguli)
- [844047e](https://github.com/druid-io/pydruid/commit/844047e057a0e03b950e4775cadf5e54299cbbd7) Update README.md (@dganguli)
- [#7](https://github.com/druid-io/pydruid/pull/7) Merge pull request #7 from metamx/pyipyi (@metamx)
- [823c55c](https://github.com/druid-io/pydruid/commit/823c55c5af0881520e85651a02f8192b1ff55758) fix whitespace ftw
- [1fabb51](https://github.com/druid-io/pydruid/commit/1fabb518a1e14a13f5d5e403fac826e5f3a2086a) setup.cfg to make it easy to upload docs to pythonhosted.org
- [9471077](https://github.com/druid-io/pydruid/commit/9471077cdd82e9a7940e2bc062299c94d378b6a7) docs: rename pyDruid -> pydruid
- [bc625b5](https://github.com/druid-io/pydruid/commit/bc625b5acfa50f7f8d6090f22dba53dbac709488) re-name pypi package from pyDruid -> pydruid
- [d64a56b](https://github.com/druid-io/pydruid/commit/d64a56b255c5f63a9e5539c56b5d4908d16e4f1b) setup.py: upgrade version to 0.2.0, remove extraneous dependencies
- [5e6dfdb](https://github.com/druid-io/pydruid/commit/5e6dfdbdb1e3a57e78e554a9cddbe400dc718761) Update README.md (@dganguli)
- [abfbcf2](https://github.com/druid-io/pydruid/commit/abfbcf224feb3edce0ab40fb2f39b7977cf076a5) Update README.md (@dganguli)
- [d579de1](https://github.com/druid-io/pydruid/commit/d579de1e1d821decdb02549c21c119279018870b) Update README.md (@dganguli)
- [#6](https://github.com/druid-io/pydruid/pull/6) Merge pull request #6 from metamx/docs (@metamx)
- [3df572f](https://github.com/druid-io/pydruid/commit/3df572f603e620a4e514bdc2caec9bff7c8fc3aa) Update README.md (@dganguli)
- [d109749](https://github.com/druid-io/pydruid/commit/d109749aa17a2aadec1bc885ba25975d0f2e244b) Update README.md (@dganguli)
- [3c1b726](https://github.com/druid-io/pydruid/commit/3c1b7263ceb58f4dd2979bf54889535d3b5d93ed) Merge branch 'docs' of github.com:metamx/pydruid into docs
- [5da69b1](https://github.com/druid-io/pydruid/commit/5da69b128294cbdf2e2eb904e1faa5d22a931332) twitter graph figure for groupby example
- [1c97eb3](https://github.com/druid-io/pydruid/commit/1c97eb3b081c8f362583dcebe94be0b9319180ef) Update README.md (@dganguli)
- [5a19cc1](https://github.com/druid-io/pydruid/commit/5a19cc104440375a09f5cd2a9af18b7356cbb5fe) Update README.md (@dganguli)
- [32ae0f8](https://github.com/druid-io/pydruid/commit/32ae0f88bfb417e15ff12f837a4704f4235821c3) re-size avg tweet length figure part deux
- [a39e9bc](https://github.com/druid-io/pydruid/commit/a39e9bc7f9353fc1e49d6e0d607c1bad75851955) re-size avg tweet length figure
- [8f9b45d](https://github.com/druid-io/pydruid/commit/8f9b45dc41853f9ec52d72b761dd39e225835795) Merge branch 'docs' of github.com:metamx/pydruid into docs
- [df90783](https://github.com/druid-io/pydruid/commit/df907837782f76bf4d0142c93aff942b5c17c2b7) docs: created figures directory
- [eb4f4a2](https://github.com/druid-io/pydruid/commit/eb4f4a23d6806d38f498be3f3a9a0bf885eb3db9) Update README.md (@dganguli)
- [458b82e](https://github.com/druid-io/pydruid/commit/458b82e80d26259ee3654ac8d92293831fcc0596) README back to md from txt
- [6c18175](https://github.com/druid-io/pydruid/commit/6c18175b10a4d09506b49ec764956db269dcc203) updated built documentation
- [3b61bbd](https://github.com/druid-io/pydruid/commit/3b61bbd76691b3846ebaf23bc89beb7d6f059612) documented export methods and big fix to export_tsv for topn queries
- [4961495](https://github.com/druid-io/pydruid/commit/4961495c22417f073a552964736ff3802f6d3c19) fix topn docstring
- [1b1f00b](https://github.com/druid-io/pydruid/commit/1b1f00b9a104a1ca917e98dfa5a222534fb1235a) Filter and Postaggregator builder methods are static members of their respective classes
- [2f92ec7](https://github.com/druid-io/pydruid/commit/2f92ec78ce92a117621c53bb1dbf55bb2ec2f491) more sensical docstring for PyDruid
- [f49265d](https://github.com/druid-io/pydruid/commit/f49265d6fee07685b989197a02b7dd3d4a0969e8) documented PyDruid class
- [c71844b](https://github.com/druid-io/pydruid/commit/c71844bbd8bb033d5f3ec179269ea20baded5bea) commit initial version of built docs
- [8d570e4](https://github.com/druid-io/pydruid/commit/8d570e42eda367529f8f95373cccc675865f644a) documented segment_metadata. fixed a bug in it too
- [1e050bc](https://github.com/druid-io/pydruid/commit/1e050bcb14e8495d2b4dec64de61304a2e039deb) make post and parse private, made build and validate public again
- [69e9784](https://github.com/druid-io/pydruid/commit/69e9784b58e072e874576039de77641df796d11f) documented time_boundary
- [9f595df](https://github.com/druid-io/pydruid/commit/9f595dfe35fe27f5ae2e7974156a30e15b066889) re-name kwargs dataSource -> datasource and postAggregations -> post_aggregations
- [9a995dd](https://github.com/druid-io/pydruid/commit/9a995dd06428cf229ebab6a58bcfe4f463767871) Added documentation for groupby and timeseries queries
- [7552dcb](https://github.com/druid-io/pydruid/commit/7552dcb42477e28adad1a2dcda8983bcf634d1b8) topN has sphinx compatible example in docstring
- [59522a7](https://github.com/druid-io/pydruid/commit/59522a7416bf8e6bf2ca1d43af278d3180671311) Ignore .DS_store
- [01a8f88](https://github.com/druid-io/pydruid/commit/01a8f884ee11c0e718717108e344b1c40f2decbb) build and validate query methods now private
- [b44a8dc](https://github.com/druid-io/pydruid/commit/b44a8dc1a289199e13860d48f9a26df56d3caf57) sphinx compatible documentation for client.topN
- [5464a2c](https://github.com/druid-io/pydruid/commit/5464a2c7643bbd25cfaaa6373e8960eafce5f07d) Working documentatin using sphinx-quickstart
- [3023707](https://github.com/druid-io/pydruid/commit/30237073fe717c3d400a2a31f09911be3e9b3ae2) Each query sets its query type instead of passing it to build_query()
- [06d00da](https://github.com/druid-io/pydruid/commit/06d00da4bf416f00798cb3c3b10c4554290bc5c9) postaggregator.py: Field and Const postaggregators call super constructor
- [8605393](https://github.com/druid-io/pydruid/commit/8605393e5e010b4d62afcb98f04285299ce389f1) filters.py: bug fix to show() method
- [6c9b7d5](https://github.com/druid-io/pydruid/commit/6c9b7d5b9df199ccbf81b40b32ea7255ae823f1a) aggregators.py: re-name doublesum -> sum
- [51aedd1](https://github.com/druid-io/pydruid/commit/51aedd1c5b79f69dfd614a3106b4c60e1da4e521) client.py: documentatino for topN query
- [ba18670](https://github.com/druid-io/pydruid/commit/ba18670d5b6a01917ef4b1bb80cab636ae5eab14) export_tsv raises NotImplementedError if necessary
- [d8bc3a7](https://github.com/druid-io/pydruid/commit/d8bc3a78cc2dc6c49d5a0b1c2c0aa32f38863f2e) client.py:
- [3b53fec](https://github.com/druid-io/pydruid/commit/3b53fec3ebc5cbc2a4411611723c484e69348dea) Finally read the pep-8 style guide. Fix whitespace ensued
- [61300c9](https://github.com/druid-io/pydruid/commit/61300c9dc50e8272768b27411cabf4c99185a080) fix whitespace ftw
- [b3d269a](https://github.com/druid-io/pydruid/commit/b3d269a67e1977208d999132af793aed731fac6e) only parse query results once
- [0a15aeb](https://github.com/druid-io/pydruid/commit/0a15aeb7749f81fd847d867ae663f3ab2f7ffe89) client.py: bug fix export_tsv for groupBy queries
- [0d56b23](https://github.com/druid-io/pydruid/commit/0d56b2302ffe87c2ab1003da5f1ff80378f573eb) client.py:
- [ac74bf6](https://github.com/druid-io/pydruid/commit/ac74bf63f06f0a272b2803a50dc65ab1e32d910d) implemented topN queries. made more informative error messages
- [b660ba7](https://github.com/druid-io/pydruid/commit/b660ba71166e84e02413aa48d2f190580fd775d0) client.py: check if bard_url ends with a / before constructing full url
- [27e87cd](https://github.com/druid-io/pydruid/commit/27e87cd6fff3379a9d5939095006b2730c797456) query implementations share more post related code
- [ed5a9a6](https://github.com/druid-io/pydruid/commit/ed5a9a6d1e08c46d8cea79dbd6f26ea25c6996f0) whitespace ftw
- [11321e1](https://github.com/druid-io/pydruid/commit/11321e1c3457406d3fa5b3f6ce5c647b274ffda6) Made pyDruid interoperate with PostAggregators objects
- [c845eb5](https://github.com/druid-io/pydruid/commit/c845eb59244a6ac4198f25ce2732d939d63494d7) Removed extraneous comments and whitespace
- [3fae2b7](https://github.com/druid-io/pydruid/commit/3fae2b721fdcc6e62bd1489cb360080fe4f2505c) Updated post-aggs to be easier to express and use
- [71e2753](https://github.com/druid-io/pydruid/commit/71e27530c3faca12a95469ad8088775aa5ac0ee0) Bug fix to export_pandas
- [9bc5ba6](https://github.com/druid-io/pydruid/commit/9bc5ba62d5311983d03d27a4ff9c3de46c84ace5) Implemented pandas export for groupby queries
- [229355b](https://github.com/druid-io/pydruid/commit/229355b118cd68a53929846a54c90d6b4ac4dce6) Remove extraneous dependencies on matplotlib
- [#1](https://github.com/druid-io/pydruid/pull/1) Merge pull request #1 from rjurney/master (@rjurney)
- [5fb737e](https://github.com/druid-io/pydruid/commit/5fb737ee5c6abc867c18e3ab739e20c5bb3321fe) Working 1.7 (@rjurney)
- [efa2786](https://github.com/druid-io/pydruid/commit/efa2786debac9a9d7d8a05a9800c205890bbecb0) Added __init__.py to pydruid and updated to version 0.1.5 for release. (@rjurney)
- [cc99963](https://github.com/druid-io/pydruid/commit/cc99963f15a76073c12492267660238eff8d29ad) Trying to re-create source code. Something weird and terrible went on. (@rjurney)
- [3c9e1a0](https://github.com/druid-io/pydruid/commit/3c9e1a0fc98a8d9de9076995c6c3ef8579d9d33f) Renaming readme. (@rjurney)
- [441e7aa](https://github.com/druid-io/pydruid/commit/441e7aa5e4291316ea9b40bb23c8ea1b0897a677) Still trying to make pypi work, but I can't get the build to update on pypi. (@rjurney)
- [1cf2971](https://github.com/druid-io/pydruid/commit/1cf29718ee53d8a290839d54ddf9a752bd6b3554) Trying to make pip install work. (@rjurney)
- [4347e69](https://github.com/druid-io/pydruid/commit/4347e69127d7564319beda73dbe5ba53d86cee74) Crap, whats going on? (@rjurney)
- [978eeaa](https://github.com/druid-io/pydruid/commit/978eeaad75eeed7e79070349730cba2623f6b828) Massive cleanup (@rjurney)
- [0e6ee14](https://github.com/druid-io/pydruid/commit/0e6ee149483561e4a2fc86c594356436e417bc45) Made the module into a package, some re-org (@rjurney)
- [b43b95d](https://github.com/druid-io/pydruid/commit/b43b95d3371cc2e9beaa3c7a2d756806bf483469) Making this into a python project (@rjurney)
- [21f3b2b](https://github.com/druid-io/pydruid/commit/21f3b2b649d14619ed5269ba69ac14a58b301261) First code commit
- [35cd39e](https://github.com/druid-io/pydruid/commit/35cd39e755cd4136923973ae1594f8b3f4336f63) Add license headers
- [d00f822](https://github.com/druid-io/pydruid/commit/d00f822f259bc8bf87e8248be2458328ed8aeabf) Update LICENSE (@xvrl)
