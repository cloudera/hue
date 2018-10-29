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
from django.urls import reverse

from nose.tools import assert_true, assert_false, assert_equal, assert_not_equal

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import grant_access
from desktop.lib.rest import resource
from desktop.models import Document2

from dashboard.facet_builder import _round_number_range
from dashboard.models import Collection2
from dashboard.controller import DashboardController


QUERY = {'qs': [{'q': ''}], 'fqs': [], 'start': 0}


def test_ranges():
  assert_equal((90, 100), _round_number_range(99))
  assert_equal((0, 100), _round_number_range(100))
  assert_equal((0, 100), _round_number_range(101))

  assert_equal((8000000, 9000000), _round_number_range(9045352))


class MockResource():
  RESPONSE = None

  def __init__(self, client):
    pass

  @classmethod
  def set_solr_response(cls, response):
    MockResource.RESPONSE = response

  def invoke(self, method, *args, **kwargs):
    if method.lower() == 'head':
      return self.head(*args, **kwargs)
    elif method.lower() == 'get':
      return self.get(*args, **kwargs)
    else:
      raise Exception('do not know how to handle %s' % method)

  def head(self, *args, **kwargs):
    return ''

  def get(self, *args, **kwargs):
    if 'collection_1/admin/file' in args[0]:
      return SOLR_SCHEMA
    elif 'collection_1/admin/luke' in args[0]:
      if ('show', 'schema') in kwargs['params']:
        return SOLR_LUKE_SCHEMA
      else:
        return SOLR_LUKE_
    else:
      return MockResource.RESPONSE


class TestSearchBase(object):

  def setUp(self):
    self.c = make_logged_in_client(username='test_search', is_superuser=False)
    self.client_not_me = make_logged_in_client(username="not_perm_user", groupname="default", recreate=True, is_superuser=False)

    self.user = User.objects.get(username='test_search')
    self.user_not_me = User.objects.get(username="not_perm_user")

    grant_access('test_search', 'test_search', 'search')
    grant_access(self.user.username, self.user.username, "desktop")
    grant_access('not_perm_user', 'not_perm_user', 'search')
    grant_access(self.user_not_me.username, self.user_not_me.username, "desktop")

    self.home_dir = Document2.objects.get_home_directory(user=self.user)

    self.prev_resource = resource.Resource
    resource.Resource = MockResource

    self.collection = Collection2(user=self.user, name='collection_1')

    MockResource.set_solr_response("""{
      "responseHeader": {
        "status": 0,
        "QTime": 0,
        "params": {
          "indent": "true",
          "q": "*:*",
          "_": "1442953203972",
          "wt": "json"
        }
      },
      "response": {
        "numFound": 1,
        "start": 0,
        "docs": [
          {
            "id": "change.me",
            "title": [
              "val1",
              "val2",
              "[val3]",
              "val4"
            ],
            "_version_": 1513046095083602000
          }
        ]
      }
      }""")

  def tearDown(self):
    # Remove monkey patching
    resource.Resource = self.prev_resource


class TestWithMockedSolr(TestSearchBase):

  def _get_collection_param(self, collection):
    col_json = json.loads(collection.get_json(self.user))
    return col_json['collection']

  def test_index(self):
    response = self.c.get(reverse('search:index'))
    assert_true('search' in response.content, response.content)

  def test_share_dashboard(self):
    doc = Document2.objects.create(name='test_dashboard', type='search-dashboard', owner=self.user,
                                   data=self.collection.data, parent_directory=self.home_dir)

    # owner can view document
    response = self.c.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert_equal(doc.uuid, data['document']['uuid'], data)

    # other user cannot view document
    response = self.client_not_me.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert_equal(-1, data['status'])

    # There are no collections with user_not_me
    search_controller = DashboardController(self.user_not_me)
    hue_collections = search_controller.get_search_collections()
    assert_true(len(hue_collections) == 0)

    # Share read perm by users
    response = self.c.post("/desktop/api2/doc/share", {
        'uuid': json.dumps(doc.uuid),
        'data': json.dumps({
            'read': {
                'user_ids': [
                    self.user.id,
                    self.user_not_me.id
                ],
                'group_ids': [],
            },
            'write': {
                'user_ids': [],
                'group_ids': [],
            }
        })
    })
    assert_equal(0, json.loads(response.content)['status'], response.content)
    assert_true(doc.can_read(self.user))
    assert_true(doc.can_write(self.user))
    assert_true(doc.can_read(self.user_not_me))
    assert_false(doc.can_write(self.user_not_me))

    # other user can view document
    response = self.client_not_me.get('/desktop/api2/doc/', {'uuid': doc.uuid})
    data = json.loads(response.content)
    assert_equal(doc.uuid, data['document']['uuid'], data)

    # other user can open dashboard
    response = self.c.post(reverse('search:search'), {
        'collection': json.dumps(self._get_collection_param(self.collection)),
        'query': json.dumps(QUERY)
    })

    data = json.loads(response.content)
    assert_true('response' in data, data)
    assert_true('docs' in data['response'], data)

    # For self.user_not_me
    search_controller = DashboardController(self.user_not_me)
    hue_collections = search_controller.get_search_collections()
    assert_equal(len(hue_collections), 1)
    assert_equal(hue_collections[0].name, 'test_dashboard')

    hue_collections = search_controller.get_owner_search_collections()
    assert_equal(len(hue_collections), 0)

    hue_collections = search_controller.get_shared_search_collections()
    assert_equal(len(hue_collections), 0)

    # For self.user
    search_controller = DashboardController(self.user)
    hue_collections = search_controller.get_search_collections()
    assert_equal(len(hue_collections), 1)
    assert_equal(hue_collections[0].name, 'test_dashboard')

    hue_collections = search_controller.get_owner_search_collections()
    assert_equal(len(hue_collections), 1)
    assert_equal(hue_collections[0].name, 'test_dashboard')

    hue_collections = search_controller.get_shared_search_collections()
    assert_equal(len(hue_collections), 1)
    assert_equal(hue_collections[0].name, 'test_dashboard')

    user_not_me_home_dir = Document2.objects.get_home_directory(user=self.user_not_me)
    doc1 = Document2.objects.create(name='test_dashboard1', type='search-dashboard', owner=self.user_not_me,
                                   data=self.collection.data, parent_directory=user_not_me_home_dir)
    # self.user_not_me can view document
    response = self.client_not_me.get('/desktop/api2/doc/', {'uuid': doc1.uuid})
    data = json.loads(response.content)
    assert_equal(doc1.uuid, data['document']['uuid'], data)

    # self.user cannot view document
    response = self.c.get('/desktop/api2/doc/', {'uuid': doc1.uuid})
    data = json.loads(response.content)
    assert_equal(-1, data['status'])

    # Share read perm by users
    response = self.client_not_me.post("/desktop/api2/doc/share", {
        'uuid': json.dumps(doc1.uuid),
        'data': json.dumps({
            'read': {
                'user_ids': [
                    self.user.id,
                ],
                'group_ids': [],
            },
            'write': {
                'user_ids': [],
                'group_ids': [],
            }
        })
    })
    assert_equal(0, json.loads(response.content)['status'], response.content)
    assert_true(doc1.can_read(self.user))
    assert_false(doc1.can_write(self.user))
    assert_true(doc1.can_read(self.user_not_me))
    assert_true(doc1.can_write(self.user_not_me))

    # For self.user_not_me
    search_controller = DashboardController(self.user_not_me)
    hue_collections = search_controller.get_search_collections()
    assert_equal(len(hue_collections), 2)

    hue_collections = search_controller.get_owner_search_collections()
    assert_equal(len(hue_collections), 1)
    assert_equal(hue_collections[0].name, 'test_dashboard1')

    hue_collections = search_controller.get_shared_search_collections()
    assert_equal(len(hue_collections), 1)
    assert_equal(hue_collections[0].name, 'test_dashboard1')

    # For self.user
    search_controller = DashboardController(self.user)
    hue_collections = search_controller.get_search_collections()
    assert_equal(len(hue_collections), 2)

    hue_collections = search_controller.get_owner_search_collections()
    assert_equal(len(hue_collections), 1)
    assert_equal(hue_collections[0].name, 'test_dashboard')

    hue_collections = search_controller.get_shared_search_collections()
    assert_equal(len(hue_collections), 1)
    assert_equal(hue_collections[0].name, 'test_dashboard')


  def test_update_document(self):
    # Regular user
    response = self.c.post(reverse('search:update_document'), {
        'collection': json.dumps(self._get_collection_param(self.collection)),
        'document': json.dumps({'hasChanged': False})
    })

    data = json.loads(response.content)
    assert_equal(0, data['status'], response.content)
    assert_true('no modifications to change' in data['message'], response.content)

    # Admin
    c = make_logged_in_client(username='admin', is_superuser=True, recreate=True)
    response = c.post(reverse('search:update_document'), {
        'collection': json.dumps(self._get_collection_param(self.collection)),
        'document': json.dumps({'hasChanged': False})
    })

    data = json.loads(response.content)
    assert_equal(0, data['status'], response.content)
    assert_true('no modifications to change' in data['message'], response.content)

  def test_strip_nulls(self):
    response = '{"uid":"1111111","method":"check_user"}\x00'
    response = json.loads(response.replace('\x00', '')) # Does not call real API

  def test_convert_schema_fields_to_luke(self):
    schema_fields = {u'fields': [
        {u'indexed': True, u'stored': True, u'type': u'long', u'name': u'_version_'},
        {u'indexed': True, u'stored': True, u'required': True, u'type': u'tdate', u'name': u'created_at'},
        {u'indexed': True, u'stored': True, u'required': True, u'type': u'string', u'name': u'expanded_url'},
        {u'uniqueKey': True, u'name': u'id', u'required': True, u'stored': True, u'indexed': True, u'type': u'tlong'},
        {u'indexed': True, u'stored': True, u'required': True, u'type': u'tlong', u'name': u'in_reply_to_status_id'},
        {u'indexed': True, u'stored': True, u'required': True, u'type': u'tint', u'name': u'in_reply_to_user_id'},
        {u'indexed': True, u'stored': True, u'required': True, u'type': u'string', u'name': u'media_url_https'},
        {u'indexed': True, u'stored': True, u'required': True, u'type': u'tint', u'name': u'retweet_count'},
        {u'indexed': True, u'stored': True, u'required': True, u'type': u'text_general', u'name': u'source'},
        {u'indexed': True, u'stored': True, u'required': True, u'type': u'text_general', u'name': u'text'},
        {u'indexed': True, u'stored': True, u'required': True, u'type': u'tint', u'name': u'user_followers_count'},
        {u'indexed': True, u'stored': True, u'required': True, u'type': u'tint', u'name': u'user_friends_count'},
        {u'indexed': True, u'stored': True, u'required': True, u'type': u'string', u'name': u'user_location'},
        {u'indexed': True, u'stored': True, u'required': True, u'type': u'text_general', u'name': u'user_name'},
        {u'indexed': True, u'stored': True, u'required': True, u'type': u'string', u'name': u'user_screen_name'},
        {u'indexed': True, u'stored': True, u'required': True, u'type': u'tint', u'name': u'user_statuses_count'}
        ], u'responseHeader': {u'status': 0, u'QTime': 1}
    }
    assert_equal([
        {'uniqueKey': None, 'copySources': [], 'flags': u'I-S-----OF-----l', 'required': True, 'type': u'long', u'copyDests': []},
        {'uniqueKey': None, 'copySources': [], 'flags': u'I-S-----OF-----l', 'required': True, 'type': u'string', u'copyDests': []},
        {'uniqueKey': None, 'copySources': [], 'flags': u'I-S-----OF-----l', 'required': True, 'type': u'string', u'copyDests': []},
        {'uniqueKey': None, 'copySources': [], 'flags': u'I-S-----OF-----l', 'required': True, 'type': u'string', u'copyDests': []},
        {'uniqueKey': None, 'copySources': [], 'flags': u'I-S-----OF-----l', 'required': True, 'type': u'string', u'copyDests': []},
        {'uniqueKey': None, 'copySources': [], 'flags': u'I-S-----OF-----l', 'required': True, 'type': u'tdate', u'copyDests': []},
        {'uniqueKey': None, 'copySources': [], 'flags': u'I-S-----OF-----l', 'required': True, 'type': u'text_general', u'copyDests': []},
        {'uniqueKey': None, 'copySources': [], 'flags': u'I-S-----OF-----l', 'required': True, 'type': u'text_general', u'copyDests': []},
        {'uniqueKey': None, 'copySources': [], 'flags': u'I-S-----OF-----l', 'required': True, 'type': u'text_general', u'copyDests': []},
        {'uniqueKey': None, 'copySources': [], 'flags': u'I-S-----OF-----l', 'required': True, 'type': u'tint', u'copyDests': []},
        {'uniqueKey': None, 'copySources': [], 'flags': u'I-S-----OF-----l', 'required': True, 'type': u'tint', u'copyDests': []},
        {'uniqueKey': None, 'copySources': [], 'flags': u'I-S-----OF-----l', 'required': True, 'type': u'tint', u'copyDests': []},
        {'uniqueKey': None, 'copySources': [], 'flags': u'I-S-----OF-----l', 'required': True, 'type': u'tint', u'copyDests': []},
        {'uniqueKey': None, 'copySources': [], 'flags': u'I-S-----OF-----l', 'required': True, 'type': u'tint', u'copyDests': []},
        {'uniqueKey': None, 'copySources': [], 'flags': u'I-S-----OF-----l', 'required': True, 'type': u'tlong', u'copyDests': []},
        {'uniqueKey': True, 'copySources': [], 'flags': u'I-S-----OF-----l', 'required': True, 'type': u'tlong', u'copyDests': []}
        ],
        sorted(Collection2._make_luke_from_schema_fields(schema_fields).values())
    )

  def test_response_escaping_multi_value(self):
    MockResource.set_solr_response("""{
      "responseHeader": {
        "status": 0,
        "QTime": 0,
        "params": {
          "indent": "true",
          "q": "*:*",
          "_": "1442953203972",
          "wt": "json"
        }
      },
      "response": {
        "numFound": 1,
        "start": 0,
        "docs": [
          {
            "id": "change.me",
            "title": [
              "val1",
              "val2",
              "[<script>alert(123)</script>]",
              "val4"
            ],
            "_version_": 1513046095083602000
          }
        ]
      }
    }""")

    response = self.c.post(reverse('search:search'), {
        'collection': json.dumps(self._get_collection_param(self.collection)),
        'query': json.dumps(QUERY)
    })

    result = json.loads(response.content)
    assert_equal(
        [{'hueId': 'change.me', 'id': 'change.me', '_version_': 1513046095083602000, 'title': ['val1', 'val2', '[&lt;script&gt;alert(123)&lt;/script&gt;]', 'val4'], 'details': [], 'externalLink': None}],
        result['response']['docs']
    )

  def test_response_with_facets(self):
    MockResource.set_solr_response("""{"responseHeader":{"status":0,"QTime":59,"params":{"facet":"true","facet.mincount":"1","facet.limit":"100","facet.date":"article_date","f.article_date.facet.date.start":"NOW-7MONTH/DAYS","wt":"json","rows":"15","user.name":"hue","start":"0","facet.sort":"count","q":"*:*","f.article_date.facet.date.end":"NOW-5MONTH","doAs":"romain","f.article_date.facet.date.gap":"+1DAYS","facet.field":["journal_title","author_facet"],"fq":["article_date:[2013-06-13T00:00:00Z TO 2013-06-13T00:00:00Z+1DAYS]","journal_title:\\"in\\""]}},"response":{"numFound":4,"start":0,"maxScore":1.0,"docs":[{"article_title":"Investigations for neonatal seizures.","journal_issn":"1878-0946","article_abstract_text":["Seizures during the neonatal period are always medical emergencies. Apart from the need for rapid anticonvulsive treatment, the underlying condition is often not immediately obvious. In the search for the correct diagnosis, a thorough history, clinical examination, laboratory work-up, neurophysiological and neuroradiological investigations are all essential. A close collaboration between neonatologists, neuropaediatricians, laboratory specialists, neurophysiologists and radiologists facilitates the adequate care of the infant."],"ontologies":["36481|1 "],"article_date":"2013-06-13T00:00:00Z","journal_title":"Seminars in fetal & neonatal medicine","date_created":"2013-08-22T00:00:00Z","journal_country":"Netherlands","journal_iso_abbreviation":"Semin Fetal Neonatal Med","id":"23680099","author":["B B Hallberg","M M Blennow"],"article_pagination":"196-201","journal_publication_date":"2013-08-22T00:00:00Z","affiliation":"Department of Neonatology, Karolinska Institutet and University Hospital, Stockholm, Sweden. boubou.hallberg@ki.se","language":"eng","_version_":1450807641462800385},{"article_title":"Enantiomeric selection properties of β-homoDNA: enhanced pairing for heterochiral complexes.","journal_issn":"1521-3773","article_date":"2013-06-13T00:00:00Z","journal_title":"Angewandte Chemie (International ed. in English)","date_created":"2013-07-20T00:00:00Z","journal_country":"Germany","journal_iso_abbreviation":"Angew. Chem. Int. Ed. Engl.","id":"23670912","author":["Daniele D D'Alonzo","Jussara J Amato","Guy G Schepers","Matheus M Froeyen","Arthur A Van Aerschot","Piet P Herdewijn","Annalisa A Guaragna"],"article_pagination":"6662-5","journal_publication_date":"2013-06-24T00:00:00Z","affiliation":"Dipartimento di Scienze Chimiche, Università degli Studi di Napoli Federico II, Via Cintia 21, 80126 Napoli, Italy. dandalonzo@unina.it","language":"eng","_version_":1450807661929955329},{"article_title":"Interference of bacterial cell-to-cell communication: a new concept of antimicrobial chemotherapy breaks antibiotic resistance.","journal_issn":"1664-302X","article_abstract_text":["Bacteria use a cell-to-cell communication activity termed \\"quorum sensing\\" to coordinate group behaviors in a cell density dependent manner. Quorum sensing influences the expression profile of diverse genes, including antibiotic tolerance and virulence determinants, via specific chemical compounds called \\"autoinducers\\". During quorum sensing, Gram-negative bacteria typically use an acylated homoserine lactone (AHL) called autoinducer 1. Since the first discovery of quorum sensing in a marine bacterium, it has been recognized that more than 100 species possess this mechanism of cell-to-cell communication. In addition to being of interest from a biological standpoint, quorum sensing is a potential target for antimicrobial chemotherapy. This unique concept of antimicrobial control relies on reducing the burden of virulence rather than killing the bacteria. It is believed that this approach will not only suppress the development of antibiotic resistance, but will also improve the treatment of refractory infections triggered by multi-drug resistant pathogens. In this paper, we review and track recent progress in studies on AHL inhibitors/modulators from a biological standpoint. It has been discovered that both natural and synthetic compounds can disrupt quorum sensing by a variety of means, such as jamming signal transduction, inhibition of signal production and break-down and trapping of signal compounds. We also focus on the regulatory elements that attenuate quorum sensing activities and discuss their unique properties. Understanding the biological roles of regulatory elements might be useful in developing inhibitor applications and understanding how quorum sensing is controlled."],"ontologies":["2402|1 ","1875|1 ","2047|3 ","36690|1 ","8120|1 ","1872|1 ","1861|1 ","1955|2 ","38027|1 ","3853|1 ","2237|3 ","37074|1 ","3043|2 ","36478|1 ","4403|1 ","2751|1 ","10751|1 ","36467|1 ","2387|1 ","7278|3 ","3826|1 "],"article_date":"2013-06-13T00:00:00Z","journal_title":"Frontiers in microbiology","date_created":"2013-06-30T00:00:00Z","journal_country":"Switzerland","journal_iso_abbreviation":"Front Microbiol","id":"23720655","author":["Hidetada H Hirakawa","Haruyoshi H Tomita"],"article_pagination":"114","journal_publication_date":"2013-09-13T00:00:00Z","affiliation":"Advanced Scientific Research Leaders Development Unit, Gunma University Maebashi, Gunma, Japan.","language":"eng","_version_":1450807662055784448},{"article_title":"The role of musical training in emergent and event-based timing.","journal_issn":"1662-5161","article_abstract_text":["Introduction: Musical performance is thought to rely predominantly on event-based timing involving a clock-like neural process and an explicit internal representation of the time interval. Some aspects of musical performance may rely on emergent timing, which is established through the optimization of movement kinematics, and can be maintained without reference to any explicit representation of the time interval. We predicted that musical training would have its largest effect on event-based timing, supporting the dissociability of these timing processes and the dominance of event-based timing in musical performance. Materials and Methods: We compared 22 musicians and 17 non-musicians on the prototypical event-based timing task of finger tapping and on the typically emergently timed task of circle drawing. For each task, participants first responded in synchrony with a metronome (Paced) and then responded at the same rate without the metronome (Unpaced). Results: Analyses of the Unpaced phase revealed that non-musicians were more variable in their inter-response intervals for finger tapping compared to circle drawing. Musicians did not differ between the two tasks. Between groups, non-musicians were more variable than musicians for tapping but not for drawing. We were able to show that the differences were due to less timer variability in musicians on the tapping task. Correlational analyses of movement jerk and inter-response interval variability revealed a negative association for tapping and a positive association for drawing in non-musicians only. Discussion: These results suggest that musical training affects temporal variability in tapping but not drawing. Additionally, musicians and non-musicians may be employing different movement strategies to maintain accurate timing in the two tasks. These findings add to our understanding of how musical training affects timing and support the dissociability of event-based and emergent timing modes."],"ontologies":["36810|1 ","49002|1 ","3132|1 ","3797|1 ","37953|1 ","36563|2 ","524|1 ","3781|1 ","2848|1 ","17163|1 ","17165|1 ","49010|1 ","36647|3 ","36529|1 ","2936|1 ","2643|1 ","714|1 ","3591|1 ","2272|1 ","3103|1 ","2265|1 ","37051|1 ","3691|1 "],"article_date":"2013-06-14T00:00:00Z","journal_title":"Frontiers in human neuroscience","date_created":"2013-06-29T00:00:00Z","journal_country":"Switzerland","journal_iso_abbreviation":"Front Hum Neurosci","id":"23717275","author":["L H LH Baer","J L N JL Thibodeau","T M TM Gralnick","K Z H KZ Li","V B VB Penhune"],"article_pagination":"191","journal_publication_date":"2013-09-13T00:00:00Z","affiliation":"Department of Psychology, Centre for Research in Human Development, Concordia University Montréal, QC, Canada.","language":"eng","_version_":1450807667479019520}]},"facet_counts":{"facet_queries":{},"facet_fields":{"journal_title":["in",4,"frontiers",2,"angewandte",1,"chemie",1,"ed",1,"english",1,"fetal",1,"human",1,"international",1,"medicine",1,"microbiology",1,"neonatal",1,"neuroscience",1,"seminars",1],"author_facet":["Annalisa A Guaragna",1,"Arthur A Van Aerschot",1,"B B Hallberg",1,"Daniele D D'Alonzo",1,"Guy G Schepers",1,"Haruyoshi H Tomita",1,"Hidetada H Hirakawa",1,"J L N JL Thibodeau",1,"Jussara J Amato",1,"K Z H KZ Li",1,"L H LH Baer",1,"M M Blennow",1,"Matheus M Froeyen",1,"Piet P Herdewijn",1,"T M TM Gralnick",1,"V B VB Penhune",1]},"facet_dates":{"article_date":{"gap":"+1DAYS","start":"2013-04-27T00:00:00Z","end":"2013-06-28T00:00:00Z"}},"facet_ranges":{}},"highlighting":{"23680099":{},"23670912":{},"23720655":{},"23717275":{}},"spellcheck":{"suggestions":["correctlySpelled",false]}}""")

    # journal_title facet + date range article_date facets clicked and author_facet not clicked
    # http://solr:8983/solr/articles/select?user.name=hue&doAs=romain&q=%2A%3A%2A&wt=json&rows=15&start=0&facet=true&facet.mincount=1&facet.limit=100&facet.sort=count&facet.field=journal_title&facet.field=author_facet&facet.date=article_date&f.article_date.facet.date.start=NOW-7MONTH%2FDAYS&f.article_date.facet.date.end=NOW-5MONTH&f.article_date.facet.date.gap=%2B1DAYS&fq=article_date%3A%5B2013-06-13T00%3A00%3A00Z+TO+2013-06-13T00%3A00%3A00Z%2B1DAYS%5D&fq=journal_title%3A%22in%22
    response = self.c.post(reverse('search:search'), {
        'collection': json.dumps(self._get_collection_param(self.collection)),
        'query': json.dumps(QUERY)
    })

    assert_false('alert alert-error' in response.content, response.content)

    assert_true('author_facet' in response.content, response.content)
    assert_true('Annalisa A Guaragna' in response.content, response.content)

    assert_true('journal_title' in response.content, response.content)
    assert_true('Angewandte' in response.content, response.content)

    assert_true('"numFound": 4' in response.content, response.content)

  def test_response_highlighting_with_binary_value(self):
    MockResource.set_solr_response("""{"responseHeader":{"status":0,"QTime":23,"params":{"hl.fragsize":"1000","fl":"*","hl.snippets":"5","start":"0","user.name":"hue","q":"*:*","doAs":"romain","hl.fl":"*","wt":"json","hl":"true","rows":"2"}},"response":{"numFound":494,"start":0,"docs":[{"id":"#31;�#8;w)�U#3;333320442�#2;�#27;�v","last_name":"Ogh","gpa":"3.88","first_name":"Eirjish","age":"12","_version_":1508697786597507072},{"id":"#31;�#8;w)�U#3;344�457�4�#2;r��","last_name":"Ennjth","gpa":"1.22","first_name":"Oopob","age":"14","_version_":1508697786815610880}]},"facet_counts":{"facet_queries":{},"facet_fields":{"id":["31",485,"8",485,"u",485,"2",461,"x",308,"w",145,"3",123,"4",90,"3;3",81,"0",76,"y",46,"41",15,"16",14,"42",14,"05",12,"7",12,"04",11,"15",11,"3;31",11,"44",11,"45",11,"i",11,"n",11,"s",11,"03",10,"07",10,"11",10,"28",10,"30",10,"3;34",10,"46",10,"a",10,"c",10,"j",10,"v",10,"02",9,"1",9,"26",9,"6",9,"e",9,"f",9,"p",9,"z",9,"00",8,"06",8,"14",8,"43",8,"g",8,"h",8,"r",8,"20",7,"23",7,"29",7,"3;37",7,"40",7,"k",7,"01",6,"17",6,"22",6,"24",6,"27",6,"3;35",6,"3;36",6,"b",6,"12",5,"19",5,"21",5,"3;323",5,"3;33",5,"47",5,"5",5,"o",5,"18",4,"25",4,"2;6",4,"3;32",4,"3;360",4,"3;372",4,"d",4,"q",4,"t",4,"005",3,"2;3",3,"3;311",3,"3;343",3,"3;344",3,"3;373",3,"420",3,"471",3,"9",3,"l",3,"m",3,"0147",2,"020",2,"022",2,"031",2,"065",2,"070",2,"2;0",2,"2;5",2],"first_name":["unt",3,"at",2,"aut",2,"eigh",2,"jh",2,"jir",2,"jz",2,"oim",2,"oith",2,"onn",2,"ouz",2,"um",2,"veitt",2,"16",1,"21",1,"28",1,"30",1,"achunn",1,"ad",1,"agauz",1,"agur",1,"aibenn",1,"aich",1,"aichaum",1,"aigh",1,"aim",1,"aimoob",1,"ainn",1,"aipf",1,"aipfouv",1,"aisainn",1,"aistjs",1,"aith",1,"aitoum",1,"aittool",1,"aittoupf",1,"aiw",1,"ak",1,"al",1,"apf",1,"astjist",1,"ataiv",1,"att",1,"auchav",1,"auchib",1,"auchih",1,"aud",1,"audaush",1,"auh",1,"auhour",1,"aum",1,"aunnoiss",1,"aunopf",1,"aupev",1,"aus",1,"ausaust",1,"austour",1,"ausyv",1,"auth",1,"authep",1,"auttjich",1,"auttjir",1,"av",1,"besooz",1,"bjfautt",1,"bjichaub",1,"bjittyl",1,"bjtoopf",1,"bleiss",1,"blistoot",1,"blittaub",1,"bljip",1,"bljir",1,"bloich",1,"bluhaid",1,"bluth",1,"breirjd",1,"breiter",1,"breitt",1,"breth",1,"brjishaip",1,"broil",1,"broopfoul",1,"brooputt",1,"brooroog",1,"brot",1,"brych",1,"brykaub",1,"brypfop",1,"bunn",1,"byroigh",1,"c",1,"caugh",1,"cautt",1,"chaittoif",1,"chaupour",1,"chautoonn",1,"chech",1,"cheigh",1,"chet",1],"last_name":["it",3,"ooz",3,"yss",3,"aih",2,"aim",2,"ash",2,"foum",2,"ig",2,"jch",2,"jif",2,"jis",2,"jiv",2,"jiw",2,"js",2,"oh",2,"ouf",2,"uch",2,"ud",2,"uf",2,"ul",2,"ush",2,"ys",2,"ab",1,"ach",1,"afoust",1,"aghaush",1,"aib",1,"aihjiss",1,"aimoint",1,"ain",1,"aineip",1,"ainn",1,"aint",1,"aintuf",1,"aipfes",1,"aipfjf",1,"air",1,"aish",1,"aishoott",1,"aishutt",1,"aisjnn",1,"aisseih",1,"aissutt",1,"aistaif",1,"aith",1,"aithjib",1,"aiv",1,"aiw",1,"aiz",1,"aizyb",1,"alyk",1,"ap",1,"apf",1,"apount",1,"assyv",1,"ast",1,"at",1,"atook",1,"att",1,"audal",1,"aug",1,"auk",1,"auloost",1,"aupfoitt",1,"aupjish",1,"aur",1,"aus",1,"authood",1,"auttyst",1,"auvjb",1,"auvon",1,"auzigh",1,"az",1,"besh",1,"birus",1,"bjit",1,"bjz",1,"blaich",1,"blaipf",1,"bleiz",1,"blikjigh",1,"bloob",1,"blouth",1,"boobjist",1,"boontoih",1,"boub",1,"bouch",1,"braul",1,"braut",1,"breinnyz",1,"brishoog",1,"brithith",1,"brjint",1,"brjth",1,"brubeist",1,"brugh",1,"bryvaip",1,"byl",1,"caleid",1,"ceir",1],"age":["12",60,"18",57,"14",56,"10",54,"11",53,"13",52,"16",50,"15",49,"17",44],"gpa":["2.34",6,"1.01",5,"1.43",5,"3.04",5,"3.14",5,"3.17",5,"3.87",5,"1.61",4,"2.24",4,"2.73",4,"2.76",4,"2.97",4,"3.28",4,"3.29",4,"3.35",4,"3.39",4,"3.67",4,"3.78",4,"3.85",4,"1.05",3,"1.1",3,"1.13",3,"1.22",3,"1.25",3,"1.3",3,"1.34",3,"1.37",3,"1.38",3,"1.39",3,"1.4",3,"1.44",3,"1.46",3,"1.53",3,"1.54",3,"1.55",3,"1.67",3,"1.72",3,"1.82",3,"1.91",3,"1.93",3,"11.0",3,"2.09",3,"2.11",3,"2.23",3,"2.26",3,"2.29",3,"2.46",3,"2.62",3,"2.71",3,"2.78",3,"2.79",3,"2.83",3,"2.84",3,"2.85",3,"2.92",3,"3.09",3,"3.11",3,"3.13",3,"3.23",3,"3.44",3,"3.76",3,"3.82",3,"3.88",3,"3.89",3,"3.92",3,"3.97",3,"4.0",3,"1.02",2,"1.11",2,"1.23",2,"1.26",2,"1.28",2,"1.35",2,"1.48",2,"1.56",2,"1.59",2,"1.63",2,"1.79",2,"1.8",2,"1.81",2,"1.97",2,"16.0",2,"2.01",2,"2.03",2,"2.05",2,"2.08",2,"2.12",2,"2.14",2,"2.17",2,"2.2",2,"2.25",2,"2.3",2,"2.35",2,"2.36",2,"2.41",2,"2.47",2,"2.49",2,"2.51",2,"2.54",2,"2.56",2],"date1":[],"date2":[],"country":[],"state":[],"city":[],"latitude":[],"longitude":[]},"facet_dates":{},"facet_ranges":{},"facet_intervals":{}},"highlighting":{"#31;�#8;w)�U#3;333320442�#2;�#27;�v":{},"#31;�#8;w)�U#3;344�457�4�#2;r��":{}}}""")

    response = self.c.post(reverse('search:search'), {
        'collection': json.dumps(self._get_collection_param(self.collection)),
        'query': json.dumps(QUERY)
    })

    assert_false('alert alert-error' in response.content, response.content)
    assert_false("'ascii' codec can't encode character u'\ufffd' in position" in response.content, response.content)

    assert_true('bluhaid' in response.content, response.content)

  def test_get_collection_fields(self):
    MockResource.set_solr_response("""{"responseHeader":{"status":0,"QTime":8},"index":{"numDocs":8,"maxDoc":8,"deletedDocs":0,"version":15,"segmentCount":5,"current":true,"hasDeletions":false,"directory":"org.apache.lucene.store.NRTCachingDirectory:NRTCachingDirectory(org.apache.solr.store.hdfs.HdfsDirectory@5efe087b lockFactory=org.apache.solr.store.hdfs.HdfsLockFactory@5106def2; maxCacheMB=192.0 maxMergeSizeMB=16.0)","userData":{"commitTimeMSec":"1389233070579"},"lastModified":"2014-01-09T02:04:30.579Z"},"fields":{"_version_":{"type":"long","schema":"ITS-----OF------","index":"-TS-------------","docs":8,"distinct":8,"topTerms":["1456716393276768256",1,"1456716398067712000",1,"1456716401465098240",1,"1460689159964327936",1,"1460689159981105152",1,"1460689159988445184",1,"1460689159993688064",1,"1456716273606983680",1],"histogram":["1",8]},"cat":{"type":"string","schema":"I-S-M---OF-----l","index":"ITS-----OF------","docs":4,"distinct":1,"topTerms":["currency",4],"histogram":["1",0,"2",0,"4",1]},"features":{"type":"text_general","schema":"ITS-M-----------","index":"ITS-------------","docs":4,"distinct":3,"topTerms":["coins",4,"notes",4,"and",4],"histogram":["1",0,"2",0,"4",3]},"id":{"type":"string","schema":"I-S-----OF-----l","index":"ITS-----OF------","docs":8,"distinct":8,"topTerms":["GBP",1,"NOK",1,"USD",1,"change.me",1,"change.me1",1,"change.me112",1,"change.me12",1,"EUR",1],"histogram":["1",8]},"inStock":{"type":"boolean","schema":"I-S-----OF-----l","index":"ITS-----OF------","docs":4,"distinct":1,"topTerms":["true",4],"histogram":["1",0,"2",0,"4",1]},"manu":{"type":"text_general","schema":"ITS-----O-------","index":"ITS-----O-------","docs":4,"distinct":7,"topTerms":["of",2,"bank",2,"european",1,"norway",1,"u.k",1,"union",1,"america",1],"histogram":["1",5,"2",2]},"manu_exact":{"type":"string","schema":"I-------OF-----l","index":"(unstored field)","docs":4,"distinct":4,"topTerms":["Bank of Norway",1,"European Union",1,"U.K.",1,"Bank of America",1],"histogram":["1",4]},"manu_id_s":{"type":"string","schema":"I-S-----OF-----l","dynamicBase":"*_s","index":"ITS-----OF------","docs":4,"distinct":4,"topTerms":["eu",1,"nor",1,"uk",1,"boa",1],"histogram":["1",4]},"name":{"type":"text_general","schema":"ITS-------------","index":"ITS-------------","docs":4,"distinct":6,"topTerms":["one",4,"euro",1,"krone",1,"dollar",1,"pound",1,"british",1],"histogram":["1",5,"2",0,"4",1]},"price_c":{"type":"currency","schema":"I-S------F------","dynamicBase":"*_c"},"price_c____amount_raw":{"type":"amount_raw_type_tlong","schema":"IT------O-------","dynamicBase":"*____amount_raw","index":"(unstored field)","docs":4,"distinct":8,"topTerms":["0",4,"0",4,"0",4,"0",4,"0",4,"0",4,"0",4,"100",4],"histogram":["1",0,"2",0,"4",8]},"price_c____currency":{"type":"currency_type_string","schema":"I-------O-------","dynamicBase":"*____currency","index":"(unstored field)","docs":4,"distinct":4,"topTerms":["GBP",1,"NOK",1,"USD",1,"EUR",1],"histogram":["1",4]},"romain_t":{"type":"text_general","schema":"ITS-------------","dynamicBase":"*_t","index":"ITS-------------","docs":1,"distinct":1,"topTerms":["true",1],"histogram":["1",1]},"text":{"type":"text_general","schema":"IT--M-----------","index":"(unstored field)","docs":8,"distinct":21,"topTerms":["and",4,"currency",4,"notes",4,"one",4,"coins",4,"bank",2,"of",2,"change.me112",1,"change.me1",1,"change.me",1],"histogram":["1",14,"2",2,"4",5]},"title":{"type":"text_general","schema":"ITS-M-----------","index":"ITS-------------","docs":4,"distinct":4,"topTerms":["change.me1",1,"change.me112",1,"change.me12",1,"change.me",1],"histogram":["1",4]}},"info":{"key":{"I":"Indexed","T":"Tokenized","S":"Stored","D":"DocValues","M":"Multivalued","V":"TermVector Stored","o":"Store Offset With TermVector","p":"Store Position With TermVector","O":"Omit Norms","F":"Omit Term Frequencies & Positions","P":"Omit Positions","H":"Store Offsets with Positions","L":"Lazy","B":"Binary","f":"Sort Missing First","l":"Sort Missing Last"},"NOTE":"Document Frequency (df) is not updated when a document is marked for deletion.  df values include deleted documents."}}""")

    assert_equal(
        # Dynamic fields not included for now
        [{'isDynamic': False, 'isId': None, 'type': 'string', 'name': '&lt;script&gt;alert(1234)&lt;/script&gt;'},
         {'isDynamic': False, 'isId': None, 'type': 'long', 'name': '_version_'},
         {'isDynamic': False, 'isId': None, 'type': 'text_general', 'name': 'author'},
         {'isDynamic': False, 'isId': None, 'type': 'text_general', 'name': 'category'},
         {'isDynamic': False, 'isId': None, 'type': 'text_general', 'name': 'comments'},
         {'isDynamic': False, 'isId': None, 'type': 'text_general', 'name': 'content'},
         {'isDynamic': False, 'isId': None, 'type': 'string', 'name': 'content_type'},
         {'isDynamic': False, 'isId': None, 'type': 'text_general', 'name': 'description'},
         {'isDynamic': False, 'isId': None, 'type': 'text_general', 'name': 'features'},
         {'isDynamic': False, 'isId': None, 'type': 'boolean', 'name': 'inStock'},
         {'isDynamic': False, 'isId': None, 'type': 'text_general', 'name': 'includes'},
         {'isDynamic': False, 'isId': None, 'type': 'text_general', 'name': 'keywords'},
         {'isDynamic': False, 'isId': None, 'type': 'date', 'name': 'last_modified'},
         {'isDynamic': False, 'isId': None, 'type': 'string', 'name': 'links'},
         {'isDynamic': False, 'isId': None, 'type': 'text_general', 'name': 'manu'},
         {'isDynamic': False, 'isId': None, 'type': 'string', 'name': 'manu_exact'},
         {'isDynamic': False, 'isId': None, 'type': 'text_general', 'name': 'name'},
         {'isDynamic': False, 'isId': None, 'type': 'payloads', 'name': 'payloads'},
         {'isDynamic': False, 'isId': None, 'type': 'int', 'name': 'popularity'},
         {'isDynamic': False, 'isId': None, 'type': 'float', 'name': 'price'},
         {'isDynamic': False, 'isId': None, 'type': 'text_general', 'name': 'resourcename'},
         {'isDynamic': False, 'isId': None, 'type': 'text_en_splitting_tight', 'name': 'sku'},
         {'isDynamic': False, 'isId': None, 'type': 'location', 'name': 'store'},
         {'isDynamic': False, 'isId': None, 'type': 'text_general', 'name': 'subject'},
         {'isDynamic': False, 'isId': None, 'type': 'text_general', 'name': 'text'},
         {'isDynamic': False, 'isId': None, 'type': 'text_general_rev', 'name': 'text_rev'},
         {'isDynamic': False, 'isId': None, 'type': 'text_general', 'name': 'title'},
         {'isDynamic': False, 'isId': None, 'type': 'text_general', 'name': 'url'},
         {'isDynamic': False, 'isId': None, 'type': 'float', 'name': 'weight'},
         {'isDynamic': False, 'isId': True, 'type': 'string', 'name': 'id'}],
         self.collection.fields_data(self.user, 'collection_1')
    )

  # TODO
  # test facet with userlocation: türkiye, 東京, new york

  def test_download(self):
    MockResource.set_solr_response("""{"responseHeader":{"status":0,"QTime":59,"params":{"facet":"true","facet.mincount":"1","facet.limit":"100","facet.date":"article_date","f.article_date.facet.date.start":"NOW-7MONTH/DAYS","wt":"json","rows":"15","user.name":"hue","start":"0","facet.sort":"count","q":"*:*","f.article_date.facet.date.end":"NOW-5MONTH","doAs":"romain","f.article_date.facet.date.gap":"+1DAYS","facet.field":["journal_title","author_facet"],"fq":["article_date:[2013-06-13T00:00:00Z TO 2013-06-13T00:00:00Z+1DAYS]","journal_title:\\"in\\""]}},"response":{"numFound":4,"start":0,"maxScore":1.0,"docs":[{"article_title":"Investigations for neonatal seizures.","journal_issn":"1878-0946","article_abstract_text":["Seizures during the neonatal period are always medical emergencies. Apart from the need for rapid anticonvulsive treatment, the underlying condition is often not immediately obvious. In the search for the correct diagnosis, a thorough history, clinical examination, laboratory work-up, neurophysiological and neuroradiological investigations are all essential. A close collaboration between neonatologists, neuropaediatricians, laboratory specialists, neurophysiologists and radiologists facilitates the adequate care of the infant."],"ontologies":["36481|1 "],"article_date":"2013-06-13T00:00:00Z","journal_title":"Seminars in fetal & neonatal medicine","date_created":"2013-08-22T00:00:00Z","journal_country":"Netherlands","journal_iso_abbreviation":"Semin Fetal Neonatal Med","id":"23680099","author":["B B Hallberg","M M Blennow"],"article_pagination":"196-201","journal_publication_date":"2013-08-22T00:00:00Z","affiliation":"Department of Neonatology, Karolinska Institutet and University Hospital, Stockholm, Sweden. boubou.hallberg@ki.se","language":"eng","_version_":1450807641462800385},{"article_title":"Enantiomeric selection properties of β-homoDNA: enhanced pairing for heterochiral complexes.","journal_issn":"1521-3773","article_date":"2013-06-13T00:00:00Z","journal_title":"Angewandte Chemie (International ed. in English)","date_created":"2013-07-20T00:00:00Z","journal_country":"Germany","journal_iso_abbreviation":"Angew. Chem. Int. Ed. Engl.","id":"23670912","author":["Daniele D D'Alonzo","Jussara J Amato","Guy G Schepers","Matheus M Froeyen","Arthur A Van Aerschot","Piet P Herdewijn","Annalisa A Guaragna"],"article_pagination":"6662-5","journal_publication_date":"2013-06-24T00:00:00Z","affiliation":"Dipartimento di Scienze Chimiche, Università degli Studi di Napoli Federico II, Via Cintia 21, 80126 Napoli, Italy. dandalonzo@unina.it","language":"eng","_version_":1450807661929955329},{"article_title":"Interference of bacterial cell-to-cell communication: a new concept of antimicrobial chemotherapy breaks antibiotic resistance.","journal_issn":"1664-302X","article_abstract_text":["Bacteria use a cell-to-cell communication activity termed \\"quorum sensing\\" to coordinate group behaviors in a cell density dependent manner. Quorum sensing influences the expression profile of diverse genes, including antibiotic tolerance and virulence determinants, via specific chemical compounds called \\"autoinducers\\". During quorum sensing, Gram-negative bacteria typically use an acylated homoserine lactone (AHL) called autoinducer 1. Since the first discovery of quorum sensing in a marine bacterium, it has been recognized that more than 100 species possess this mechanism of cell-to-cell communication. In addition to being of interest from a biological standpoint, quorum sensing is a potential target for antimicrobial chemotherapy. This unique concept of antimicrobial control relies on reducing the burden of virulence rather than killing the bacteria. It is believed that this approach will not only suppress the development of antibiotic resistance, but will also improve the treatment of refractory infections triggered by multi-drug resistant pathogens. In this paper, we review and track recent progress in studies on AHL inhibitors/modulators from a biological standpoint. It has been discovered that both natural and synthetic compounds can disrupt quorum sensing by a variety of means, such as jamming signal transduction, inhibition of signal production and break-down and trapping of signal compounds. We also focus on the regulatory elements that attenuate quorum sensing activities and discuss their unique properties. Understanding the biological roles of regulatory elements might be useful in developing inhibitor applications and understanding how quorum sensing is controlled."],"ontologies":["2402|1 ","1875|1 ","2047|3 ","36690|1 ","8120|1 ","1872|1 ","1861|1 ","1955|2 ","38027|1 ","3853|1 ","2237|3 ","37074|1 ","3043|2 ","36478|1 ","4403|1 ","2751|1 ","10751|1 ","36467|1 ","2387|1 ","7278|3 ","3826|1 "],"article_date":"2013-06-13T00:00:00Z","journal_title":"Frontiers in microbiology","date_created":"2013-06-30T00:00:00Z","journal_country":"Switzerland","journal_iso_abbreviation":"Front Microbiol","id":"23720655","author":["Hidetada H Hirakawa","Haruyoshi H Tomita"],"article_pagination":"114","journal_publication_date":"2013-09-13T00:00:00Z","affiliation":"Advanced Scientific Research Leaders Development Unit, Gunma University Maebashi, Gunma, Japan.","language":"eng","_version_":1450807662055784448},{"article_title":"The role of musical training in emergent and event-based timing.","journal_issn":"1662-5161","article_abstract_text":["Introduction: Musical performance is thought to rely predominantly on event-based timing involving a clock-like neural process and an explicit internal representation of the time interval. Some aspects of musical performance may rely on emergent timing, which is established through the optimization of movement kinematics, and can be maintained without reference to any explicit representation of the time interval. We predicted that musical training would have its largest effect on event-based timing, supporting the dissociability of these timing processes and the dominance of event-based timing in musical performance. Materials and Methods: We compared 22 musicians and 17 non-musicians on the prototypical event-based timing task of finger tapping and on the typically emergently timed task of circle drawing. For each task, participants first responded in synchrony with a metronome (Paced) and then responded at the same rate without the metronome (Unpaced). Results: Analyses of the Unpaced phase revealed that non-musicians were more variable in their inter-response intervals for finger tapping compared to circle drawing. Musicians did not differ between the two tasks. Between groups, non-musicians were more variable than musicians for tapping but not for drawing. We were able to show that the differences were due to less timer variability in musicians on the tapping task. Correlational analyses of movement jerk and inter-response interval variability revealed a negative association for tapping and a positive association for drawing in non-musicians only. Discussion: These results suggest that musical training affects temporal variability in tapping but not drawing. Additionally, musicians and non-musicians may be employing different movement strategies to maintain accurate timing in the two tasks. These findings add to our understanding of how musical training affects timing and support the dissociability of event-based and emergent timing modes."],"ontologies":["36810|1 ","49002|1 ","3132|1 ","3797|1 ","37953|1 ","36563|2 ","524|1 ","3781|1 ","2848|1 ","17163|1 ","17165|1 ","49010|1 ","36647|3 ","36529|1 ","2936|1 ","2643|1 ","714|1 ","3591|1 ","2272|1 ","3103|1 ","2265|1 ","37051|1 ","3691|1 "],"article_date":"2013-06-14T00:00:00Z","journal_title":"Frontiers in human neuroscience","date_created":"2013-06-29T00:00:00Z","journal_country":"Switzerland","journal_iso_abbreviation":"Front Hum Neurosci","id":"23717275","author":["L H LH Baer","J L N JL Thibodeau","T M TM Gralnick","K Z H KZ Li","V B VB Penhune"],"article_pagination":"191","journal_publication_date":"2013-09-13T00:00:00Z","affiliation":"Department of Psychology, Centre for Research in Human Development, Concordia University Montréal, QC, Canada.","language":"eng","_version_":1450807667479019520}]},"facet_counts":{"facet_queries":{},"facet_fields":{"journal_title":["in",4,"frontiers",2,"angewandte",1,"chemie",1,"ed",1,"english",1,"fetal",1,"human",1,"international",1,"medicine",1,"microbiology",1,"neonatal",1,"neuroscience",1,"seminars",1],"author_facet":["Annalisa A Guaragna",1,"Arthur A Van Aerschot",1,"B B Hallberg",1,"Daniele D D'Alonzo",1,"Guy G Schepers",1,"Haruyoshi H Tomita",1,"Hidetada H Hirakawa",1,"J L N JL Thibodeau",1,"Jussara J Amato",1,"K Z H KZ Li",1,"L H LH Baer",1,"M M Blennow",1,"Matheus M Froeyen",1,"Piet P Herdewijn",1,"T M TM Gralnick",1,"V B VB Penhune",1]},"facet_dates":{"article_date":{"gap":"+1DAYS","start":"2013-04-27T00:00:00Z","end":"2013-06-28T00:00:00Z"}},"facet_ranges":{}},"highlighting":{"23680099":{},"23670912":{},"23720655":{},"23717275":{}},"spellcheck":{"suggestions":["correctlySpelled",false]}}""")

    json_response = self.c.post(reverse('search:download'), {
        'type': 'json',
        'collection': json.dumps(self._get_collection_param(self.collection)),
        'query': json.dumps(QUERY)
    })

    json_response_content = json.loads(json_response.content)
    assert_equal('application/json', json_response['Content-Type'])
    assert_equal('attachment; filename="query_result.json"', json_response['Content-Disposition'])
    assert_equal(4, len(json_response_content), len(json_response_content))
    assert_equal('Investigations for neonatal seizures.', json_response_content[0]['article_title'])

    csv_response = self.c.post(reverse('search:download'), {
        'type': 'csv',
        'collection': json.dumps(self._get_collection_param(self.collection)),
        'query': json.dumps(QUERY)
    })
    csv_response_content = ''.join(csv_response.streaming_content)
    assert_equal('application/csv', csv_response['Content-Type'])
    assert_equal('attachment; filename="query_result.csv"', csv_response['Content-Disposition'])
    assert_equal(4 + 1 + 1, len(csv_response_content.split('\n')), csv_response_content.split('\n'))
    assert_true('&lt;script&gt;alert(1234)&lt;/script&gt;,_version_,author,category,comments,content,content_type,description,features,inStock,includes,keywords,last_modified,links,manu,manu_exact,name,payloads,popularity,price,resourcename,sku,store,subject,text,text_rev,title,url,weight,id' in csv_response_content, csv_response_content)
    # Fields does not exactly match the response but this is because the collection schema does not match the query response.
    assert_true(""",1450807641462800385,"['B B Hallberg', 'M M Blennow']",,,,,,,,,,,,,,,,,,,,,,,,,,,23680099""" in csv_response_content, csv_response_content)

    xls_response = self.c.post(reverse('search:download'), {
        'type': 'xls',
        'collection': json.dumps(self._get_collection_param(self.collection)),
        'query': json.dumps(QUERY)
    })
    xls_response_content = ''.join(xls_response.content)
    assert_not_equal(0, len(xls_response_content))
    assert_equal('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', xls_response['Content-Type'])
    assert_equal('attachment; filename="query_result.xlsx"', xls_response['Content-Disposition'])


SOLR_LUKE_SCHEMA = """{"responseHeader":{"status":0,"QTime":2},"index":{"numDocs":8,"maxDoc":8,"deletedDocs":0,"version":15,"segmentCount":5,"current":true,"hasDeletions":false,"directory":"org.apache.lucene.store.NRTCachingDirectory:NRTCachingDirectory(org.apache.solr.store.hdfs.HdfsDirectory@5efe087b lockFactory=org.apache.solr.store.hdfs.HdfsLockFactory@5106def2; maxCacheMB=192.0 maxMergeSizeMB=16.0)","userData":{"commitTimeMSec":"1389233070579"},"lastModified":"2014-01-09T02:04:30.579Z"},"schema":{"fields":{"_version_":{"type":"long","flags":"ITS-----OF------","copyDests":[],"copySources":[]},"author":{"type":"text_general","flags":"ITS-------------","positionIncrementGap":100,"copyDests":["author_s","text"],"copySources":[]},"<script>alert(1234)</script>":{"type":"string","flags":"I-S-M---OF-----l","copyDests":["text"],"copySources":[]},"category":{"type":"text_general","flags":"ITS-------------","positionIncrementGap":100,"copyDests":[],"copySources":[]},"comments":{"type":"text_general","flags":"ITS-------------","positionIncrementGap":100,"copyDests":[],"copySources":[]},"content":{"type":"text_general","flags":"-TS-M-----------","positionIncrementGap":100,"copyDests":["text"],"copySources":[]},"content_type":{"type":"string","flags":"I-S-M---OF-----l","copyDests":["text"],"copySources":[]},"description":{"type":"text_general","flags":"ITS-------------","positionIncrementGap":100,"copyDests":["text"],"copySources":[]},"features":{"type":"text_general","flags":"ITS-M-----------","positionIncrementGap":100,"copyDests":["text"],"copySources":[]},"id":{"type":"string","flags":"I-S-----OF-----l","required":true,"uniqueKey":true,"copyDests":[],"copySources":[]},"inStock":{"type":"boolean","flags":"I-S-----OF-----l","copyDests":[],"copySources":[]},"includes":{"type":"text_general","flags":"ITS--Vop--------","positionIncrementGap":100,"copyDests":["text"],"copySources":[]},"keywords":{"type":"text_general","flags":"ITS-------------","positionIncrementGap":100,"copyDests":["text"],"copySources":[]},"last_modified":{"type":"date","flags":"ITS------F------","copyDests":[],"copySources":[]},"links":{"type":"string","flags":"I-S-M---OF-----l","copyDests":[],"copySources":[]},"manu":{"type":"text_general","flags":"ITS-----O-------","positionIncrementGap":100,"copyDests":["text","manu_exact"],"copySources":[]},"manu_exact":{"type":"string","flags":"I-------OF-----l","copyDests":[],"copySources":["manu"]},"name":{"type":"text_general","flags":"ITS-------------","positionIncrementGap":100,"copyDests":["text"],"copySources":[]},"payloads":{"type":"payloads","flags":"ITS-------------","copyDests":[],"copySources":[]},"popularity":{"type":"int","flags":"ITS-----OF------","copyDests":[],"copySources":[]},"price":{"type":"float","flags":"ITS-----OF------","copyDests":["price_c"],"copySources":[]},"resourcename":{"type":"text_general","flags":"ITS-------------","positionIncrementGap":100,"copyDests":["text"],"copySources":[]},"sku":{"type":"text_en_splitting_tight","flags":"ITS-----O-------","positionIncrementGap":100,"copyDests":[],"copySources":[]},"store":{"type":"location","flags":"I-S------F------","copyDests":[],"copySources":[]},"subject":{"type":"text_general","flags":"ITS-------------","positionIncrementGap":100,"copyDests":[],"copySources":[]},"text":{"type":"text_general","flags":"IT--M-----------","positionIncrementGap":100,"copyDests":[],"copySources":["cat","keywords","resourcename","includes","url","content","author","title","manu","description","name","features","content_type"]},"text_rev":{"type":"text_general_rev","flags":"IT--M-----------","positionIncrementGap":100,"copyDests":[],"copySources":[]},"title":{"type":"text_general","flags":"ITS-M-----------","positionIncrementGap":100,"copyDests":["text"],"copySources":[]},"url":{"type":"text_general","flags":"ITS-------------","positionIncrementGap":100,"copyDests":["text"],"copySources":[]},"weight":{"type":"float","flags":"ITS-----OF------","copyDests":[],"copySources":[]}},"dynamicFields":{"*____amount_raw":{"type":"amount_raw_type_tlong","flags":"IT------O-------","copyDests":[],"copySources":[]},"*____currency":{"type":"currency_type_string","flags":"I-------O-------","copyDests":[],"copySources":[]},"*_b":{"type":"boolean","flags":"I-S-----OF-----l","copyDests":[],"copySources":[]},"*_bs":{"type":"boolean","flags":"I-S-M---OF-----l","copyDests":[],"copySources":[]},"*_c":{"type":"currency","flags":"I-S------F------","copyDests":[],"copySources":[]},"*_coordinate":{"type":"tdouble","flags":"IT------OF------","copyDests":[],"copySources":[]},"*_d":{"type":"double","flags":"ITS-----OF------","copyDests":[],"copySources":[]},"*_ds":{"type":"double","flags":"ITS-M---OF------","copyDests":[],"copySources":[]},"*_dt":{"type":"date","flags":"ITS------F------","copyDests":[],"copySources":[]},"*_dts":{"type":"date","flags":"ITS-M----F------","copyDests":[],"copySources":[]},"*_en":{"type":"text_en","flags":"ITS-M-----------","positionIncrementGap":100,"copyDests":[],"copySources":[]},"*_f":{"type":"float","flags":"ITS-----OF------","copyDests":[],"copySources":[]},"*_fs":{"type":"float","flags":"ITS-M---OF------","copyDests":[],"copySources":[]},"*_i":{"type":"int","flags":"ITS-----OF------","copyDests":[],"copySources":[]},"*_is":{"type":"int","flags":"ITS-M---OF------","copyDests":[],"copySources":[]},"*_l":{"type":"long","flags":"ITS-----OF------","copyDests":[],"copySources":[]},"*_ls":{"type":"long","flags":"ITS-M---OF------","copyDests":[],"copySources":[]},"*_p":{"type":"location","flags":"I-S------F------","copyDests":[],"copySources":[]},"*_pi":{"type":"pint","flags":"I-S-----OF------","copyDests":[],"copySources":[]},"*_s":{"type":"string","flags":"I-S-----OF-----l","copyDests":[],"copySources":[]},"*_ss":{"type":"string","flags":"I-S-M---OF-----l","copyDests":[],"copySources":[]},"*_t":{"type":"text_general","flags":"ITS-------------","positionIncrementGap":100,"copyDests":[],"copySources":[]},"*_td":{"type":"tdouble","flags":"ITS-----OF------","copyDests":[],"copySources":[]},"*_tdt":{"type":"tdate","flags":"ITS------F------","copyDests":[],"copySources":[]},"*_tf":{"type":"tfloat","flags":"ITS-----OF------","copyDests":[],"copySources":[]},"*_ti":{"type":"tint","flags":"ITS-----OF------","copyDests":[],"copySources":[]},"*_tl":{"type":"tlong","flags":"ITS-----OF------","copyDests":[],"copySources":[]},"*_txt":{"type":"text_general","flags":"ITS-M-----------","positionIncrementGap":100,"copyDests":[],"copySources":[]},"attr_*":{"type":"text_general","flags":"ITS-M-----------","positionIncrementGap":100,"copyDests":[],"copySources":[]},"ignored_*":{"type":"ignored","flags":"----M---OF------","copyDests":[],"copySources":[]},"random_*":{"type":"random","flags":"I-S------F------","copyDests":[],"copySources":[]}},"uniqueKeyField":"id","defaultSearchField":null,"types":{"alphaOnlySort":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.core.KeywordTokenizerFactory","args":{"class":"solr.KeywordTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"TrimFilterFactory":{"args":{"class":"solr.TrimFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.miscellaneous.TrimFilterFactory"},"PatternReplaceFilterFactory":{"args":{"replace":"all","replacement":"","pattern":"([^a-z])","class":"solr.PatternReplaceFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.pattern.PatternReplaceFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.core.KeywordTokenizerFactory","args":{"class":"solr.KeywordTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"TrimFilterFactory":{"args":{"class":"solr.TrimFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.miscellaneous.TrimFilterFactory"},"PatternReplaceFilterFactory":{"args":{"replace":"all","replacement":"","pattern":"([^a-z])","class":"solr.PatternReplaceFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.pattern.PatternReplaceFilterFactory"}}},"similarity":{}},"ancestor_path":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.core.KeywordTokenizerFactory","args":{"class":"solr.KeywordTokenizerFactory","luceneMatchVersion":"LUCENE_44"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.path.PathHierarchyTokenizerFactory","args":{"delimiter":"/","class":"solr.PathHierarchyTokenizerFactory","luceneMatchVersion":"LUCENE_44"}}},"similarity":{}},"binary":{"fields":null,"tokenized":false,"className":"org.apache.solr.schema.BinaryField","indexAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"queryAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"similarity":{}},"boolean":{"fields":["inStock","*_bs","*_b"],"tokenized":false,"className":"org.apache.solr.schema.BoolField","indexAnalyzer":{"className":"org.apache.solr.schema.BoolField$1"},"queryAnalyzer":{"className":"org.apache.solr.schema.BoolField$1"},"similarity":{}},"currency":{"fields":["*_c"],"tokenized":false,"className":"org.apache.solr.schema.CurrencyField","indexAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"queryAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"similarity":{}},"date":{"fields":["last_modified","*_dts","*_dt"],"tokenized":true,"className":"org.apache.solr.schema.TrieDateField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.solr.analysis.TrieTokenizerFactory","args":{}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.solr.analysis.TrieTokenizerFactory","args":{}}},"similarity":{}},"descendent_path":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.path.PathHierarchyTokenizerFactory","args":{"delimiter":"/","class":"solr.PathHierarchyTokenizerFactory","luceneMatchVersion":"LUCENE_44"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.core.KeywordTokenizerFactory","args":{"class":"solr.KeywordTokenizerFactory","luceneMatchVersion":"LUCENE_44"}}},"similarity":{}},"double":{"fields":["*_ds","*_d"],"tokenized":true,"className":"org.apache.solr.schema.TrieDoubleField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.solr.analysis.TrieTokenizerFactory","args":{}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.solr.analysis.TrieTokenizerFactory","args":{}}},"similarity":{}},"float":{"fields":["weight","price","*_fs","*_f"],"tokenized":true,"className":"org.apache.solr.schema.TrieFloatField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.solr.analysis.TrieTokenizerFactory","args":{}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.solr.analysis.TrieTokenizerFactory","args":{}}},"similarity":{}},"ignored":{"fields":["ignored_*"],"tokenized":false,"className":"org.apache.solr.schema.StrField","indexAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"queryAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"similarity":{}},"int":{"fields":["popularity","*_is","*_i"],"tokenized":true,"className":"org.apache.solr.schema.TrieIntField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.solr.analysis.TrieTokenizerFactory","args":{}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.solr.analysis.TrieTokenizerFactory","args":{}}},"similarity":{}},"location":{"fields":["store","*_p"],"tokenized":false,"className":"org.apache.solr.schema.LatLonType","indexAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"queryAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"similarity":{}},"location_rpt":{"fields":null,"tokenized":false,"className":"org.apache.solr.schema.SpatialRecursivePrefixTreeFieldType","indexAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"queryAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"similarity":{}},"long":{"fields":["_version_","*_ls","*_l"],"tokenized":true,"className":"org.apache.solr.schema.TrieLongField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.solr.analysis.TrieTokenizerFactory","args":{}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.solr.analysis.TrieTokenizerFactory","args":{}}},"similarity":{}},"lowercase":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.core.KeywordTokenizerFactory","args":{"class":"solr.KeywordTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.core.KeywordTokenizerFactory","args":{"class":"solr.KeywordTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"}}},"similarity":{}},"payloads":{"fields":["payloads"],"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.core.WhitespaceTokenizerFactory","args":{"class":"solr.WhitespaceTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"DelimitedPayloadTokenFilterFactory":{"args":{"class":"solr.DelimitedPayloadTokenFilterFactory","luceneMatchVersion":"LUCENE_44","encoder":"float"},"className":"org.apache.lucene.analysis.payloads.DelimitedPayloadTokenFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.core.WhitespaceTokenizerFactory","args":{"class":"solr.WhitespaceTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"DelimitedPayloadTokenFilterFactory":{"args":{"class":"solr.DelimitedPayloadTokenFilterFactory","luceneMatchVersion":"LUCENE_44","encoder":"float"},"className":"org.apache.lucene.analysis.payloads.DelimitedPayloadTokenFilterFactory"}}},"similarity":{}},"pdate":{"fields":null,"tokenized":false,"className":"org.apache.solr.schema.DateField","indexAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"queryAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"similarity":{}},"pdouble":{"fields":null,"tokenized":false,"className":"org.apache.solr.schema.DoubleField","indexAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"queryAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"similarity":{}},"pfloat":{"fields":null,"tokenized":false,"className":"org.apache.solr.schema.FloatField","indexAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"queryAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"similarity":{}},"phonetic":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"DoubleMetaphoneFilterFactory":{"args":{"inject":"false","class":"solr.DoubleMetaphoneFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.phonetic.DoubleMetaphoneFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"DoubleMetaphoneFilterFactory":{"args":{"inject":"false","class":"solr.DoubleMetaphoneFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.phonetic.DoubleMetaphoneFilterFactory"}}},"similarity":{}},"pint":{"fields":["*_pi"],"tokenized":false,"className":"org.apache.solr.schema.IntField","indexAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"queryAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"similarity":{}},"plong":{"fields":null,"tokenized":false,"className":"org.apache.solr.schema.LongField","indexAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"queryAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"similarity":{}},"point":{"fields":null,"tokenized":false,"className":"org.apache.solr.schema.PointType","indexAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"queryAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"similarity":{}},"random":{"fields":["random_*"],"tokenized":false,"className":"org.apache.solr.schema.RandomSortField","indexAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"queryAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"similarity":{}},"string":{"fields":["cat","id","manu_exact","content_type","links","*_ss","*_s"],"tokenized":false,"className":"org.apache.solr.schema.StrField","indexAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"queryAnalyzer":{"className":"org.apache.solr.schema.FieldType$DefaultAnalyzer"},"similarity":{}},"tdate":{"fields":["*_tdt"],"tokenized":true,"className":"org.apache.solr.schema.TrieDateField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.solr.analysis.TrieTokenizerFactory","args":{}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.solr.analysis.TrieTokenizerFactory","args":{}}},"similarity":{}},"tdouble":{"fields":["*_coordinate","*_td"],"tokenized":true,"className":"org.apache.solr.schema.TrieDoubleField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.solr.analysis.TrieTokenizerFactory","args":{}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.solr.analysis.TrieTokenizerFactory","args":{}}},"similarity":{}},"text_ar":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_ar.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"ArabicNormalizationFilterFactory":{"args":{"class":"solr.ArabicNormalizationFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.ar.ArabicNormalizationFilterFactory"},"ArabicStemFilterFactory":{"args":{"class":"solr.ArabicStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.ar.ArabicStemFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_ar.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"ArabicNormalizationFilterFactory":{"args":{"class":"solr.ArabicNormalizationFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.ar.ArabicNormalizationFilterFactory"},"ArabicStemFilterFactory":{"args":{"class":"solr.ArabicStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.ar.ArabicStemFilterFactory"}}},"similarity":{}},"text_bg":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_bg.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"BulgarianStemFilterFactory":{"args":{"class":"solr.BulgarianStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.bg.BulgarianStemFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_bg.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"BulgarianStemFilterFactory":{"args":{"class":"solr.BulgarianStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.bg.BulgarianStemFilterFactory"}}},"similarity":{}},"text_ca":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"ElisionFilterFactory":{"args":{"articles":"lang/contractions_ca.txt","class":"solr.ElisionFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.util.ElisionFilterFactory"},"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_ca.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Catalan","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"ElisionFilterFactory":{"args":{"articles":"lang/contractions_ca.txt","class":"solr.ElisionFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.util.ElisionFilterFactory"},"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_ca.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Catalan","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"similarity":{}},"text_cjk":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"CJKWidthFilterFactory":{"args":{"class":"solr.CJKWidthFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.cjk.CJKWidthFilterFactory"},"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"CJKBigramFilterFactory":{"args":{"class":"solr.CJKBigramFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.cjk.CJKBigramFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"CJKWidthFilterFactory":{"args":{"class":"solr.CJKWidthFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.cjk.CJKWidthFilterFactory"},"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"CJKBigramFilterFactory":{"args":{"class":"solr.CJKBigramFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.cjk.CJKBigramFilterFactory"}}},"similarity":{}},"text_cz":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_cz.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"CzechStemFilterFactory":{"args":{"class":"solr.CzechStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.cz.CzechStemFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_cz.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"CzechStemFilterFactory":{"args":{"class":"solr.CzechStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.cz.CzechStemFilterFactory"}}},"similarity":{}},"text_da":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_da.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Danish","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_da.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Danish","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"similarity":{}},"text_de":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_de.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"GermanNormalizationFilterFactory":{"args":{"class":"solr.GermanNormalizationFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.de.GermanNormalizationFilterFactory"},"GermanLightStemFilterFactory":{"args":{"class":"solr.GermanLightStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.de.GermanLightStemFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_de.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"GermanNormalizationFilterFactory":{"args":{"class":"solr.GermanNormalizationFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.de.GermanNormalizationFilterFactory"},"GermanLightStemFilterFactory":{"args":{"class":"solr.GermanLightStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.de.GermanLightStemFilterFactory"}}},"similarity":{}},"text_el":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"GreekLowerCaseFilterFactory":{"args":{"class":"solr.GreekLowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.el.GreekLowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_el.txt","class":"solr.StopFilterFactory","ignoreCase":"false","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"GreekStemFilterFactory":{"args":{"class":"solr.GreekStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.el.GreekStemFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"GreekLowerCaseFilterFactory":{"args":{"class":"solr.GreekLowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.el.GreekLowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_el.txt","class":"solr.StopFilterFactory","ignoreCase":"false","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"GreekStemFilterFactory":{"args":{"class":"solr.GreekStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.el.GreekStemFilterFactory"}}},"similarity":{}},"text_en":{"fields":["*_en"],"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"StopFilterFactory":{"args":{"words":"lang/stopwords_en.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"EnglishPossessiveFilterFactory":{"args":{"class":"solr.EnglishPossessiveFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.en.EnglishPossessiveFilterFactory"},"KeywordMarkerFilterFactory":{"args":{"protected":"protwords.txt","class":"solr.KeywordMarkerFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.miscellaneous.KeywordMarkerFilterFactory"},"PorterStemFilterFactory":{"args":{"class":"solr.PorterStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.en.PorterStemFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"SynonymFilterFactory":{"args":{"class":"solr.SynonymFilterFactory","expand":"true","synonyms":"synonyms.txt","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.synonym.SynonymFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_en.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"EnglishPossessiveFilterFactory":{"args":{"class":"solr.EnglishPossessiveFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.en.EnglishPossessiveFilterFactory"},"KeywordMarkerFilterFactory":{"args":{"protected":"protwords.txt","class":"solr.KeywordMarkerFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.miscellaneous.KeywordMarkerFilterFactory"},"PorterStemFilterFactory":{"args":{"class":"solr.PorterStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.en.PorterStemFilterFactory"}}},"similarity":{}},"text_en_splitting":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.core.WhitespaceTokenizerFactory","args":{"class":"solr.WhitespaceTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"StopFilterFactory":{"args":{"words":"lang/stopwords_en.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"WordDelimiterFilterFactory":{"args":{"generateNumberParts":"1","splitOnCaseChange":"1","catenateWords":"1","class":"solr.WordDelimiterFilterFactory","generateWordParts":"1","luceneMatchVersion":"LUCENE_44","catenateAll":"0","catenateNumbers":"1"},"className":"org.apache.lucene.analysis.miscellaneous.WordDelimiterFilterFactory"},"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"KeywordMarkerFilterFactory":{"args":{"protected":"protwords.txt","class":"solr.KeywordMarkerFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.miscellaneous.KeywordMarkerFilterFactory"},"PorterStemFilterFactory":{"args":{"class":"solr.PorterStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.en.PorterStemFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.core.WhitespaceTokenizerFactory","args":{"class":"solr.WhitespaceTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"SynonymFilterFactory":{"args":{"class":"solr.SynonymFilterFactory","expand":"true","synonyms":"synonyms.txt","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.synonym.SynonymFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_en.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"WordDelimiterFilterFactory":{"args":{"generateNumberParts":"1","splitOnCaseChange":"1","catenateWords":"0","class":"solr.WordDelimiterFilterFactory","generateWordParts":"1","luceneMatchVersion":"LUCENE_44","catenateAll":"0","catenateNumbers":"0"},"className":"org.apache.lucene.analysis.miscellaneous.WordDelimiterFilterFactory"},"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"KeywordMarkerFilterFactory":{"args":{"protected":"protwords.txt","class":"solr.KeywordMarkerFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.miscellaneous.KeywordMarkerFilterFactory"},"PorterStemFilterFactory":{"args":{"class":"solr.PorterStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.en.PorterStemFilterFactory"}}},"similarity":{}},"text_en_splitting_tight":{"fields":["sku"],"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.core.WhitespaceTokenizerFactory","args":{"class":"solr.WhitespaceTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"SynonymFilterFactory":{"args":{"class":"solr.SynonymFilterFactory","expand":"false","synonyms":"synonyms.txt","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.synonym.SynonymFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_en.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"WordDelimiterFilterFactory":{"args":{"generateNumberParts":"0","catenateWords":"1","class":"solr.WordDelimiterFilterFactory","generateWordParts":"0","luceneMatchVersion":"LUCENE_44","catenateAll":"0","catenateNumbers":"1"},"className":"org.apache.lucene.analysis.miscellaneous.WordDelimiterFilterFactory"},"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"KeywordMarkerFilterFactory":{"args":{"protected":"protwords.txt","class":"solr.KeywordMarkerFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.miscellaneous.KeywordMarkerFilterFactory"},"EnglishMinimalStemFilterFactory":{"args":{"class":"solr.EnglishMinimalStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.en.EnglishMinimalStemFilterFactory"},"RemoveDuplicatesTokenFilterFactory":{"args":{"class":"solr.RemoveDuplicatesTokenFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.miscellaneous.RemoveDuplicatesTokenFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.core.WhitespaceTokenizerFactory","args":{"class":"solr.WhitespaceTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"SynonymFilterFactory":{"args":{"class":"solr.SynonymFilterFactory","expand":"false","synonyms":"synonyms.txt","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.synonym.SynonymFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_en.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"WordDelimiterFilterFactory":{"args":{"generateNumberParts":"0","catenateWords":"1","class":"solr.WordDelimiterFilterFactory","generateWordParts":"0","luceneMatchVersion":"LUCENE_44","catenateAll":"0","catenateNumbers":"1"},"className":"org.apache.lucene.analysis.miscellaneous.WordDelimiterFilterFactory"},"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"KeywordMarkerFilterFactory":{"args":{"protected":"protwords.txt","class":"solr.KeywordMarkerFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.miscellaneous.KeywordMarkerFilterFactory"},"EnglishMinimalStemFilterFactory":{"args":{"class":"solr.EnglishMinimalStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.en.EnglishMinimalStemFilterFactory"},"RemoveDuplicatesTokenFilterFactory":{"args":{"class":"solr.RemoveDuplicatesTokenFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.miscellaneous.RemoveDuplicatesTokenFilterFactory"}}},"similarity":{}},"text_es":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_es.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SpanishLightStemFilterFactory":{"args":{"class":"solr.SpanishLightStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.es.SpanishLightStemFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_es.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SpanishLightStemFilterFactory":{"args":{"class":"solr.SpanishLightStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.es.SpanishLightStemFilterFactory"}}},"similarity":{}},"text_eu":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_eu.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Basque","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_eu.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Basque","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"similarity":{}},"text_fa":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","charFilters":{"PersianCharFilterFactory":{"args":{"class":"solr.PersianCharFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.fa.PersianCharFilterFactory"}},"tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"ArabicNormalizationFilterFactory":{"args":{"class":"solr.ArabicNormalizationFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.ar.ArabicNormalizationFilterFactory"},"PersianNormalizationFilterFactory":{"args":{"class":"solr.PersianNormalizationFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.fa.PersianNormalizationFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_fa.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","charFilters":{"PersianCharFilterFactory":{"args":{"class":"solr.PersianCharFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.fa.PersianCharFilterFactory"}},"tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"ArabicNormalizationFilterFactory":{"args":{"class":"solr.ArabicNormalizationFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.ar.ArabicNormalizationFilterFactory"},"PersianNormalizationFilterFactory":{"args":{"class":"solr.PersianNormalizationFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.fa.PersianNormalizationFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_fa.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"}}},"similarity":{}},"text_fi":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_fi.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Finnish","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_fi.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Finnish","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"similarity":{}},"text_fr":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"ElisionFilterFactory":{"args":{"articles":"lang/contractions_fr.txt","class":"solr.ElisionFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.util.ElisionFilterFactory"},"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_fr.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"FrenchLightStemFilterFactory":{"args":{"class":"solr.FrenchLightStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.fr.FrenchLightStemFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"ElisionFilterFactory":{"args":{"articles":"lang/contractions_fr.txt","class":"solr.ElisionFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.util.ElisionFilterFactory"},"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_fr.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"FrenchLightStemFilterFactory":{"args":{"class":"solr.FrenchLightStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.fr.FrenchLightStemFilterFactory"}}},"similarity":{}},"text_ga":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"ElisionFilterFactory":{"args":{"articles":"lang/contractions_ga.txt","class":"solr.ElisionFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.util.ElisionFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/hyphenations_ga.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"IrishLowerCaseFilterFactory":{"args":{"class":"solr.IrishLowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.ga.IrishLowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_ga.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Irish","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"ElisionFilterFactory":{"args":{"articles":"lang/contractions_ga.txt","class":"solr.ElisionFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.util.ElisionFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/hyphenations_ga.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"IrishLowerCaseFilterFactory":{"args":{"class":"solr.IrishLowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.ga.IrishLowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_ga.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Irish","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"similarity":{}},"text_general":{"fields":["subject","includes","author","title","description","name","features","text","keywords","resourcename","url","content","category","manu","comments","attr_*","*_txt","*_t"],"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"StopFilterFactory":{"args":{"words":"stopwords.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"StopFilterFactory":{"args":{"words":"stopwords.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SynonymFilterFactory":{"args":{"class":"solr.SynonymFilterFactory","expand":"true","synonyms":"synonyms.txt","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.synonym.SynonymFilterFactory"},"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"}}},"similarity":{}},"text_general_rev":{"fields":["text_rev"],"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"StopFilterFactory":{"args":{"words":"stopwords.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"ReversedWildcardFilterFactory":{"args":{"maxFractionAsterisk":"0.33","withOriginal":"true","maxPosQuestion":"2","class":"solr.ReversedWildcardFilterFactory","maxPosAsterisk":"3","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.solr.analysis.ReversedWildcardFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"SynonymFilterFactory":{"args":{"class":"solr.SynonymFilterFactory","expand":"true","synonyms":"synonyms.txt","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.synonym.SynonymFilterFactory"},"StopFilterFactory":{"args":{"words":"stopwords.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"}}},"similarity":{}},"text_gl":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_gl.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"GalicianStemFilterFactory":{"args":{"class":"solr.GalicianStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.gl.GalicianStemFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_gl.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"GalicianStemFilterFactory":{"args":{"class":"solr.GalicianStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.gl.GalicianStemFilterFactory"}}},"similarity":{}},"text_hi":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"IndicNormalizationFilterFactory":{"args":{"class":"solr.IndicNormalizationFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.in.IndicNormalizationFilterFactory"},"HindiNormalizationFilterFactory":{"args":{"class":"solr.HindiNormalizationFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.hi.HindiNormalizationFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_hi.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"HindiStemFilterFactory":{"args":{"class":"solr.HindiStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.hi.HindiStemFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"IndicNormalizationFilterFactory":{"args":{"class":"solr.IndicNormalizationFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.in.IndicNormalizationFilterFactory"},"HindiNormalizationFilterFactory":{"args":{"class":"solr.HindiNormalizationFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.hi.HindiNormalizationFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_hi.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"HindiStemFilterFactory":{"args":{"class":"solr.HindiStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.hi.HindiStemFilterFactory"}}},"similarity":{}},"text_hu":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_hu.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Hungarian","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_hu.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Hungarian","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"similarity":{}},"text_hy":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_hy.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Armenian","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_hy.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Armenian","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"similarity":{}},"text_id":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_id.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"IndonesianStemFilterFactory":{"args":{"class":"solr.IndonesianStemFilterFactory","stemDerivational":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.id.IndonesianStemFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_id.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"IndonesianStemFilterFactory":{"args":{"class":"solr.IndonesianStemFilterFactory","stemDerivational":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.id.IndonesianStemFilterFactory"}}},"similarity":{}},"text_it":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"ElisionFilterFactory":{"args":{"articles":"lang/contractions_it.txt","class":"solr.ElisionFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.util.ElisionFilterFactory"},"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_it.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"ItalianLightStemFilterFactory":{"args":{"class":"solr.ItalianLightStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.it.ItalianLightStemFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"ElisionFilterFactory":{"args":{"articles":"lang/contractions_it.txt","class":"solr.ElisionFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.util.ElisionFilterFactory"},"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_it.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"ItalianLightStemFilterFactory":{"args":{"class":"solr.ItalianLightStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.it.ItalianLightStemFilterFactory"}}},"similarity":{}},"text_ja":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.ja.JapaneseTokenizerFactory","args":{"class":"solr.JapaneseTokenizerFactory","luceneMatchVersion":"LUCENE_44","mode":"search"}},"filters":{"JapaneseBaseFormFilterFactory":{"args":{"class":"solr.JapaneseBaseFormFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.ja.JapaneseBaseFormFilterFactory"},"JapanesePartOfSpeechStopFilterFactory":{"args":{"tags":"lang/stoptags_ja.txt","class":"solr.JapanesePartOfSpeechStopFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.ja.JapanesePartOfSpeechStopFilterFactory"},"CJKWidthFilterFactory":{"args":{"class":"solr.CJKWidthFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.cjk.CJKWidthFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_ja.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"JapaneseKatakanaStemFilterFactory":{"args":{"class":"solr.JapaneseKatakanaStemFilterFactory","minimumLength":"4","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.ja.JapaneseKatakanaStemFilterFactory"},"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.ja.JapaneseTokenizerFactory","args":{"class":"solr.JapaneseTokenizerFactory","luceneMatchVersion":"LUCENE_44","mode":"search"}},"filters":{"JapaneseBaseFormFilterFactory":{"args":{"class":"solr.JapaneseBaseFormFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.ja.JapaneseBaseFormFilterFactory"},"JapanesePartOfSpeechStopFilterFactory":{"args":{"tags":"lang/stoptags_ja.txt","class":"solr.JapanesePartOfSpeechStopFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.ja.JapanesePartOfSpeechStopFilterFactory"},"CJKWidthFilterFactory":{"args":{"class":"solr.CJKWidthFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.cjk.CJKWidthFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_ja.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"JapaneseKatakanaStemFilterFactory":{"args":{"class":"solr.JapaneseKatakanaStemFilterFactory","minimumLength":"4","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.ja.JapaneseKatakanaStemFilterFactory"},"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"}}},"similarity":{}},"text_lv":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_lv.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"LatvianStemFilterFactory":{"args":{"class":"solr.LatvianStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.lv.LatvianStemFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_lv.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"LatvianStemFilterFactory":{"args":{"class":"solr.LatvianStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.lv.LatvianStemFilterFactory"}}},"similarity":{}},"text_nl":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_nl.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"StemmerOverrideFilterFactory":{"args":{"class":"solr.StemmerOverrideFilterFactory","dictionary":"lang/stemdict_nl.txt","ignoreCase":"false","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.miscellaneous.StemmerOverrideFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Dutch","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_nl.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"StemmerOverrideFilterFactory":{"args":{"class":"solr.StemmerOverrideFilterFactory","dictionary":"lang/stemdict_nl.txt","ignoreCase":"false","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.miscellaneous.StemmerOverrideFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Dutch","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"similarity":{}},"text_no":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_no.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Norwegian","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_no.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Norwegian","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"similarity":{}},"text_pt":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_pt.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"PortugueseLightStemFilterFactory":{"args":{"class":"solr.PortugueseLightStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.pt.PortugueseLightStemFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_pt.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"PortugueseLightStemFilterFactory":{"args":{"class":"solr.PortugueseLightStemFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.pt.PortugueseLightStemFilterFactory"}}},"similarity":{}},"text_ro":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_ro.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Romanian","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_ro.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Romanian","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"similarity":{}},"text_ru":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_ru.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Russian","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_ru.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Russian","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"similarity":{}},"text_sv":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_sv.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Swedish","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_sv.txt","class":"solr.StopFilterFactory","format":"snowball","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Swedish","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"similarity":{}},"text_th":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"ThaiWordFilterFactory":{"args":{"class":"solr.ThaiWordFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.th.ThaiWordFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_th.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"LowerCaseFilterFactory":{"args":{"class":"solr.LowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.LowerCaseFilterFactory"},"ThaiWordFilterFactory":{"args":{"class":"solr.ThaiWordFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.th.ThaiWordFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_th.txt","class":"solr.StopFilterFactory","ignoreCase":"true","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"}}},"similarity":{}},"text_tr":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"TurkishLowerCaseFilterFactory":{"args":{"class":"solr.TurkishLowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.tr.TurkishLowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_tr.txt","class":"solr.StopFilterFactory","ignoreCase":"false","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Turkish","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.standard.StandardTokenizerFactory","args":{"class":"solr.StandardTokenizerFactory","luceneMatchVersion":"LUCENE_44"}},"filters":{"TurkishLowerCaseFilterFactory":{"args":{"class":"solr.TurkishLowerCaseFilterFactory","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.tr.TurkishLowerCaseFilterFactory"},"StopFilterFactory":{"args":{"words":"lang/stopwords_tr.txt","class":"solr.StopFilterFactory","ignoreCase":"false","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.core.StopFilterFactory"},"SnowballPorterFilterFactory":{"args":{"class":"solr.SnowballPorterFilterFactory","language":"Turkish","luceneMatchVersion":"LUCENE_44"},"className":"org.apache.lucene.analysis.snowball.SnowballPorterFilterFactory"}}},"similarity":{}},"text_ws":{"fields":null,"tokenized":true,"className":"org.apache.solr.schema.TextField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.core.WhitespaceTokenizerFactory","args":{"class":"solr.WhitespaceTokenizerFactory","luceneMatchVersion":"LUCENE_44"}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.lucene.analysis.core.WhitespaceTokenizerFactory","args":{"class":"solr.WhitespaceTokenizerFactory","luceneMatchVersion":"LUCENE_44"}}},"similarity":{}},"tfloat":{"fields":["*_tf"],"tokenized":true,"className":"org.apache.solr.schema.TrieFloatField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.solr.analysis.TrieTokenizerFactory","args":{}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.solr.analysis.TrieTokenizerFactory","args":{}}},"similarity":{}},"tint":{"fields":["*_ti"],"tokenized":true,"className":"org.apache.solr.schema.TrieIntField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.solr.analysis.TrieTokenizerFactory","args":{}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.solr.analysis.TrieTokenizerFactory","args":{}}},"similarity":{}},"tlong":{"fields":["*_tl"],"tokenized":true,"className":"org.apache.solr.schema.TrieLongField","indexAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.solr.analysis.TrieTokenizerFactory","args":{}}},"queryAnalyzer":{"className":"org.apache.solr.analysis.TokenizerChain","tokenizer":{"className":"org.apache.solr.analysis.TrieTokenizerFactory","args":{}}},"similarity":{}}}},"info":{"key":{"I":"Indexed","T":"Tokenized","S":"Stored","D":"DocValues","M":"Multivalued","V":"TermVector Stored","o":"Store Offset With TermVector","p":"Store Position With TermVector","O":"Omit Norms","F":"Omit Term Frequencies & Positions","P":"Omit Positions","H":"Store Offsets with Positions","L":"Lazy","B":"Binary","f":"Sort Missing First","l":"Sort Missing Last"},"NOTE":"Document Frequency (df) is not updated when a document is marked for deletion.  df values include deleted documents."}}"""

SOLR_LUKE_ = """{"responseHeader":{"status":0,"QTime":5},"index":{"numDocs":8,"maxDoc":8,"deletedDocs":0,"version":15,"segmentCount":5,"current":true,"hasDeletions":false,"directory":"org.apache.lucene.store.NRTCachingDirectory:NRTCachingDirectory(org.apache.solr.store.hdfs.HdfsDirectory@5efe087b lockFactory=org.apache.solr.store.hdfs.HdfsLockFactory@5106def2; maxCacheMB=192.0 maxMergeSizeMB=16.0)","userData":{"commitTimeMSec":"1389233070579"},"lastModified":"2014-01-09T02:04:30.579Z"},"fields":{"_version_":{"type":"long","schema":"ITS-----OF------","index":"-TS-------------","docs":8,"distinct":8,"topTerms":["1456716393276768256",1,"1456716398067712000",1,"1456716401465098240",1,"1460689159964327936",1,"1460689159981105152",1,"1460689159988445184",1,"1460689159993688064",1,"1456716273606983680",1],"histogram":["1",8]},"cat":{"type":"string","schema":"I-S-M---OF-----l","index":"ITS-----OF------","docs":4,"distinct":1,"topTerms":["currency",4],"histogram":["1",0,"2",0,"4",1]},"features":{"type":"text_general","schema":"ITS-M-----------","index":"ITS-------------","docs":4,"distinct":3,"topTerms":["coins",4,"notes",4,"and",4],"histogram":["1",0,"2",0,"4",3]},"id":{"type":"string","schema":"I-S-----OF-----l","index":"ITS-----OF------","docs":8,"distinct":8,"topTerms":["GBP",1,"NOK",1,"USD",1,"change.me",1,"change.me1",1,"change.me112",1,"change.me12",1,"EUR",1],"histogram":["1",8]},"inStock":{"type":"boolean","schema":"I-S-----OF-----l","index":"ITS-----OF------","docs":4,"distinct":1,"topTerms":["true",4],"histogram":["1",0,"2",0,"4",1]},"manu":{"type":"text_general","schema":"ITS-----O-------","index":"ITS-----O-------","docs":4,"distinct":7,"topTerms":["of",2,"bank",2,"european",1,"norway",1,"u.k",1,"union",1,"america",1],"histogram":["1",5,"2",2]},"manu_exact":{"type":"string","schema":"I-------OF-----l","index":"(unstored field)","docs":4,"distinct":4,"topTerms":["Bank of Norway",1,"European Union",1,"U.K.",1,"Bank of America",1],"histogram":["1",4]},"manu_id_s":{"type":"string","schema":"I-S-----OF-----l","dynamicBase":"*_s","index":"ITS-----OF------","docs":4,"distinct":4,"topTerms":["eu",1,"nor",1,"uk",1,"boa",1],"histogram":["1",4]},"name":{"type":"text_general","schema":"ITS-------------","index":"ITS-------------","docs":4,"distinct":6,"topTerms":["one",4,"euro",1,"krone",1,"dollar",1,"pound",1,"british",1],"histogram":["1",5,"2",0,"4",1]},"price_c":{"type":"currency","schema":"I-S------F------","dynamicBase":"*_c"},"price_c____amount_raw":{"type":"amount_raw_type_tlong","schema":"IT------O-------","dynamicBase":"*____amount_raw","index":"(unstored field)","docs":4,"distinct":8,"topTerms":["0",4,"0",4,"0",4,"0",4,"0",4,"0",4,"0",4,"100",4],"histogram":["1",0,"2",0,"4",8]},"price_c____currency":{"type":"currency_type_string","schema":"I-------O-------","dynamicBase":"*____currency","index":"(unstored field)","docs":4,"distinct":4,"topTerms":["GBP",1,"NOK",1,"USD",1,"EUR",1],"histogram":["1",4]},"romain_t":{"type":"text_general","schema":"ITS-------------","dynamicBase":"*_t","index":"ITS-------------","docs":1,"distinct":1,"topTerms":["true",1],"histogram":["1",1]},"text":{"type":"text_general","schema":"IT--M-----------","index":"(unstored field)","docs":8,"distinct":21,"topTerms":["and",4,"currency",4,"notes",4,"one",4,"coins",4,"bank",2,"of",2,"change.me112",1,"change.me1",1,"change.me",1],"histogram":["1",14,"2",2,"4",5]},"title":{"type":"text_general","schema":"ITS-M-----------","index":"ITS-------------","docs":4,"distinct":4,"topTerms":["change.me1",1,"change.me112",1,"change.me12",1,"change.me",1],"histogram":["1",4]}},"info":{"key":{"I":"Indexed","T":"Tokenized","S":"Stored","D":"DocValues","M":"Multivalued","V":"TermVector Stored","o":"Store Offset With TermVector","p":"Store Position With TermVector","O":"Omit Norms","F":"Omit Term Frequencies & Positions","P":"Omit Positions","H":"Store Offsets with Positions","L":"Lazy","B":"Binary","f":"Sort Missing First","l":"Sort Missing Last"},"NOTE":"Document Frequency (df) is not updated when a document is marked for deletion.  df values include deleted documents."}}"""

SOLR_SCHEMA = """
<?xml version="1.0" encoding="UTF-8" ?>
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

   <field name="id" type="string" indexed="true" stored="true" required="true" multiValued="false" />
   <field name="sku" type="text_en_splitting_tight" indexed="true" stored="true" omitNorms="true"/>
   <field name="name" type="text_general" indexed="true" stored="true"/>
   <field name="manu" type="text_general" indexed="true" stored="true" omitNorms="true"/>
   <field name="cat" type="string" indexed="true" stored="true" multiValued="true"/>
   <field name="features" type="text_general" indexed="true" stored="true" multiValued="true"/>
   <field name="includes" type="text_general" indexed="true" stored="true" termVectors="true" termPositions="true" termOffsets="true" />

   <field name="weight" type="float" indexed="true" stored="true"/>
   <field name="price"  type="float" indexed="true" stored="true"/>
   <field name="popularity" type="int" indexed="true" stored="true" />
   <field name="inStock" type="boolean" indexed="true" stored="true" />

   <field name="store" type="location" indexed="true" stored="true"/>

   <!-- Common metadata fields, named specifically to match up with
     SolrCell metadata when parsing rich documents such as Word, PDF.
     Some fields are multiValued only because Tika currently may return
     multiple values for them. Some metadata is parsed from the documents,
     but there are some which come from the client context:
       "content_type": From the HTTP headers of incoming stream
       "resourcename": From SolrCell request param resource.name
   -->
   <field name="title" type="text_general" indexed="true" stored="true" multiValued="true"/>
   <field name="subject" type="text_general" indexed="true" stored="true"/>
   <field name="description" type="text_general" indexed="true" stored="true"/>
   <field name="comments" type="text_general" indexed="true" stored="true"/>
   <field name="author" type="text_general" indexed="true" stored="true"/>
   <field name="keywords" type="text_general" indexed="true" stored="true"/>
   <field name="category" type="text_general" indexed="true" stored="true"/>
   <field name="resourcename" type="text_general" indexed="true" stored="true"/>
   <field name="url" type="text_general" indexed="true" stored="true"/>
   <field name="content_type" type="string" indexed="true" stored="true" multiValued="true"/>
   <field name="last_modified" type="date" indexed="true" stored="true"/>
   <field name="links" type="string" indexed="true" stored="true" multiValued="true"/>

   <!-- Main body of document extracted by SolrCell.
        NOTE: This field is not indexed by default, since it is also copied to "text"
        using copyField below. This is to save space. Use this field for returning and
        highlighting document content. Use the "text" field to search the content. -->
   <field name="content" type="text_general" indexed="false" stored="true" multiValued="true"/>


   <!-- catchall field, containing all other searchable text fields (implemented
        via copyField further on in this schema  -->
   <field name="text" type="text_general" indexed="true" stored="false" multiValued="true"/>

   <!-- catchall text field that indexes tokens both normally and in reverse for efficient
        leading wildcard queries. -->
   <field name="text_rev" type="text_general_rev" indexed="true" stored="false" multiValued="true"/>

   <!-- non-tokenized version of manufacturer to make it easier to sort or group
        results by manufacturer.  copied from "manu" via copyField -->
   <field name="manu_exact" type="string" indexed="true" stored="false"/>

   <field name="payloads" type="payloads" indexed="true" stored="true"/>

   <field name="_version_" type="long" indexed="true" stored="true"/>

   <!--
     Some fields such as popularity and manu_exact could be modified to
     leverage doc values:
     <field name="popularity" type="int" indexed="true" stored="true" docValues="true" default="0" />
     <field name="manu_exact" type="string" indexed="false" stored="false" docValues="true" default="" />

     Although it would make indexing slightly slower and the index bigger, it
     would also make the index faster to load, more memory-efficient and more
     NRT-friendly.
     -->

   <!-- Dynamic field definitions allow using convention over configuration
       for fields via the specification of patterns to match field names.
       EXAMPLE:  name="*_i" will match any field ending in _i (like myid_i, z_i)
       RESTRICTION: the glob-like pattern in the name attribute must have
       a "*" only at the start or the end.  -->

   <dynamicField name="*_i"  type="int"    indexed="true"  stored="true"/>
   <dynamicField name="*_is" type="int"    indexed="true"  stored="true"  multiValued="true"/>
   <dynamicField name="*_s"  type="string"  indexed="true"  stored="true" />
   <dynamicField name="*_ss" type="string"  indexed="true"  stored="true" multiValued="true"/>
   <dynamicField name="*_l"  type="long"   indexed="true"  stored="true"/>
   <dynamicField name="*_ls" type="long"   indexed="true"  stored="true"  multiValued="true"/>
   <dynamicField name="*_t"  type="text_general"    indexed="true"  stored="true"/>
   <dynamicField name="*_txt" type="text_general"   indexed="true"  stored="true" multiValued="true"/>
   <dynamicField name="*_en"  type="text_en"    indexed="true"  stored="true" multiValued="true"/>
   <dynamicField name="*_b"  type="boolean" indexed="true" stored="true"/>
   <dynamicField name="*_bs" type="boolean" indexed="true" stored="true"  multiValued="true"/>
   <dynamicField name="*_f"  type="float"  indexed="true"  stored="true"/>
   <dynamicField name="*_fs" type="float"  indexed="true"  stored="true"  multiValued="true"/>
   <dynamicField name="*_d"  type="double" indexed="true"  stored="true"/>
   <dynamicField name="*_ds" type="double" indexed="true"  stored="true"  multiValued="true"/>

   <!-- Type used to index the lat and lon components for the "location" FieldType -->
   <dynamicField name="*_coordinate"  type="tdouble" indexed="true"  stored="false" />

   <dynamicField name="*_dt"  type="date"    indexed="true"  stored="true"/>
   <dynamicField name="*_dts" type="date"    indexed="true"  stored="true" multiValued="true"/>
   <dynamicField name="*_p"  type="location" indexed="true" stored="true"/>

   <!-- some trie-coded dynamic fields for faster range queries -->
   <dynamicField name="*_ti" type="tint"    indexed="true"  stored="true"/>
   <dynamicField name="*_tl" type="tlong"   indexed="true"  stored="true"/>
   <dynamicField name="*_tf" type="tfloat"  indexed="true"  stored="true"/>
   <dynamicField name="*_td" type="tdouble" indexed="true"  stored="true"/>
   <dynamicField name="*_tdt" type="tdate"  indexed="true"  stored="true"/>

   <dynamicField name="*_pi"  type="pint"    indexed="true"  stored="true"/>
   <dynamicField name="*_c"   type="currency" indexed="true"  stored="true"/>

   <dynamicField name="ignored_*" type="ignored" multiValued="true"/>
   <dynamicField name="attr_*" type="text_general" indexed="true" stored="true" multiValued="true"/>

   <dynamicField name="random_*" type="random" />

   <!-- uncomment the following to ignore any fields that don't already match an existing
        field name or dynamic field, rather than reporting them as an error.
        alternately, change the type="ignored" to some other type e.g. "text" if you want
        unknown fields indexed and/or stored by default -->
   <!--dynamicField name="*" type="ignored" multiValued="true" /-->

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

   <copyField source="cat" dest="text"/>
   <copyField source="name" dest="text"/>
   <copyField source="manu" dest="text"/>
   <copyField source="features" dest="text"/>
   <copyField source="includes" dest="text"/>
   <copyField source="manu" dest="manu_exact"/>

   <!-- Copy the price into a currency enabled field (default USD) -->
   <copyField source="price" dest="price_c"/>

   <!-- Text fields from SolrCell to search by default in our catch-all field -->
   <copyField source="title" dest="text"/>
   <copyField source="author" dest="text"/>
   <copyField source="description" dest="text"/>
   <copyField source="keywords" dest="text"/>
   <copyField source="content" dest="text"/>
   <copyField source="content_type" dest="text"/>
   <copyField source="resourcename" dest="text"/>
   <copyField source="url" dest="text"/>

   <!-- Create a string version of author for faceting -->
   <copyField source="author" dest="author_s"/>

   <!-- Above, multiple source fields are copied to the [text] field.
    Another way to map multiple source fields to the same
    destination field is to use the dynamic field syntax.
    copyField also supports a maxChars to copy setting.  -->

   <!-- <copyField source="*_t" dest="text" maxChars="3000"/> -->

   <!-- copy name to alphaNameSort, a field designed for sorting by name -->
   <!-- <copyField source="name" dest="alphaNameSort"/> -->

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
    <fieldType name="string" class="solr.StrField" sortMissingLast="true" />

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

    <!--
      Note:
      These should only be used for compatibility with existing indexes (created with lucene or older Solr versions).
      Use Trie based fields instead. As of Solr 3.5 and 4.x, Trie based fields support sortMissingFirst/Last

      Plain numeric field types that store and index the text
      value verbatim (and hence don't correctly support range queries, since the
      lexicographic ordering isn't equal to the numeric ordering)
    -->
    <fieldType name="pint" class="solr.IntField"/>
    <fieldType name="plong" class="solr.LongField"/>
    <fieldType name="pfloat" class="solr.FloatField"/>
    <fieldType name="pdouble" class="solr.DoubleField"/>
    <fieldType name="pdate" class="solr.DateField" sortMissingLast="true"/>

    <!-- The "RandomSortField" is not used to store or search any
         data.  You can declare fields of this type it in your schema
         to generate pseudo-random orderings of your docs for sorting
         or function purposes.  The ordering is generated based on the field
         name and the version of the index. As long as the index version
         remains unchanged, and the same field name is reused,
         the ordering of the docs will be consistent.
         If you want different psuedo-random orderings of documents,
         for the same version of the index, use a dynamicField and
         change the field name in the request.
     -->
    <fieldType name="random" class="solr.RandomSortField" indexed="true" />

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
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="stopwords.txt" />
        <!-- in this example, we will only use synonyms at query time
        <filter class="solr.SynonymFilterFactory" synonyms="index_synonyms.txt" ignoreCase="true" expand="false"/>
        -->
        <filter class="solr.LowerCaseFilterFactory"/>
      </analyzer>
      <analyzer type="query">
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="stopwords.txt" />
        <filter class="solr.SynonymFilterFactory" synonyms="synonyms.txt" ignoreCase="true" expand="true"/>
        <filter class="solr.LowerCaseFilterFactory"/>
      </analyzer>
    </fieldType>

    <!-- A text field with defaults appropriate for English: it
         tokenizes with StandardTokenizer, removes English stop words
         (lang/stopwords_en.txt), down cases, protects words from protwords.txt, and
         finally applies Porter's stemming.  The query time analyzer
         also applies synonyms from synonyms.txt. -->
    <fieldType name="text_en" class="solr.TextField" positionIncrementGap="100">
      <analyzer type="index">
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <!-- in this example, we will only use synonyms at query time
        <filter class="solr.SynonymFilterFactory" synonyms="index_synonyms.txt" ignoreCase="true" expand="false"/>
        -->
        <!-- Case insensitive stop word removal.
        -->
        <filter class="solr.StopFilterFactory"
                ignoreCase="true"
                words="lang/stopwords_en.txt"
                />
        <filter class="solr.LowerCaseFilterFactory"/>
  <filter class="solr.EnglishPossessiveFilterFactory"/>
        <filter class="solr.KeywordMarkerFilterFactory" protected="protwords.txt"/>
  <!-- Optionally you may want to use this less aggressive stemmer instead of PorterStemFilterFactory:
        <filter class="solr.EnglishMinimalStemFilterFactory"/>
  -->
        <filter class="solr.PorterStemFilterFactory"/>
      </analyzer>
      <analyzer type="query">
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.SynonymFilterFactory" synonyms="synonyms.txt" ignoreCase="true" expand="true"/>
        <filter class="solr.StopFilterFactory"
                ignoreCase="true"
                words="lang/stopwords_en.txt"
                />
        <filter class="solr.LowerCaseFilterFactory"/>
  <filter class="solr.EnglishPossessiveFilterFactory"/>
        <filter class="solr.KeywordMarkerFilterFactory" protected="protwords.txt"/>
  <!-- Optionally you may want to use this less aggressive stemmer instead of PorterStemFilterFactory:
        <filter class="solr.EnglishMinimalStemFilterFactory"/>
  -->
        <filter class="solr.PorterStemFilterFactory"/>
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
    <fieldType name="text_en_splitting" class="solr.TextField" positionIncrementGap="100" autoGeneratePhraseQueries="true">
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
        <filter class="solr.WordDelimiterFilterFactory" generateWordParts="1" generateNumberParts="1" catenateWords="1" catenateNumbers="1" catenateAll="0" splitOnCaseChange="1"/>
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
        <filter class="solr.WordDelimiterFilterFactory" generateWordParts="1" generateNumberParts="1" catenateWords="0" catenateNumbers="0" catenateAll="0" splitOnCaseChange="1"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.KeywordMarkerFilterFactory" protected="protwords.txt"/>
        <filter class="solr.PorterStemFilterFactory"/>
      </analyzer>
    </fieldType>

    <!-- Less flexible matching, but less false matches.  Probably not ideal for product names,
         but may be good for SKUs.  Can insert dashes in the wrong place and still match. -->
    <fieldType name="text_en_splitting_tight" class="solr.TextField" positionIncrementGap="100" autoGeneratePhraseQueries="true">
      <analyzer>
        <tokenizer class="solr.WhitespaceTokenizerFactory"/>
        <filter class="solr.SynonymFilterFactory" synonyms="synonyms.txt" ignoreCase="true" expand="false"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_en.txt"/>
        <filter class="solr.WordDelimiterFilterFactory" generateWordParts="0" generateNumberParts="0" catenateWords="1" catenateNumbers="1" catenateAll="0"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.KeywordMarkerFilterFactory" protected="protwords.txt"/>
        <filter class="solr.EnglishMinimalStemFilterFactory"/>
        <!-- this filter can remove any duplicate tokens that appear at the same position - sometimes
             possible with WordDelimiterFilter in conjuncton with stemming. -->
        <filter class="solr.RemoveDuplicatesTokenFilterFactory"/>
      </analyzer>
    </fieldType>

    <!-- Just like text_general except it reverses the characters of
   each token, to enable more efficient leading wildcard queries. -->
    <fieldType name="text_general_rev" class="solr.TextField" positionIncrementGap="100">
      <analyzer type="index">
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="stopwords.txt" />
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.ReversedWildcardFilterFactory" withOriginal="true"
           maxPosAsterisk="3" maxPosQuestion="2" maxFractionAsterisk="0.33"/>
      </analyzer>
      <analyzer type="query">
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.SynonymFilterFactory" synonyms="synonyms.txt" ignoreCase="true" expand="true"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="stopwords.txt" />
        <filter class="solr.LowerCaseFilterFactory"/>
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
        <filter class="solr.LowerCaseFilterFactory" />
        <!-- The TrimFilter removes any leading or trailing whitespace -->
        <filter class="solr.TrimFilterFactory" />
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

    <fieldtype name="phonetic" stored="false" indexed="true" class="solr.TextField" >
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.DoubleMetaphoneFilterFactory" inject="false"/>
      </analyzer>
    </fieldtype>

    <fieldtype name="payloads" stored="false" indexed="true" class="solr.TextField" >
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
        <filter class="solr.LowerCaseFilterFactory" />
      </analyzer>
    </fieldType>

    <!--
      Example of using PathHierarchyTokenizerFactory at index time, so
      queries for paths match documents at that path, or in descendent paths
    -->
    <fieldType name="descendent_path" class="solr.TextField">
      <analyzer type="index">
  <tokenizer class="solr.PathHierarchyTokenizerFactory" delimiter="/" />
      </analyzer>
      <analyzer type="query">
  <tokenizer class="solr.KeywordTokenizerFactory" />
      </analyzer>
    </fieldType>
    <!--
      Example of using PathHierarchyTokenizerFactory at query time, so
      queries for paths match documents at that path, or in ancestor paths
    -->
    <fieldType name="ancestor_path" class="solr.TextField">
      <analyzer type="index">
  <tokenizer class="solr.KeywordTokenizerFactory" />
      </analyzer>
      <analyzer type="query">
  <tokenizer class="solr.PathHierarchyTokenizerFactory" delimiter="/" />
      </analyzer>
    </fieldType>

    <!-- since fields of this type are by default not stored or indexed,
         any data added to them will be ignored outright.  -->
    <fieldtype name="ignored" stored="false" indexed="false" multiValued="true" class="solr.StrField" />

    <!-- This point type indexes the coordinates as separate fields (subFields)
      If subFieldType is defined, it references a type, and a dynamic field
      definition is created matching *___<typename>.  Alternately, if
      subFieldSuffix is defined, that is used to create the subFields.
      Example: if subFieldType="double", then the coordinates would be
        indexed in fields myloc_0___double,myloc_1___double.
      Example: if subFieldSuffix="_d" then the coordinates would be indexed
        in fields myloc_0_d,myloc_1_d
      The subFields are an implementation detail of the fieldType, and end
      users normally should not need to know about them.
     -->
    <fieldType name="point" class="solr.PointType" dimension="2" subFieldSuffix="_d"/>

    <!-- A specialized field for geospatial search. If indexed, this fieldType must not be multivalued. -->
    <fieldType name="location" class="solr.LatLonType" subFieldSuffix="_coordinate"/>

    <!-- An alternative geospatial field type new to Solr 4.  It supports multiValued and polygon shapes.
      For more information about this and other Spatial fields new to Solr 4, see:
      http://wiki.apache.org/solr/SolrAdaptersForLuceneSpatial4
    -->
    <fieldType name="location_rpt" class="solr.SpatialRecursivePrefixTreeFieldType"
        geo="true" distErrPct="0.025" maxDistErr="0.000009" units="degrees" />

   <!-- Money/currency field type. See http://wiki.apache.org/solr/MoneyFieldType
        Parameters:
          defaultCurrency: Specifies the default currency if none specified. Defaults to "USD"
          precisionStep:   Specifies the precisionStep for the TrieLong field used for the amount
          providerClass:   Lets you plug in other exchange provider backend:
                           solr.FileExchangeRateProvider is the default and takes one parameter:
                             currencyConfig: name of an xml file holding exchange rates
                           solr.OpenExchangeRatesOrgProvider uses rates from openexchangerates.org:
                             ratesFileLocation: URL or path to rates JSON file (default latest.json on the web)
                             refreshInterval: Number of minutes between each rates fetch (default: 1440, min: 60)
   -->
    <fieldType name="currency" class="solr.CurrencyField" precisionStep="8" defaultCurrency="USD" currencyConfig="currency.xml" />



   <!-- some examples for different languages (generally ordered by ISO code) -->

    <!-- Arabic -->
    <fieldType name="text_ar" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <!-- for any non-arabic -->
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_ar.txt" />
        <!-- normalizes ﻯ to ﻱ, etc -->
        <filter class="solr.ArabicNormalizationFilterFactory"/>
        <filter class="solr.ArabicStemFilterFactory"/>
      </analyzer>
    </fieldType>

    <!-- Bulgarian -->
    <fieldType name="text_bg" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_bg.txt" />
        <filter class="solr.BulgarianStemFilterFactory"/>
      </analyzer>
    </fieldType>

    <!-- Catalan -->
    <fieldType name="text_ca" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <!-- removes l', etc -->
        <filter class="solr.ElisionFilterFactory" ignoreCase="true" articles="lang/contractions_ca.txt"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_ca.txt" />
        <filter class="solr.SnowballPorterFilterFactory" language="Catalan"/>
      </analyzer>
    </fieldType>

    <!-- CJK bigram (see text_ja for a Japanese configuration using morphological analysis) -->
    <fieldType name="text_cjk" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <!-- normalize width before bigram, as e.g. half-width dakuten combine  -->
        <filter class="solr.CJKWidthFilterFactory"/>
        <!-- for any non-CJK -->
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.CJKBigramFilterFactory"/>
      </analyzer>
    </fieldType>

    <!-- Czech -->
    <fieldType name="text_cz" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_cz.txt" />
        <filter class="solr.CzechStemFilterFactory"/>
      </analyzer>
    </fieldType>

    <!-- Danish -->
    <fieldType name="text_da" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_da.txt" format="snowball" />
        <filter class="solr.SnowballPorterFilterFactory" language="Danish"/>
      </analyzer>
    </fieldType>

    <!-- German -->
    <fieldType name="text_de" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_de.txt" format="snowball" />
        <filter class="solr.GermanNormalizationFilterFactory"/>
        <filter class="solr.GermanLightStemFilterFactory"/>
        <!-- less aggressive: <filter class="solr.GermanMinimalStemFilterFactory"/> -->
        <!-- more aggressive: <filter class="solr.SnowballPorterFilterFactory" language="German2"/> -->
      </analyzer>
    </fieldType>

    <!-- Greek -->
    <fieldType name="text_el" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <!-- greek specific lowercase for sigma -->
        <filter class="solr.GreekLowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="false" words="lang/stopwords_el.txt" />
        <filter class="solr.GreekStemFilterFactory"/>
      </analyzer>
    </fieldType>

    <!-- Spanish -->
    <fieldType name="text_es" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_es.txt" format="snowball" />
        <filter class="solr.SpanishLightStemFilterFactory"/>
        <!-- more aggressive: <filter class="solr.SnowballPorterFilterFactory" language="Spanish"/> -->
      </analyzer>
    </fieldType>

    <!-- Basque -->
    <fieldType name="text_eu" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_eu.txt" />
        <filter class="solr.SnowballPorterFilterFactory" language="Basque"/>
      </analyzer>
    </fieldType>

    <!-- Persian -->
    <fieldType name="text_fa" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <!-- for ZWNJ -->
        <charFilter class="solr.PersianCharFilterFactory"/>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.ArabicNormalizationFilterFactory"/>
        <filter class="solr.PersianNormalizationFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_fa.txt" />
      </analyzer>
    </fieldType>

    <!-- Finnish -->
    <fieldType name="text_fi" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_fi.txt" format="snowball" />
        <filter class="solr.SnowballPorterFilterFactory" language="Finnish"/>
        <!-- less aggressive: <filter class="solr.FinnishLightStemFilterFactory"/> -->
      </analyzer>
    </fieldType>

    <!-- French -->
    <fieldType name="text_fr" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <!-- removes l', etc -->
        <filter class="solr.ElisionFilterFactory" ignoreCase="true" articles="lang/contractions_fr.txt"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_fr.txt" format="snowball" />
        <filter class="solr.FrenchLightStemFilterFactory"/>
        <!-- less aggressive: <filter class="solr.FrenchMinimalStemFilterFactory"/> -->
        <!-- more aggressive: <filter class="solr.SnowballPorterFilterFactory" language="French"/> -->
      </analyzer>
    </fieldType>

    <!-- Irish -->
    <fieldType name="text_ga" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <!-- removes d', etc -->
        <filter class="solr.ElisionFilterFactory" ignoreCase="true" articles="lang/contractions_ga.txt"/>
        <!-- removes n-, etc. position increments is intentionally false! -->
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/hyphenations_ga.txt"/>
        <filter class="solr.IrishLowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_ga.txt"/>
        <filter class="solr.SnowballPorterFilterFactory" language="Irish"/>
      </analyzer>
    </fieldType>

    <!-- Galician -->
    <fieldType name="text_gl" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_gl.txt" />
        <filter class="solr.GalicianStemFilterFactory"/>
        <!-- less aggressive: <filter class="solr.GalicianMinimalStemFilterFactory"/> -->
      </analyzer>
    </fieldType>

    <!-- Hindi -->
    <fieldType name="text_hi" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <!-- normalizes unicode representation -->
        <filter class="solr.IndicNormalizationFilterFactory"/>
        <!-- normalizes variation in spelling -->
        <filter class="solr.HindiNormalizationFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_hi.txt" />
        <filter class="solr.HindiStemFilterFactory"/>
      </analyzer>
    </fieldType>

    <!-- Hungarian -->
    <fieldType name="text_hu" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_hu.txt" format="snowball" />
        <filter class="solr.SnowballPorterFilterFactory" language="Hungarian"/>
        <!-- less aggressive: <filter class="solr.HungarianLightStemFilterFactory"/> -->
      </analyzer>
    </fieldType>

    <!-- Armenian -->
    <fieldType name="text_hy" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_hy.txt" />
        <filter class="solr.SnowballPorterFilterFactory" language="Armenian"/>
      </analyzer>
    </fieldType>

    <!-- Indonesian -->
    <fieldType name="text_id" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_id.txt" />
        <!-- for a less aggressive approach (only inflectional suffixes), set stemDerivational to false -->
        <filter class="solr.IndonesianStemFilterFactory" stemDerivational="true"/>
      </analyzer>
    </fieldType>

    <!-- Italian -->
    <fieldType name="text_it" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <!-- removes l', etc -->
        <filter class="solr.ElisionFilterFactory" ignoreCase="true" articles="lang/contractions_it.txt"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_it.txt" format="snowball" />
        <filter class="solr.ItalianLightStemFilterFactory"/>
        <!-- more aggressive: <filter class="solr.SnowballPorterFilterFactory" language="Italian"/> -->
      </analyzer>
    </fieldType>

    <!-- Japanese using morphological analysis (see text_cjk for a configuration using bigramming)

         NOTE: If you want to optimize search for precision, use default operator AND in your query
         parser config with <solrQueryParser defaultOperator="AND"/> further down in this file.  Use
         OR if you would like to optimize for recall (default).
    -->
    <fieldType name="text_ja" class="solr.TextField" positionIncrementGap="100" autoGeneratePhraseQueries="false">
      <analyzer>
      <!-- Kuromoji Japanese morphological analyzer/tokenizer (JapaneseTokenizer)

           Kuromoji has a search mode (default) that does segmentation useful for search.  A heuristic
           is used to segment compounds into its parts and the compound itself is kept as synonym.

           Valid values for attribute mode are:
              normal: regular segmentation
              search: segmentation useful for search with synonyms compounds (default)
            extended: same as search mode, but unigrams unknown words (experimental)

           For some applications it might be good to use search mode for indexing and normal mode for
           queries to reduce recall and prevent parts of compounds from being matched and highlighted.
           Use <analyzer type="index"> and <analyzer type="query"> for this and mode normal in query.

           Kuromoji also has a convenient user dictionary feature that allows overriding the statistical
           model with your own entries for segmentation, part-of-speech tags and readings without a need
           to specify weights.  Notice that user dictionaries have not been subject to extensive testing.

           User dictionary attributes are:
                     userDictionary: user dictionary filename
             userDictionaryEncoding: user dictionary encoding (default is UTF-8)

           See lang/userdict_ja.txt for a sample user dictionary file.

           Punctuation characters are discarded by default.  Use discardPunctuation="false" to keep them.

           See http://wiki.apache.org/solr/JapaneseLanguageSupport for more on Japanese language support.
        -->
        <tokenizer class="solr.JapaneseTokenizerFactory" mode="search"/>
        <!--<tokenizer class="solr.JapaneseTokenizerFactory" mode="search" userDictionary="lang/userdict_ja.txt"/>-->
        <!-- Reduces inflected verbs and adjectives to their base/dictionary forms (辞書形) -->
        <filter class="solr.JapaneseBaseFormFilterFactory"/>
        <!-- Removes tokens with certain part-of-speech tags -->
        <filter class="solr.JapanesePartOfSpeechStopFilterFactory" tags="lang/stoptags_ja.txt" />
        <!-- Normalizes full-width romaji to half-width and half-width kana to full-width (Unicode NFKC subset) -->
        <filter class="solr.CJKWidthFilterFactory"/>
        <!-- Removes common tokens typically not useful for search, but have a negative effect on ranking -->
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_ja.txt" />
        <!-- Normalizes common katakana spelling variations by removing any last long sound character (U+30FC) -->
        <filter class="solr.JapaneseKatakanaStemFilterFactory" minimumLength="4"/>
        <!-- Lower-cases romaji characters -->
        <filter class="solr.LowerCaseFilterFactory"/>
      </analyzer>
    </fieldType>

    <!-- Latvian -->
    <fieldType name="text_lv" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_lv.txt" />
        <filter class="solr.LatvianStemFilterFactory"/>
      </analyzer>
    </fieldType>

    <!-- Dutch -->
    <fieldType name="text_nl" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_nl.txt" format="snowball" />
        <filter class="solr.StemmerOverrideFilterFactory" dictionary="lang/stemdict_nl.txt" ignoreCase="false"/>
        <filter class="solr.SnowballPorterFilterFactory" language="Dutch"/>
      </analyzer>
    </fieldType>

    <!-- Norwegian -->
    <fieldType name="text_no" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_no.txt" format="snowball" />
        <filter class="solr.SnowballPorterFilterFactory" language="Norwegian"/>
        <!-- less aggressive: <filter class="solr.NorwegianLightStemFilterFactory" variant="nb"/> -->
        <!-- singular/plural: <filter class="solr.NorwegianMinimalStemFilterFactory" variant="nb"/> -->
        <!-- The "light" and "minimal" stemmers support variants: nb=Bokmål, nn=Nynorsk, no=Both -->
      </analyzer>
    </fieldType>

    <!-- Portuguese -->
    <fieldType name="text_pt" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_pt.txt" format="snowball" />
        <filter class="solr.PortugueseLightStemFilterFactory"/>
        <!-- less aggressive: <filter class="solr.PortugueseMinimalStemFilterFactory"/> -->
        <!-- more aggressive: <filter class="solr.SnowballPorterFilterFactory" language="Portuguese"/> -->
        <!-- most aggressive: <filter class="solr.PortugueseStemFilterFactory"/> -->
      </analyzer>
    </fieldType>

    <!-- Romanian -->
    <fieldType name="text_ro" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_ro.txt" />
        <filter class="solr.SnowballPorterFilterFactory" language="Romanian"/>
      </analyzer>
    </fieldType>

    <!-- Russian -->
    <fieldType name="text_ru" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_ru.txt" format="snowball" />
        <filter class="solr.SnowballPorterFilterFactory" language="Russian"/>
        <!-- less aggressive: <filter class="solr.RussianLightStemFilterFactory"/> -->
      </analyzer>
    </fieldType>

    <!-- Swedish -->
    <fieldType name="text_sv" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_sv.txt" format="snowball" />
        <filter class="solr.SnowballPorterFilterFactory" language="Swedish"/>
        <!-- less aggressive: <filter class="solr.SwedishLightStemFilterFactory"/> -->
      </analyzer>
    </fieldType>

    <!-- Thai -->
    <fieldType name="text_th" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.LowerCaseFilterFactory"/>
        <filter class="solr.ThaiWordFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="true" words="lang/stopwords_th.txt" />
      </analyzer>
    </fieldType>

    <!-- Turkish -->
    <fieldType name="text_tr" class="solr.TextField" positionIncrementGap="100">
      <analyzer>
        <tokenizer class="solr.StandardTokenizerFactory"/>
        <filter class="solr.TurkishLowerCaseFilterFactory"/>
        <filter class="solr.StopFilterFactory" ignoreCase="false" words="lang/stopwords_tr.txt" />
        <filter class="solr.SnowballPorterFilterFactory" language="Turkish"/>
      </analyzer>
    </fieldType>

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
