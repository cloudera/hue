#!/usr/bin/env python

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

import os
import sys

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
import desktop.conf
from desktop.models import Document, Document2
from django.contrib.auth.models import User
import desktop.conf

import logging
import logging.handlers

if sys.version_info[0] > 2:
  from django.utils.translation import gettext_lazy as _t, gettext as _
else:
  from django.utils.translation import ugettext_lazy as _t, ugettext as _

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Handler for purging cleaning up doc2 objets missing content objects
    """

    def handle(self, *args, **options):

        LOG.info("Cleaning up Doc2 objects missing content object")

        model_class = Document2
        extra = "workflow2"
        qfilter = None

        idlist = []

        for user in User.objects.filter():
            LOG.info("Idlist: %s" % idlist)
            LOG.info("User: user: %s" % user.username)
            docs = Document.objects.documents(user).exclude(name='pig-app-hue-script')
            duplicated_records = Document.objects.values('name', 'owner').annotate(name_count=models.Count('name')).filter(name_count__gt=1, owner = user)
            names = []
            for obj in duplicated_records:
                names.append(obj["name"])

            duplicate_doc_ids = []
            doclist = Document.objects.values('id', 'name', 'owner').filter(owner = user)
            for obj in doclist:
                if obj["name"] in names:
                    duplicate_doc_ids.append(obj["id"])

            LOG.info("Docs: docs: %s" % docs)

            if model_class is not None:
                ct = ContentType.objects.get_for_model(model_class)
                docs = docs.filter(content_type=ct)

            if extra is not None:
                docs = docs.filter(extra=extra)

            if qfilter is not None:
                docs = docs.filter(qfilter)

            LOG.info("Grabbing only duplicates")
            docs = docs.filter(id__in=duplicate_doc_ids)
            for d in docs:
                try:
                    if d.content_object is None:
                        LOG.info("Adding document id %s with name %s and owner %s to idlist" % (d.id, d.name, user.username))
                        idlist.append(d.id)
                except:
                    pass


        deldocs = Document.objects.filter(id__in=idlist)
        LOG.info("Docs to delete are: %s" % deldocs)
        deldocs.delete()
