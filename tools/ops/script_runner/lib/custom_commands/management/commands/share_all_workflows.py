#!/usr/bin/env python
import os
import sys

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _t, ugettext as _
import desktop.conf
from desktop.models import Document2
from django.contrib.auth.models import User, Group
import desktop.conf

import logging
import logging.handlers

LOG = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Handler for sharing workflows
    """

    try:
        from optparse import make_option
        option_list = BaseCommand.option_list + (
            make_option("--shareusers", help=_t("Comma separated list of users to share all workflows with."),
                        action="store"),
            make_option("--sharegroups", help=_t("Comma separated list of groups to share all workflows with."),
                        action="store"),
            make_option("--owner", help=_t("Give permissions to only workflows owned by this user."),
                        action="store"),
            make_option("--permissions", help=_t("Comma separated list of permissions for the users and groups."
                                                 "read, write or read,write"), action="store"),
        )

    except AttributeError, e:
        baseoption_test = 'BaseCommand' in str(e) and 'option_list' in str(e)
        if baseoption_test:
            def add_arguments(self, parser):
                parser.add_argument("--shareusers", help=_t("Comma separated list of users to share all workflows with."),
                        action="store"),
                parser.add_argument("--sharegroups", help=_t("Comma separated list of groups to share all workflows with."),
                        action="store"),
                parser.add_argument("--owner", help=_t("Give permissions to only workflows owned by this user."),
                        action="store"),
                parser.add_argument("--permissions", help=_t("Comma separated list of permissions for the users and groups."
                                                 "read, write or read,write"), action="store")
        else:
            LOG.exception(str(e))
            sys.exit(1)

    def handle(self, *args, **options):

        if not options['shareusers'] and not options['sharegroups']:
            LOG.warn("You must set either shareusers or sharegroups or both")
            sys.exit(1)

        if not options['permissions']:
            LOG.warn("permissions option required either read, write or read,write")
            sys.exit(1)

        if options['shareusers']:
            users = options['shareusers'].split(",")
        else:
            users = []

        if options['sharegroups']:
            groups = options['sharegroups'].split(",")
        else:
            groups = []

        perms = options['permissions'].split(",")

        LOG.info("Setting permissions %s on all workflows for users: %s" % (perms, users))
        LOG.info("Setting permissions %s on all workflows for groups: %s" % (perms, groups))

        shareusers = User.objects.filter(username__in=users)
        sharegroups = Group.objects.filter(name__in=groups)

        doc_types = ['oozie-workflow2', 'oozie-coordinator2', 'oozie-bundle2']
        workflow_owner = User.objects.get(username = options['owner'])

        if options['owner']:
            LOG.info("Only setting permissions for workflows owned by %s" % options['owner'])
            oozie_docs = Document2.objects.filter(type__in=doc_types, owner = workflow_owner)
        else:
            oozie_docs = Document2.objects.filter(type__in=doc_types)

        for perm in perms:
            if perm in ['read', 'write']:
                for oozie_doc in oozie_docs:
                    owner = User.objects.get(id = oozie_doc.owner_id)
                    read_perms = oozie_doc.to_dict()['perms']['read']
                    write_perms = oozie_doc.to_dict()['perms']['write']

                    read_users = []
                    write_users = []
                    read_groups = []
                    write_groups = []

                    for user in read_perms['users']:
                        read_users.append(user['id'])

                    for group in read_perms['groups']:
                        read_groups.append(group['id'])

                    for user in write_perms['users']:
                        write_users.append(user['id'])

                    for group in write_perms['groups']:
                        write_groups.append(group['id'])

                    for user in shareusers:
                        if perm == 'read':
                            read_users.append(user.id)

                        if perm == 'write':
                            write_users.append(user.id)

                    for group in sharegroups:
                        if perm == 'read':
                            read_groups.append(group.id)

                        if perm == 'write':
                            write_groups.append(group.id)

                    if perm == 'read':
                        users = User.objects.in_bulk(read_users)
                        groups = Group.objects.in_bulk(read_groups)

                    if perm == 'write':
                        users = User.objects.in_bulk(write_users)
                        groups = Group.objects.in_bulk(write_groups)

                    LOG.warn("Setting %s on %s for users: %s : groups: %s" % (perm, oozie_doc.name, users, groups))
                    oozie_doc.share(owner, name=perm, users=users, groups=groups)

