from __future__ import absolute_import

import os
import os.path
import shutil
import subprocess

from .os import pushd


class RepoNotFoundError(Exception):
    pass


class Repo(object):

    BRANCH = None

    COMMAND = None
    COMMANDS = {}

    def __getattr__(self, name):
        try:
            args = self.COMMANDS[name]
        except KeyError:
            raise AttributeError(name)
        return lambda dirname=None: self._cmd(name, dirname)

    def _cmd(self, cmd, dirname=None):
        # XXX sanitize dirname?
        if dirname is None:
            dirname = '.'
        try:
            args = self.COMMANDS[cmd]
        except KeyError:
            raise NotImplementedError(cmd)
        cmd = '{} {}'.format(self.COMMAND, args)
        with pushd(dirname):
            try:
                output = subprocess.check_output(cmd, shell=True)
            except subprocess.CalledProcessError as e:
                if self._repo_not_found(e):
                    raise RepoNotFoundError
                raise
        return output.decode().strip()

    def listdir(dirname=None):
        output = self._cmd('listdir', dirname)
        return output.splitlines()

    def _copy_file(self, filename, source, target, verbose, dryrun):
        if isinstance(filename, str):
            sfilename = filename
            tfilename = filename
        else:
            sfilename, tfilename = filename
        spath = os.path.join(source, sfilename)
        tpath = os.path.join(target, tfilename)

        if verbose:
            if sfilename == tfilename:
                print(sfilename)
            else:
                print('{} -> {}'.format(sfilename, tfilename))

        if not dryrun:
            try:
                os.makedirs(target)
            except OSError:
                pass
            shutil.copy2(spath, tpath)

    def _copy_files(self, source, target, verbose, dryrun, filenames):
        source = os.path.abspath(source) + os.path.sep
        target = os.path.abspath(target) + os.path.sep
        if verbose:
            print('------------------------------')
            print(source)
            print('  to')
            print(target)
            print('------------------------------')
        for filename in filenames:
            self._copy_file(filename, source, target, verbose, dryrun)

    def copytree(self, source, target, verbose=True, dryrun=False):
        filenames = self.listdir(source)
        self._copy_files(source, target, verbose, dryrun, filenames)

    def copyfile(self, source, target, verbose=True, dryrun=False):
        sfilename = os.path.basename(source)
        source = os.path.dirname(source)

        if target.endswith('/'):
            filenames = [sfilename]
        else:
            tfilename = os.path.basename(target)
            filenames = [(sfilename, tfilename)]
            target = os.path.dirname(target)

        self._copy_files(source, target, verbose, dryrun, filenames)


class HGRepo(Repo):

    BRANCH = 'default'

    COMMAND = 'hg'
    COMMANDS = {'branch': 'branch',
                'root': 'root',
                'listdir': 'status -n -c .',
                'revision': 'id -i',
                }


class GitRepo(Repo):

    BRANCH = 'master'

    COMMAND = 'git'
    COMMANDS = {'branch': 'rev-parse --abbrev-ref HEAD',
                'root': 'rev-parse --show-toplevel',
                }
