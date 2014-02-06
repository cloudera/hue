#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from nose.tools import assert_true, assert_false, assert_equal, assert_not_equal

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access
from desktop.lib.rest import resource

from search.models import Collection


class MockResource():
  RESPONSE = None

  def __init__(self, client):
    pass

  @classmethod
  def set_solr_response(cls, response):
    MockResource.RESPONSE = response

  def get(self, *args, **kwargs):
    if 'collection_1/admin/file' in args[0]:
      return SOLR_SCHEMA
    else:
      return MockResource.RESPONSE


class TestSearchBase(object):

  def setUp(self):
    self.c = make_logged_in_client(username='test_search', is_superuser=False)
    grant_access('test_search', 'test_search', 'search')
    self.user = User.objects.get(username='test_search')

    self.prev_resource = resource.Resource
    resource.Resource = MockResource

  def tearDown(self):
    # Remove monkey patching
    resource.Resource = self.prev_resource


class TestWithMockedSolr(TestSearchBase):

  def test_index(self):
    response = self.c.get(reverse('search:index'))
    assert_true('search' in response.content, response.content)

  def test_strip_nulls(self):
    response = '{"uid":"1111111","method":"check_user"}\x00'
    response = json.loads(response.replace('\x00', '')) # Does not call real API

  def test_response_with_facets(self):
    collection, created = Collection.objects.get_or_create(name='collection_1', solr_properties={})

    self.c.cookies['hueSearchLastCollection'] = collection.id
    MockResource.set_solr_response("""{"responseHeader":{"status":0,"QTime":59,"params":{"facet":"true","facet.mincount":"1","facet.limit":"100","facet.date":"article_date","f.article_date.facet.date.start":"NOW-7MONTH/DAYS","wt":"json","rows":"15","user.name":"hue","start":"0","facet.sort":"count","q":"*:*","f.article_date.facet.date.end":"NOW-5MONTH","doAs":"romain","f.article_date.facet.date.gap":"+1DAYS","facet.field":["journal_title","author_facet"],"fq":["article_date:[2013-06-13T00:00:00Z TO 2013-06-13T00:00:00Z+1DAYS]","journal_title:\\"in\\""]}},"response":{"numFound":4,"start":0,"maxScore":1.0,"docs":[{"article_title":"Investigations for neonatal seizures.","journal_issn":"1878-0946","article_abstract_text":["Seizures during the neonatal period are always medical emergencies. Apart from the need for rapid anticonvulsive treatment, the underlying condition is often not immediately obvious. In the search for the correct diagnosis, a thorough history, clinical examination, laboratory work-up, neurophysiological and neuroradiological investigations are all essential. A close collaboration between neonatologists, neuropaediatricians, laboratory specialists, neurophysiologists and radiologists facilitates the adequate care of the infant."],"ontologies":["36481|1 "],"article_date":"2013-06-13T00:00:00Z","journal_title":"Seminars in fetal & neonatal medicine","date_created":"2013-08-22T00:00:00Z","journal_country":"Netherlands","journal_iso_abbreviation":"Semin Fetal Neonatal Med","id":"23680099","author":["B B Hallberg","M M Blennow"],"article_pagination":"196-201","journal_publication_date":"2013-08-22T00:00:00Z","affiliation":"Department of Neonatology, Karolinska Institutet and University Hospital, Stockholm, Sweden. boubou.hallberg@ki.se","language":"eng","_version_":1450807641462800385},{"article_title":"Enantiomeric selection properties of β-homoDNA: enhanced pairing for heterochiral complexes.","journal_issn":"1521-3773","article_date":"2013-06-13T00:00:00Z","journal_title":"Angewandte Chemie (International ed. in English)","date_created":"2013-07-20T00:00:00Z","journal_country":"Germany","journal_iso_abbreviation":"Angew. Chem. Int. Ed. Engl.","id":"23670912","author":["Daniele D D'Alonzo","Jussara J Amato","Guy G Schepers","Matheus M Froeyen","Arthur A Van Aerschot","Piet P Herdewijn","Annalisa A Guaragna"],"article_pagination":"6662-5","journal_publication_date":"2013-06-24T00:00:00Z","affiliation":"Dipartimento di Scienze Chimiche, Università degli Studi di Napoli Federico II, Via Cintia 21, 80126 Napoli, Italy. dandalonzo@unina.it","language":"eng","_version_":1450807661929955329},{"article_title":"Interference of bacterial cell-to-cell communication: a new concept of antimicrobial chemotherapy breaks antibiotic resistance.","journal_issn":"1664-302X","article_abstract_text":["Bacteria use a cell-to-cell communication activity termed \\"quorum sensing\\" to coordinate group behaviors in a cell density dependent manner. Quorum sensing influences the expression profile of diverse genes, including antibiotic tolerance and virulence determinants, via specific chemical compounds called \\"autoinducers\\". During quorum sensing, Gram-negative bacteria typically use an acylated homoserine lactone (AHL) called autoinducer 1. Since the first discovery of quorum sensing in a marine bacterium, it has been recognized that more than 100 species possess this mechanism of cell-to-cell communication. In addition to being of interest from a biological standpoint, quorum sensing is a potential target for antimicrobial chemotherapy. This unique concept of antimicrobial control relies on reducing the burden of virulence rather than killing the bacteria. It is believed that this approach will not only suppress the development of antibiotic resistance, but will also improve the treatment of refractory infections triggered by multi-drug resistant pathogens. In this paper, we review and track recent progress in studies on AHL inhibitors/modulators from a biological standpoint. It has been discovered that both natural and synthetic compounds can disrupt quorum sensing by a variety of means, such as jamming signal transduction, inhibition of signal production and break-down and trapping of signal compounds. We also focus on the regulatory elements that attenuate quorum sensing activities and discuss their unique properties. Understanding the biological roles of regulatory elements might be useful in developing inhibitor applications and understanding how quorum sensing is controlled."],"ontologies":["2402|1 ","1875|1 ","2047|3 ","36690|1 ","8120|1 ","1872|1 ","1861|1 ","1955|2 ","38027|1 ","3853|1 ","2237|3 ","37074|1 ","3043|2 ","36478|1 ","4403|1 ","2751|1 ","10751|1 ","36467|1 ","2387|1 ","7278|3 ","3826|1 "],"article_date":"2013-06-13T00:00:00Z","journal_title":"Frontiers in microbiology","date_created":"2013-06-30T00:00:00Z","journal_country":"Switzerland","journal_iso_abbreviation":"Front Microbiol","id":"23720655","author":["Hidetada H Hirakawa","Haruyoshi H Tomita"],"article_pagination":"114","journal_publication_date":"2013-09-13T00:00:00Z","affiliation":"Advanced Scientific Research Leaders Development Unit, Gunma University Maebashi, Gunma, Japan.","language":"eng","_version_":1450807662055784448},{"article_title":"The role of musical training in emergent and event-based timing.","journal_issn":"1662-5161","article_abstract_text":["Introduction: Musical performance is thought to rely predominantly on event-based timing involving a clock-like neural process and an explicit internal representation of the time interval. Some aspects of musical performance may rely on emergent timing, which is established through the optimization of movement kinematics, and can be maintained without reference to any explicit representation of the time interval. We predicted that musical training would have its largest effect on event-based timing, supporting the dissociability of these timing processes and the dominance of event-based timing in musical performance. Materials and Methods: We compared 22 musicians and 17 non-musicians on the prototypical event-based timing task of finger tapping and on the typically emergently timed task of circle drawing. For each task, participants first responded in synchrony with a metronome (Paced) and then responded at the same rate without the metronome (Unpaced). Results: Analyses of the Unpaced phase revealed that non-musicians were more variable in their inter-response intervals for finger tapping compared to circle drawing. Musicians did not differ between the two tasks. Between groups, non-musicians were more variable than musicians for tapping but not for drawing. We were able to show that the differences were due to less timer variability in musicians on the tapping task. Correlational analyses of movement jerk and inter-response interval variability revealed a negative association for tapping and a positive association for drawing in non-musicians only. Discussion: These results suggest that musical training affects temporal variability in tapping but not drawing. Additionally, musicians and non-musicians may be employing different movement strategies to maintain accurate timing in the two tasks. These findings add to our understanding of how musical training affects timing and support the dissociability of event-based and emergent timing modes."],"ontologies":["36810|1 ","49002|1 ","3132|1 ","3797|1 ","37953|1 ","36563|2 ","524|1 ","3781|1 ","2848|1 ","17163|1 ","17165|1 ","49010|1 ","36647|3 ","36529|1 ","2936|1 ","2643|1 ","714|1 ","3591|1 ","2272|1 ","3103|1 ","2265|1 ","37051|1 ","3691|1 "],"article_date":"2013-06-14T00:00:00Z","journal_title":"Frontiers in human neuroscience","date_created":"2013-06-29T00:00:00Z","journal_country":"Switzerland","journal_iso_abbreviation":"Front Hum Neurosci","id":"23717275","author":["L H LH Baer","J L N JL Thibodeau","T M TM Gralnick","K Z H KZ Li","V B VB Penhune"],"article_pagination":"191","journal_publication_date":"2013-09-13T00:00:00Z","affiliation":"Department of Psychology, Centre for Research in Human Development, Concordia University Montréal, QC, Canada.","language":"eng","_version_":1450807667479019520}]},"facet_counts":{"facet_queries":{},"facet_fields":{"journal_title":["in",4,"frontiers",2,"angewandte",1,"chemie",1,"ed",1,"english",1,"fetal",1,"human",1,"international",1,"medicine",1,"microbiology",1,"neonatal",1,"neuroscience",1,"seminars",1],"author_facet":["Annalisa A Guaragna",1,"Arthur A Van Aerschot",1,"B B Hallberg",1,"Daniele D D'Alonzo",1,"Guy G Schepers",1,"Haruyoshi H Tomita",1,"Hidetada H Hirakawa",1,"J L N JL Thibodeau",1,"Jussara J Amato",1,"K Z H KZ Li",1,"L H LH Baer",1,"M M Blennow",1,"Matheus M Froeyen",1,"Piet P Herdewijn",1,"T M TM Gralnick",1,"V B VB Penhune",1]},"facet_dates":{"article_date":{"gap":"+1DAYS","start":"2013-04-27T00:00:00Z","end":"2013-06-28T00:00:00Z"}},"facet_ranges":{}},"highlighting":{"23680099":{},"23670912":{},"23720655":{},"23717275":{}},"spellcheck":{"suggestions":["correctlySpelled",false]}}""")

    # journal_title facet + date range article_date facets clicked and author_facet not clicked
    # http://solr:8983/solr/articles/select?user.name=hue&doAs=romain&q=%2A%3A%2A&wt=json&rows=15&start=0&facet=true&facet.mincount=1&facet.limit=100&facet.sort=count&facet.field=journal_title&facet.field=author_facet&facet.date=article_date&f.article_date.facet.date.start=NOW-7MONTH%2FDAYS&f.article_date.facet.date.end=NOW-5MONTH&f.article_date.facet.date.gap=%2B1DAYS&fq=article_date%3A%5B2013-06-13T00%3A00%3A00Z+TO+2013-06-13T00%3A00%3A00Z%2B1DAYS%5D&fq=journal_title%3A%22in%22
    response = self.c.get(reverse('search:index'))

    assert_false('alert alert-error' in response.content, response.content)

    assert_true('author_facet' in response.content, response.content)
    assert_true('Annalisa A Guaragna' in response.content, response.content)

    assert_true('journal_title' in response.content, response.content)
    assert_true('angewandte' in response.content, response.content)

    assert_true('Showing 4 results' in response.content, response.content)

  def test_empty_highlighting(self):
    collection, created = Collection.objects.get_or_create(name='collection_1', solr_properties={})

    assert_equal('[]', collection.result.get_highlighting())

    assert_true('{{_version_}} {{affiliation}}' in collection.result.get_template(True), collection.result.get_template(True))

  def test_download(self):
    collection, created = Collection.objects.get_or_create(name='collection_1', solr_properties={})

    self.c.cookies['hueSearchLastCollection'] = collection.id
    MockResource.set_solr_response("""{"responseHeader":{"status":0,"QTime":59,"params":{"facet":"true","facet.mincount":"1","facet.limit":"100","facet.date":"article_date","f.article_date.facet.date.start":"NOW-7MONTH/DAYS","wt":"json","rows":"15","user.name":"hue","start":"0","facet.sort":"count","q":"*:*","f.article_date.facet.date.end":"NOW-5MONTH","doAs":"romain","f.article_date.facet.date.gap":"+1DAYS","facet.field":["journal_title","author_facet"],"fq":["article_date:[2013-06-13T00:00:00Z TO 2013-06-13T00:00:00Z+1DAYS]","journal_title:\\"in\\""]}},"response":{"numFound":4,"start":0,"maxScore":1.0,"docs":[{"article_title":"Investigations for neonatal seizures.","journal_issn":"1878-0946","article_abstract_text":["Seizures during the neonatal period are always medical emergencies. Apart from the need for rapid anticonvulsive treatment, the underlying condition is often not immediately obvious. In the search for the correct diagnosis, a thorough history, clinical examination, laboratory work-up, neurophysiological and neuroradiological investigations are all essential. A close collaboration between neonatologists, neuropaediatricians, laboratory specialists, neurophysiologists and radiologists facilitates the adequate care of the infant."],"ontologies":["36481|1 "],"article_date":"2013-06-13T00:00:00Z","journal_title":"Seminars in fetal & neonatal medicine","date_created":"2013-08-22T00:00:00Z","journal_country":"Netherlands","journal_iso_abbreviation":"Semin Fetal Neonatal Med","id":"23680099","author":["B B Hallberg","M M Blennow"],"article_pagination":"196-201","journal_publication_date":"2013-08-22T00:00:00Z","affiliation":"Department of Neonatology, Karolinska Institutet and University Hospital, Stockholm, Sweden. boubou.hallberg@ki.se","language":"eng","_version_":1450807641462800385},{"article_title":"Enantiomeric selection properties of β-homoDNA: enhanced pairing for heterochiral complexes.","journal_issn":"1521-3773","article_date":"2013-06-13T00:00:00Z","journal_title":"Angewandte Chemie (International ed. in English)","date_created":"2013-07-20T00:00:00Z","journal_country":"Germany","journal_iso_abbreviation":"Angew. Chem. Int. Ed. Engl.","id":"23670912","author":["Daniele D D'Alonzo","Jussara J Amato","Guy G Schepers","Matheus M Froeyen","Arthur A Van Aerschot","Piet P Herdewijn","Annalisa A Guaragna"],"article_pagination":"6662-5","journal_publication_date":"2013-06-24T00:00:00Z","affiliation":"Dipartimento di Scienze Chimiche, Università degli Studi di Napoli Federico II, Via Cintia 21, 80126 Napoli, Italy. dandalonzo@unina.it","language":"eng","_version_":1450807661929955329},{"article_title":"Interference of bacterial cell-to-cell communication: a new concept of antimicrobial chemotherapy breaks antibiotic resistance.","journal_issn":"1664-302X","article_abstract_text":["Bacteria use a cell-to-cell communication activity termed \\"quorum sensing\\" to coordinate group behaviors in a cell density dependent manner. Quorum sensing influences the expression profile of diverse genes, including antibiotic tolerance and virulence determinants, via specific chemical compounds called \\"autoinducers\\". During quorum sensing, Gram-negative bacteria typically use an acylated homoserine lactone (AHL) called autoinducer 1. Since the first discovery of quorum sensing in a marine bacterium, it has been recognized that more than 100 species possess this mechanism of cell-to-cell communication. In addition to being of interest from a biological standpoint, quorum sensing is a potential target for antimicrobial chemotherapy. This unique concept of antimicrobial control relies on reducing the burden of virulence rather than killing the bacteria. It is believed that this approach will not only suppress the development of antibiotic resistance, but will also improve the treatment of refractory infections triggered by multi-drug resistant pathogens. In this paper, we review and track recent progress in studies on AHL inhibitors/modulators from a biological standpoint. It has been discovered that both natural and synthetic compounds can disrupt quorum sensing by a variety of means, such as jamming signal transduction, inhibition of signal production and break-down and trapping of signal compounds. We also focus on the regulatory elements that attenuate quorum sensing activities and discuss their unique properties. Understanding the biological roles of regulatory elements might be useful in developing inhibitor applications and understanding how quorum sensing is controlled."],"ontologies":["2402|1 ","1875|1 ","2047|3 ","36690|1 ","8120|1 ","1872|1 ","1861|1 ","1955|2 ","38027|1 ","3853|1 ","2237|3 ","37074|1 ","3043|2 ","36478|1 ","4403|1 ","2751|1 ","10751|1 ","36467|1 ","2387|1 ","7278|3 ","3826|1 "],"article_date":"2013-06-13T00:00:00Z","journal_title":"Frontiers in microbiology","date_created":"2013-06-30T00:00:00Z","journal_country":"Switzerland","journal_iso_abbreviation":"Front Microbiol","id":"23720655","author":["Hidetada H Hirakawa","Haruyoshi H Tomita"],"article_pagination":"114","journal_publication_date":"2013-09-13T00:00:00Z","affiliation":"Advanced Scientific Research Leaders Development Unit, Gunma University Maebashi, Gunma, Japan.","language":"eng","_version_":1450807662055784448},{"article_title":"The role of musical training in emergent and event-based timing.","journal_issn":"1662-5161","article_abstract_text":["Introduction: Musical performance is thought to rely predominantly on event-based timing involving a clock-like neural process and an explicit internal representation of the time interval. Some aspects of musical performance may rely on emergent timing, which is established through the optimization of movement kinematics, and can be maintained without reference to any explicit representation of the time interval. We predicted that musical training would have its largest effect on event-based timing, supporting the dissociability of these timing processes and the dominance of event-based timing in musical performance. Materials and Methods: We compared 22 musicians and 17 non-musicians on the prototypical event-based timing task of finger tapping and on the typically emergently timed task of circle drawing. For each task, participants first responded in synchrony with a metronome (Paced) and then responded at the same rate without the metronome (Unpaced). Results: Analyses of the Unpaced phase revealed that non-musicians were more variable in their inter-response intervals for finger tapping compared to circle drawing. Musicians did not differ between the two tasks. Between groups, non-musicians were more variable than musicians for tapping but not for drawing. We were able to show that the differences were due to less timer variability in musicians on the tapping task. Correlational analyses of movement jerk and inter-response interval variability revealed a negative association for tapping and a positive association for drawing in non-musicians only. Discussion: These results suggest that musical training affects temporal variability in tapping but not drawing. Additionally, musicians and non-musicians may be employing different movement strategies to maintain accurate timing in the two tasks. These findings add to our understanding of how musical training affects timing and support the dissociability of event-based and emergent timing modes."],"ontologies":["36810|1 ","49002|1 ","3132|1 ","3797|1 ","37953|1 ","36563|2 ","524|1 ","3781|1 ","2848|1 ","17163|1 ","17165|1 ","49010|1 ","36647|3 ","36529|1 ","2936|1 ","2643|1 ","714|1 ","3591|1 ","2272|1 ","3103|1 ","2265|1 ","37051|1 ","3691|1 "],"article_date":"2013-06-14T00:00:00Z","journal_title":"Frontiers in human neuroscience","date_created":"2013-06-29T00:00:00Z","journal_country":"Switzerland","journal_iso_abbreviation":"Front Hum Neurosci","id":"23717275","author":["L H LH Baer","J L N JL Thibodeau","T M TM Gralnick","K Z H KZ Li","V B VB Penhune"],"article_pagination":"191","journal_publication_date":"2013-09-13T00:00:00Z","affiliation":"Department of Psychology, Centre for Research in Human Development, Concordia University Montréal, QC, Canada.","language":"eng","_version_":1450807667479019520}]},"facet_counts":{"facet_queries":{},"facet_fields":{"journal_title":["in",4,"frontiers",2,"angewandte",1,"chemie",1,"ed",1,"english",1,"fetal",1,"human",1,"international",1,"medicine",1,"microbiology",1,"neonatal",1,"neuroscience",1,"seminars",1],"author_facet":["Annalisa A Guaragna",1,"Arthur A Van Aerschot",1,"B B Hallberg",1,"Daniele D D'Alonzo",1,"Guy G Schepers",1,"Haruyoshi H Tomita",1,"Hidetada H Hirakawa",1,"J L N JL Thibodeau",1,"Jussara J Amato",1,"K Z H KZ Li",1,"L H LH Baer",1,"M M Blennow",1,"Matheus M Froeyen",1,"Piet P Herdewijn",1,"T M TM Gralnick",1,"V B VB Penhune",1]},"facet_dates":{"article_date":{"gap":"+1DAYS","start":"2013-04-27T00:00:00Z","end":"2013-06-28T00:00:00Z"}},"facet_ranges":{}},"highlighting":{"23680099":{},"23670912":{},"23720655":{},"23717275":{}},"spellcheck":{"suggestions":["correctlySpelled",false]}}""")

    csv_response = self.c.get(reverse('search:download', kwargs={'format': 'csv'}))
    assert_equal(6898, len(csv_response.content))
    assert_equal('application/csv', csv_response['Content-Type'])
    assert_true('article_title,_version_,article_pagination,author,language,journal_title,journal_country,journal_issn,id,affiliation,article_date,journal_iso_abbreviation,journal_publication_date,date_created,article_abstract_text' in csv_response.content, csv_response.content)
    assert_true("""The role of musical training in emergent and event-based timing.,1450807667479019520,191,"[u'L H LH Baer', u'J L N JL Thibodeau', u'T M TM Gralnick', u'K Z H KZ Li', u'V B VB Penhune']",eng,Frontiers in human neuroscience,Switzerland,1662-5161,23717275,"Department of Psychology, Centre for Research in Human Development, Concordia University Montréal, QC, Canada.",2013-06-14T00:00:00Z,Front Hum Neurosci,2013-09-13T00:00:00Z,2013-06-29T00:00:00Z,"[u'Introduction: Musical performance is thought to rely predominantly on event-based timing involving a clock-like neural process and an explicit internal representation of the time interval. Some aspects of musical performance may rely on emergent timing, which is established through the optimization of movement kinematics, and can be maintained without reference to any explicit representation of the time interval. We predicted that musical training would have its largest effect on event-based timing, supporting the dissociability of these timing processes and the dominance of event-based timing in musical performance. Materials and Methods: We compared 22 musicians and 17 non-musicians on the prototypical event-based timing task of finger tapping and on the typically emergently timed task of circle drawing. For each task, participants first responded in synchrony with a metronome (Paced) and then responded at the same rate without the metronome (Unpaced). Results: Analyses of the Unpaced phase revealed that non-musicians were more variable in their inter-response intervals for finger tapping compared to circle drawing. Musicians did not differ between the two tasks. Between groups, non-musicians were more variable than musicians for tapping but not for drawing. We were able to show that the differences were due to less timer variability in musicians on the tapping task. Correlational analyses of movement jerk and inter-response interval variability revealed a negative association for tapping and a positive association for drawing in non-musicians only. Discussion: These results suggest that musical training affects temporal variability in tapping but not drawing. Additionally, musicians and non-musicians may be employing different movement strategies to maintain accurate timing in the two tasks. These findings add to our understanding of how musical training affects timing and support the dissociability of event-based and emergent timing modes.']","[u'36810|1 ', u'49002|1 ', u'3132|1 ', u'3797|1 ', u'37953|1 ', u'36563|2 ', u'524|1 ', u'3781|1 ', u'2848|1 ', u'17163|1 ', u'17165|1 ', u'49010|1 ', u'36647|3 ', u'36529|1 ', u'2936|1 ', u'2643|1 ', u'714|1 ', u'3591|1 ', u'2272|1 ', u'3103|1 ', u'2265|1 ', u'37051|1 ', u'3691|1 ']""" in csv_response.content, csv_response.content)

    xls_response = self.c.get(reverse('search:download', kwargs={'format': 'xls'}))
    assert_not_equal(0, len(xls_response.content))
    assert_equal('application/xls', xls_response['Content-Type'])


SOLR_SCHEMA = """<?xml version="1.0" encoding="UTF-8" ?>
<!--
 Licensed to the Apache Software Foundation (ASF) under one or more
 contributor license agreements.  See the NOTICE file distributed with
 this work for additional information regarding copyright ownership.
 The ASF licenses this file to You under the Apache License, Version 2.0
 (the "License"); you may not use this file except in compliance with
 the License.  You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
-->

<!--
 This is the Solr schema file. This file should be named "schema.xml" and
 should be in the conf directory under the solr home
 (i.e. ./solr/conf/schema.xml by default)
 or located where the classloader for the Solr webapp can find it.

 This example schema is the recommended starting point for users.
 It should be kept correct and concise, usable out-of-the-box.

 For more information, on how to customize this file, please see
 http://wiki.apache.org/solr/SchemaXml

 PERFORMANCE NOTE: this schema includes many optional features and should not
 be used for benchmarking.  To improve performance one could
  - set stored="false" for all fields possible (esp large fields) when you
    only need to search on the field but don't need to return the original
    value.
  - set indexed="false" if you don't need to search on the field, but only
    return the field as a result of searching on other indexed fields.
  - remove all unneeded copyField statements
  - for best index size and searching performance, set "index" to false
    for all general text fields, use copyField to copy them to the
    catchall "text" field, and use that for searching.
  - For maximum indexing performance, use the StreamingUpdateSolrServer
    java client.
  - Remember to run the JVM in server mode, and use a higher logging level
    that avoids logging every request
-->

<schema name="example" version="1.5">
    <!-- attribute "name" is the name of this schema and is only used for display purposes.
         version="x.y" is Solr's version number for the schema syntax and
         semantics.  It should not normally be changed by applications.

         1.0: multiValued attribute did not exist, all fields are multiValued
              by nature
         1.1: multiValued attribute introduced, false by default
         1.2: omitTermFreqAndPositions attribute introduced, true by default
              except for text fields.
         1.3: removed optional field compress feature
         1.4: autoGeneratePhraseQueries attribute introduced to drive QueryParser
              behavior when a single string produces multiple tokens.  Defaults
              to off for version >= 1.4
         1.5: omitNorms defaults to true for primitive field types
              (int, float, boolean, string...)
       -->

    <fields>
        <!-- Valid attributes for fields:
          name: mandatory - the name for the field
          type: mandatory - the name of a field type from the
            <types> fieldType section
          indexed: true if this field should be indexed (searchable or sortable)
          stored: true if this field should be retrievable
          docValues: true if this field should have doc values. Doc values are
            useful for faceting, grouping, sorting and function queries. Although not
            required, doc values will make the index faster to load, more
            NRT-friendly and more memory-efficient. They however come with some
            limitations: they are currently only supported by StrField, UUIDField
            and all Trie*Fields, and depending on the field type, they might
            require the field to be single-valued, be required or have a default
            value (check the documentation of the field type you're interested in
            for more information)
          multiValued: true if this field may contain multiple values per document
          omitNorms: (expert) set to true to omit the norms associated with
            this field (this disables length normalization and index-time
            boosting for the field, and saves some memory).  Only full-text
            fields or fields that need an index-time boost need norms.
            Norms are omitted for primitive (non-analyzed) types by default.
          termVectors: [false] set to true to store the term vector for a
            given field.
            When using MoreLikeThis, fields used for similarity should be
            stored for best performance.
          termPositions: Store position information with the term vector.
            This will increase storage costs.
          termOffsets: Store offset information with the term vector. This
            will increase storage costs.
          required: The field is required.  It will throw an error if the
            value does not exist
          default: a value that should be used if no value is specified
            when adding a document.
        -->

        <!-- field names should consist of alphanumeric or underscore characters only and
           not start with a digit.  This is not currently strictly enforced,
           but other field names will not have first class support from all components
           and back compatibility is not guaranteed.  Names with both leading and
           trailing underscores (e.g. _version_) are reserved.
        -->

        <field name="id" type="string" indexed="true" stored="true" required="true" multiValued="false"/>
        <field name="_version_" type="long" indexed="true" stored="true"/>
        <field name="affiliation" type="text_multi_lang" indexed="true" stored="true"/>
        <field name="article_abstract_text" type="text_multi_lang" indexed="true" stored="true" multiValued="true" termVectors="true" />
        <field name="article_date" type="tdate" indexed="true" stored="true"/>
        <field name="article_pagination" type="string" indexed="true" stored="true"/>
        <field name="article_title" type="text_multi_lang" indexed="true" stored="true" termVectors="true" />
        <field name="article_title_sort" type="alphaOnlySort" indexed="true" stored="false"/>
        <field name="author" type="text_multi_lang" indexed="true" stored="true" multiValued="true"/>
        <field name="author_facet" type="string" indexed="true" stored="false" multiValued="true"/>
        <field name="date_created" type="tdate" indexed="true" stored="true"/>
        <field name="journal_country" type="lowercase" indexed="true" stored="true"/>
        <field name="journal_iso_abbreviation" type="lowercase" indexed="true" stored="true"/>
        <field name="journal_issn" type="string" indexed="true" stored="true"/>
        <field name="journal_publication_date" type="tdate" indexed="true" stored="true"/>
        <field name="journal_title" type="text_multi_lang" indexed="true" stored="true"/>
        <field name="journal_title_sort" type="alphaOnlySort" indexed="true" stored="false"/>
        <field name="language" type="lowercase" indexed="true" stored="true"/>
        <field name="other_metadata" type="text_multi_lang" indexed="true" stored="true" multiValued="true"/>
        <field name="ontologies" type="payloads" indexed="true" stored="true" multiValued="true" />
        <field name="word_bag" type="text_multi_lang" indexed="true" stored="false" multiValued="true"/>
        <field name="roots" type="string" indexed="true" stored="false" multiValued="true" />
    </fields>


    <!-- Field to use to determine and enforce document uniqueness.
         Unless this field is marked with required="false", it will be a required field
      -->
    <uniqueKey>id</uniqueKey>

    <!-- DEPRECATED: The defaultSearchField is consulted by various query parsers when
     parsing a query string that isn't explicit about the field.  Machine (non-user)
     generated queries are best made explicit, or they can use the "df" request parameter
     which takes precedence over this.
     Note: Un-commenting defaultSearchField will be insufficient if your request handler
     in solrconfig.xml defines "df", which takes precedence. That would need to be removed.
    <defaultSearchField>text</defaultSearchField> -->

    <!-- DEPRECATED: The defaultOperator (AND|OR) is consulted by various query parsers
     when parsing a query string to determine if a clause of the query should be marked as
     required or optional, assuming the clause isn't already marked by some operator.
     The default is OR, which is generally assumed so it is not a good idea to change it
     globally here.  The "q.op" request parameter takes precedence over this.
    <solrQueryParser defaultOperator="OR"/> -->

    <!-- copyField commands copy one field to another at the time a document
          is added to the index.  It's used either to index the same field differently,
          or to add multiple fields to the same field for easier/faster searching.  -->

    <!--copyField source="cat" dest="text"/-->
    <copyField source="article_title" dest="article_title_sort"/>
    <copyField source="journal_title" dest="journal_title_sort"/>
    <copyField source="author" dest="author_facet"/>

    <types>
        <!-- field type definitions. The "name" attribute is
           just a label to be used by field definitions.  The "class"
           attribute and any other attributes determine the real
           behavior of the fieldType.
             Class names starting with "solr" refer to java classes in a
           standard package such as org.apache.solr.analysis
        -->

        <!-- The StrField type is not analyzed, but indexed/stored verbatim.
           It supports doc values but in that case the field needs to be
           single-valued and either required or have a default value.
          -->
        <fieldType name="string" class="solr.StrField" sortMissingLast="true"/>

        <!-- boolean type: "true" or "false" -->
        <fieldType name="boolean" class="solr.BoolField" sortMissingLast="true"/>

        <!-- sortMissingLast and sortMissingFirst attributes are optional attributes are
             currently supported on types that are sorted internally as strings
             and on numeric types.
             This includes "string","boolean", and, as of 3.5 (and 4.x),
             int, float, long, date, double, including the "Trie" variants.
           - If sortMissingLast="true", then a sort on this field will cause documents
             without the field to come after documents with the field,
             regardless of the requested sort order (asc or desc).
           - If sortMissingFirst="true", then a sort on this field will cause documents
             without the field to come before documents with the field,
             regardless of the requested sort order.
           - If sortMissingLast="false" and sortMissingFirst="false" (the default),
             then default lucene sorting will be used which places docs without the
             field first in an ascending sort and last in a descending sort.
        -->

        <!--
          Default numeric field types. For faster range queries, consider the tint/tfloat/tlong/tdouble types.

          These fields support doc values, but they require the field to be
          single-valued and either be required or have a default value.
        -->
        <fieldType name="int" class="solr.TrieIntField" precisionStep="0" positionIncrementGap="0"/>
        <fieldType name="float" class="solr.TrieFloatField" precisionStep="0" positionIncrementGap="0"/>
        <fieldType name="long" class="solr.TrieLongField" precisionStep="0" positionIncrementGap="0"/>
        <fieldType name="double" class="solr.TrieDoubleField" precisionStep="0" positionIncrementGap="0"/>

        <!--
         Numeric field types that index each value at various levels of precision
         to accelerate range queries when the number of values between the range
         endpoints is large. See the javadoc for NumericRangeQuery for internal
         implementation details.

         Smaller precisionStep values (specified in bits) will lead to more tokens
         indexed per value, slightly larger index size, and faster range queries.
         A precisionStep of 0 disables indexing at different precision levels.
        -->
        <fieldType name="tint" class="solr.TrieIntField" precisionStep="8" positionIncrementGap="0"/>
        <fieldType name="tfloat" class="solr.TrieFloatField" precisionStep="8" positionIncrementGap="0"/>
        <fieldType name="tlong" class="solr.TrieLongField" precisionStep="8" positionIncrementGap="0"/>
        <fieldType name="tdouble" class="solr.TrieDoubleField" precisionStep="8" positionIncrementGap="0"/>

        <!-- The format for this date field is of the form 1995-12-31T23:59:59Z, and
             is a more restricted form of the canonical representation of dateTime
             http://www.w3.org/TR/xmlschema-2/#dateTime
             The trailing "Z" designates UTC time and is mandatory.
             Optional fractional seconds are allowed: 1995-12-31T23:59:59.999Z
             All other components are mandatory.

             Expressions can also be used to denote calculations that should be
             performed relative to "NOW" to determine the value, ie...

                   NOW/HOUR
                      ... Round to the start of the current hour
                   NOW-1DAY
                      ... Exactly 1 day prior to now
                   NOW/DAY+6MONTHS+3DAYS
                      ... 6 months and 3 days in the future from the start of
                          the current day

             Consult the DateField javadocs for more information.

             Note: For faster range queries, consider the tdate type
          -->
        <fieldType name="date" class="solr.TrieDateField" precisionStep="0" positionIncrementGap="0"/>

        <!-- A Trie based date field for faster date range queries and date faceting. -->
        <fieldType name="tdate" class="solr.TrieDateField" precisionStep="6" positionIncrementGap="0"/>


        <!--Binary data type. The data should be sent/retrieved in as Base64 encoded Strings -->
        <fieldtype name="binary" class="solr.BinaryField"/>

        <!-- solr.TextField allows the specification of custom text analyzers
             specified as a tokenizer and a list of token filters. Different
             analyzers may be specified for indexing and querying.

             The optional positionIncrementGap puts space between multiple fields of
             this type on the same document, with the purpose of preventing false phrase
             matching across fields.

             For more info on customizing your analyzer chain, please see
             http://wiki.apache.org/solr/AnalyzersTokenizersTokenFilters
         -->

        <!-- One can also specify an existing Analyzer class that has a
             default constructor via the class attribute on the analyzer element.
             Example:
        <fieldType name="text_greek" class="solr.TextField">
          <analyzer class="org.apache.lucene.analysis.el.GreekAnalyzer"/>
        </fieldType>
        -->

        <!-- A text field that only splits on whitespace for exact matching of words -->
        <fieldType name="text_ws" class="solr.TextField" positionIncrementGap="100">
            <analyzer>
                <tokenizer class="solr.WhitespaceTokenizerFactory"/>
            </analyzer>
        </fieldType>

        <!-- A general text field that has reasonable, generic
             cross-language defaults: it tokenizes with StandardTokenizer,
         removes stop words from case-insensitive "stopwords.txt"
         (empty by default), and down cases.  At query time only, it
         also applies synonyms. -->
        <fieldType name="text_general" class="solr.TextField" positionIncrementGap="100">
            <analyzer type="index">
                <tokenizer class="solr.StandardTokenizerFactory"/>
                <filter class="solr.StopFilterFactory" ignoreCase="true" words="stopwords.txt"/>
                <!-- in this example, we will only use synonyms at query time
                <filter class="solr.SynonymFilterFactory" synonyms="index_synonyms.txt" ignoreCase="true" expand="false"/>
                -->
                <filter class="solr.LowerCaseFilterFactory"/>
            </analyzer>
            <analyzer type="query">
                <tokenizer class="solr.StandardTokenizerFactory"/>
                <filter class="solr.StopFilterFactory" ignoreCase="true" words="stopwords.txt"/>
                <filter class="solr.SynonymFilterFactory" synonyms="synonyms.txt" ignoreCase="true" expand="true"/>
                <filter class="solr.LowerCaseFilterFactory"/>
            </analyzer>
        </fieldType>

        <!-- A text field with defaults appropriate for English: it
             tokenizes with StandardTokenizer, removes English stop words
             (lang/stopwords_en.txt), down cases, protects words from protwords.txt, and
             finally applies Porter's stemming.  The query time analyzer
             also applies synonyms from synonyms.txt. -->
        <fieldType name="text_multi_lang" class="solr.TextField" positionIncrementGap="100">
            <analyzer type="index">
                <tokenizer class="solr.StandardTokenizerFactory"/>
                <!-- in this example, we will only use synonyms at query time
                <filter class="solr.SynonymFilterFactory" synonyms="index_synonyms.txt" ignoreCase="true" expand="false"/>
                -->
                <!-- Case insensitive stop word removal.
                -->
                <!--filter class="solr.StopFilterFactory"
                        ignoreCase="true"
                        words="lang/stopwords_en.txt"
                        /-->
                <filter class="solr.LowerCaseFilterFactory"/>
                <filter class="solr.ASCIIFoldingFilterFactory"/>
                <!--filter class="solr.KeywordMarkerFilterFactory" protected="protwords.txt"/-->
                <!-- Optionally you may want to use this less aggressive stemmer instead of PorterStemFilterFactory:
                    <filter class="solr.EnglishMinimalStemFilterFactory"/>
                -->
            </analyzer>
            <analyzer type="query">
                <tokenizer class="solr.StandardTokenizerFactory"/>
                <filter class="solr.SynonymFilterFactory" synonyms="synonyms.txt" ignoreCase="true" expand="true"/>
                <!--filter class="solr.StopFilterFactory"
                        ignoreCase="true"
                        words="lang/stopwords_en.txt"
                        /-->
                <filter class="solr.LowerCaseFilterFactory"/>
                <filter class="solr.ASCIIFoldingFilterFactory"/>
                <!--filter class="solr.KeywordMarkerFilterFactory" protected="protwords.txt"/-->
                <!-- Optionally you may want to use this less aggressive stemmer instead of PorterStemFilterFactory:
                    <filter class="solr.EnglishMinimalStemFilterFactory"/>
                -->
            </analyzer>
        </fieldType>

        <!-- A text field with defaults appropriate for English, plus
         aggressive word-splitting and autophrase features enabled.
         This field is just like text_en, except it adds
         WordDelimiterFilter to enable splitting and matching of
         words on case-change, alpha numeric boundaries, and
         non-alphanumeric chars.  This means certain compound word
         cases will work, for example query "wi fi" will match
         document "WiFi" or "wi-fi".
            -->
        <fieldType name="text_en_splitting" class="solr.TextField" positionIncrementGap="100"
                   autoGeneratePhraseQueries="true">
            <analyzer type="index">
                <tokenizer class="solr.WhitespaceTokenizerFactory"/>
                <!-- in this example, we will only use synonyms at query time
                <filter class="solr.SynonymFilterFactory" synonyms="index_synonyms.txt" ignoreCase="true" expand="false"/>
                -->
                <!-- Case insensitive stop word removal.
                -->
                <filter class="solr.StopFilterFactory"
                        ignoreCase="true"
                        words="lang/stopwords_en.txt"
                        />
                <filter class="solr.WordDelimiterFilterFactory" generateWordParts="1" generateNumberParts="1"
                        catenateWords="1" catenateNumbers="1" catenateAll="0" splitOnCaseChange="1"/>
                <filter class="solr.LowerCaseFilterFactory"/>
                <filter class="solr.KeywordMarkerFilterFactory" protected="protwords.txt"/>
                <filter class="solr.PorterStemFilterFactory"/>
            </analyzer>
            <analyzer type="query">
                <tokenizer class="solr.WhitespaceTokenizerFactory"/>
                <filter class="solr.SynonymFilterFactory" synonyms="synonyms.txt" ignoreCase="true" expand="true"/>
                <filter class="solr.StopFilterFactory"
                        ignoreCase="true"
                        words="lang/stopwords_en.txt"
                        />
                <filter class="solr.WordDelimiterFilterFactory" generateWordParts="1" generateNumberParts="1"
                        catenateWords="0" catenateNumbers="0" catenateAll="0" splitOnCaseChange="1"/>
                <filter class="solr.LowerCaseFilterFactory"/>
                <filter class="solr.KeywordMarkerFilterFactory" protected="protwords.txt"/>
                <filter class="solr.PorterStemFilterFactory"/>
            </analyzer>
        </fieldType>

        <!-- charFilter + WhitespaceTokenizer  -->
        <!--
        <fieldType name="text_char_norm" class="solr.TextField" positionIncrementGap="100" >
          <analyzer>
            <charFilter class="solr.MappingCharFilterFactory" mapping="mapping-ISOLatin1Accent.txt"/>
            <tokenizer class="solr.WhitespaceTokenizerFactory"/>
          </analyzer>
        </fieldType>
        -->

        <!-- This is an example of using the KeywordTokenizer along
             With various TokenFilterFactories to produce a sortable field
             that does not include some properties of the source text
          -->
        <fieldType name="alphaOnlySort" class="solr.TextField" sortMissingLast="true" omitNorms="true">
            <analyzer>
                <!-- KeywordTokenizer does no actual tokenizing, so the entire
                     input string is preserved as a single token
                  -->
                <tokenizer class="solr.KeywordTokenizerFactory"/>
                <!-- The LowerCase TokenFilter does what you expect, which can be
                     when you want your sorting to be case insensitive
                  -->
                <filter class="solr.LowerCaseFilterFactory"/>
                <!-- The TrimFilter removes any leading or trailing whitespace -->
                <filter class="solr.TrimFilterFactory"/>
                <!-- The PatternReplaceFilter gives you the flexibility to use
                     Java Regular expression to replace any sequence of characters
                     matching a pattern with an arbitrary replacement string,
                     which may include back references to portions of the original
                     string matched by the pattern.

                     See the Java Regular Expression documentation for more
                     information on pattern and replacement string syntax.

                     http://java.sun.com/j2se/1.6.0/docs/api/java/util/regex/package-summary.html
                  -->
                <filter class="solr.PatternReplaceFilterFactory"
                        pattern="([^a-z])" replacement="" replace="all"
                        />
            </analyzer>
        </fieldType>

        <fieldType name="payloads_path" class="solr.TextField" positionIncrementGap="100">
          <analyzer type="index">
          <charFilter class="solr.PatternReplaceCharFilterFactory" pattern="\|.*" replacement=""/>
          <charFilter class="solr.PatternReplaceCharFilterFactory" pattern="," replacement=" "/>
            <tokenizer class="solr.WhitespaceTokenizerFactory"/>
          </analyzer>
          <analyzer type="query">
             <tokenizer class="solr.WhitespaceTokenizerFactory" />
          </analyzer>
        </fieldType>


        <!-- For the time being, we'll just dispense with the payload data at least
             until morning -->
        <fieldType name="payloads_bak1" class="solr.TextField" positionIncrementGap="100">
          <analyzer type="index">
          <charFilter class="solr.PatternReplaceCharFilterFactory" pattern="\|.*" replacement=""/>
            <tokenizer class="solr.PathHierarchyTokenizerFactory" delimiter="/"/>
          </analyzer>
          <analyzer type="query">
             <tokenizer class="solr.KeywordTokenizerFactory" />
          </analyzer>
        </fieldType>

        <fieldtype name="payloads" stored="false" indexed="true" class="solr.TextField">
            <analyzer>
                <tokenizer class="solr.WhitespaceTokenizerFactory"/>
                <!--
                The DelimitedPayloadTokenFilter can put payloads on tokens... for example,
                a token of "foo|1.4"  would be indexed as "foo" with a payload of 1.4f
                Attributes of the DelimitedPayloadTokenFilterFactory :
                 "delimiter" - a one character delimiter. Default is | (pipe)
             "encoder" - how to encode the following value into a playload
                float -> org.apache.lucene.analysis.payloads.FloatEncoder,
                integer -> o.a.l.a.p.IntegerEncoder
                identity -> o.a.l.a.p.IdentityEncoder
                    Fully Qualified class name implementing PayloadEncoder, Encoder must have a no arg constructor.
                 -->
                <filter class="solr.DelimitedPayloadTokenFilterFactory" encoder="float"/>
            </analyzer>
        </fieldtype>

        <!-- lowercases the entire field value, keeping it as a single token.  -->
        <fieldType name="lowercase" class="solr.TextField" positionIncrementGap="100">
            <analyzer>
                <tokenizer class="solr.KeywordTokenizerFactory"/>
                <filter class="solr.LowerCaseFilterFactory"/>
            </analyzer>
        </fieldType>

        <!-- since fields of this type are by default not stored or indexed,
             any data added to them will be ignored outright.  -->
        <fieldtype name="ignored" stored="false" indexed="false" multiValued="true" class="solr.StrField"/>

    </types>

    <!-- Similarity is the scoring routine for each document vs. a query.
         A custom Similarity or SimilarityFactory may be specified here, but
         the default is fine for most applications.
         For more info: http://wiki.apache.org/solr/SchemaXml#Similarity
      -->
    <!--
       <similarity class="com.example.solr.CustomSimilarityFactory">
         <str name="paramkey">param value</str>
       </similarity>
      -->

</schema>
"""