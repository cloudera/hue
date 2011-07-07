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
# a thirdparty project

import sys, os, logging
from django.core.management.base import BaseCommand

from desktop import conf


CPSERVER_HELP = r"""
  Run Hue using the CherryPy WSGI server.
"""

CPSERVER_OPTIONS = {
  'host': conf.HTTP_HOST.get(),
  'port': conf.HTTP_PORT.get(),
  'server_name': 'localhost',
  'threads': conf.CHERRYPY_SERVER_THREADS.get(),
  'daemonize': False, # supervisor does this for us
  'workdir': None,
  'pidfile': None,
  'server_user': conf.SERVER_USER.get(),
  'server_group': conf.SERVER_GROUP.get(),
  'ssl_certificate': conf.SSL_CERTIFICATE.get(),
  'ssl_private_key': conf.SSL_PRIVATE_KEY.get()
}


class Command(BaseCommand):
    help = "CherryPy Server for Desktop."
    args = ""

    def handle(self, *args, **options):
        from django.conf import settings
        from django.utils import translation

        if not conf.ENABLE_SERVER.get():
          logging.info("Hue is configured to not start its own web server.")
          sys.exit(0)

        # Activate the current language, because it won't get activated later.
        try:
            translation.activate(settings.LANGUAGE_CODE)
        except AttributeError:
            pass
        runcpserver(args)
        
    def usage(self, subcommand):
        return CPSERVER_HELP

def change_uid_gid(uid, gid=None):
    """Try to change UID and GID to the provided values.
    UID and GID are given as names like 'nobody' not integer.

    Src: http://mail.mems-exchange.org/durusmail/quixote-users/4940/1/
    """
    if not os.geteuid() == 0:
        # Do not try to change the gid/uid if not root.
        return
    (uid, gid) = get_uid_gid(uid, gid)
    os.setgid(gid)
    os.setuid(uid)

def get_uid_gid(uid, gid=None):
    """Try to change UID and GID to the provided values.
    UID and GID are given as names like 'nobody' not integer.

    Src: http://mail.mems-exchange.org/durusmail/quixote-users/4940/1/
    """
    import pwd, grp
    uid, default_grp = pwd.getpwnam(uid)[2:4]
    if gid is None:
        gid = default_grp
    else:
        try:
            gid = grp.getgrnam(gid)[2]            
        except KeyError:
            gid = default_grp
    return (uid, gid)

def drop_privileges_if_necessary(options):
  if os.geteuid() == 0 and options['server_user'] and options['server_group']:
    #ensure the that the daemon runs as specified user
    change_uid_gid(options['server_user'], options['server_group'])

def start_server(options):
    """
    Start CherryPy server
    """
    from desktop.lib.wsgiserver import CherryPyWSGIServer as Server
    from django.core.handlers.wsgi import WSGIHandler
    # Translogger wraps a WSGI app with Apache-style combined logging.
    server = Server(
        (options['host'], int(options['port'])),
        WSGIHandler(),
        int(options['threads']), 
        options['server_name']
    )
    if options['ssl_certificate'] and options['ssl_private_key']:
        server.ssl_certificate = options['ssl_certificate']
        server.ssl_private_key = options['ssl_private_key']  
    try:
        server.bind_server()
        drop_privileges_if_necessary(options)
        server.listen_and_loop()
    except KeyboardInterrupt:
        server.stop()


def runcpserver(argset=[], **kwargs):
    # Get the options
    options = CPSERVER_OPTIONS.copy()
    options.update(kwargs)
    for x in argset:
        if "=" in x:
            k, v = x.split('=', 1)
        else:
            k, v = x, True
        options[k.lower()] = v
    
    if "help" in options:
        print CPSERVER_HELP
        return

    # Start the webserver
    print 'starting server with options %s' % options
    start_server(options)


if __name__ == '__main__':
    runcpserver(sys.argv[1:])
