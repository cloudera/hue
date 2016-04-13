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

import logging

import stat as stat_module


logger = logging.getLogger(__name__)


def do_overwrite_save(fs, path, data):

    def copy_data(path_dest):
        try:
            fs.create(path_dest, overwrite=False, data=data)
            logging.info("Wrote to " + path_dest)
        except Exception, e:
            # An error occurred in writing, we should clean up
            # the tmp file if it exists, before re-raising
            try:
                fs.remove(path_dest, skip_trash=True)
            except:
                logger.exception('failed to remove %s' % path_dest)
            raise e

    _do_overwrite(fs, path, copy_data)


def remove_header(fs, path):

    def copy_data(path_dest):
        fs.copyfile(path, path_dest, skip_header=True)

    _do_overwrite(fs, path, copy_data)


def _do_overwrite(fs, path, copy_data):
    """
    Atomically (best-effort) save the specified data to the given path
    on the filesystem.
    """
    # TODO(todd) Should probably do an advisory permissions check here to
    # see if we're likely to fail (eg make sure we own the file
    # and can write to the dir)

    # First write somewhat-kinda-atomically to a staging file
    # so that if we fail, we don't clobber the old one
    path_dest = path + "._hue_new"

    # Copy the data to destination
    copy_data(path_dest)

    # Try to match the permissions and ownership of the old file
    cur_stats = fs.stats(path)
    try:
        fs.do_as_superuser(fs.chmod, path_dest, stat_module.S_IMODE(cur_stats['mode']))
    except:
        logging.exception("Could not chmod new file %s to match old file %s" % (path_dest, path))
        # but not the end of the world - keep going

    try:
        fs.do_as_superuser(fs.chown, path_dest, cur_stats['user'], cur_stats['group'])
    except:
        logging.exception("Could not chown new file %s to match old file %s" % (path_dest, path))
        # but not the end of the world - keep going

    # Now delete the old - nothing we can do here to recover
    fs.remove(path, skip_trash=True)

    # Now move the new one into place
    # If this fails, then we have no reason to assume
    # we can do anything to recover, since we know the
    # destination shouldn't already exist (we just deleted it above)
    fs.rename(path_dest, path)


