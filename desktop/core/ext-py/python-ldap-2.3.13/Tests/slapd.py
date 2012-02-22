
"""
Utilities for starting up a test slapd server 
and talking to it with ldapsearch/ldapadd.
"""

import sys, os, socket, time, subprocess, logging

_log = logging.getLogger("slapd")

def quote(s):
    '''Quotes the '"' and '\' characters in a string and surrounds with "..."'''
    return '"' + s.replace('\\','\\\\').replace('"','\\"') + '"'

def mkdirs(path):
    """Creates the directory path unless it already exists"""
    if not os.access(os.path.join(path, os.path.curdir), os.F_OK):
        _log.debug("creating temp directory %s", path)
        os.mkdir(path)
    return path

def delete_directory_content(path):
    for dirpath,dirnames,filenames in os.walk(path, topdown=False):
        for n in filenames: 
            _log.info("remove %s", os.path.join(dirpath, n))
            os.remove(os.path.join(dirpath, n))
        for n in dirnames: 
            _log.info("rmdir %s", os.path.join(dirpath, n))
            os.rmdir(os.path.join(dirpath, n))

LOCALHOST = '127.0.0.1'

def find_available_tcp_port(host=LOCALHOST):
    s = socket.socket()
    s.bind((host, 0))
    port = s.getsockname()[1]
    s.close()
    _log.info("Found available port %d", port)
    return port

class Slapd:
    """
    Controller class for a slapd instance, OpenLDAP's server.

    This class creates a temporary data store for slapd, runs it
    on a private port, and initialises it with a top-level dc and
    the root user.

    When a reference to an instance of this class is lost, the slapd
    server is shut down.
    """

    _log = logging.getLogger("Slapd")

    # Use /var/tmp to placate apparmour on Ubuntu:
    PATH_TMPDIR = "/var/tmp/python-ldap-test"  
    PATH_SBINDIR = "/usr/sbin"
    PATH_BINDIR = "/usr/bin"
    PATH_SCHEMA_CORE = "/etc/ldap/schema/core.schema"
    PATH_LDAPADD = os.path.join(PATH_BINDIR, "ldapadd")
    PATH_LDAPSEARCH = os.path.join(PATH_BINDIR, "ldapsearch")
    PATH_SLAPD = os.path.join(PATH_SBINDIR, "slapd")
    PATH_SLAPTEST = os.path.join(PATH_SBINDIR, "slaptest")

    # TODO add paths for other OSs

    def check_paths(cls):
        """
        Checks that the configured executable paths look valid.
        If they don't, then logs warning messages (not errors).
        """
        for name,path in (
                ("slapd", cls.PATH_SLAPD),
                ("ldapadd", cls.PATH_LDAPADD),
                ("ldapsearch", cls.PATH_LDAPSEARCH),
             ):
            cls._log.debug("checking %s executable at %s", name, path)
            if not os.access(path, os.X_OK):
                cls._log.warn("cannot find %s executable at %s", name, path)
    check_paths = classmethod(check_paths)

    def __init__(self):
        self._config = []
        self._proc = None
        self._port = 0
        self._tmpdir = self.PATH_TMPDIR
        self._dn_suffix = "dc=python-ldap,dc=org"
        self._root_cn = "Manager"
        self._root_password = "password"
        self._slapd_debug_level = 0

    # Setters 
    def set_port(self, port):
        self._port = port
    def set_dn_suffix(self, dn):
        self._dn_suffix = dn
    def set_root_cn(self, cn):
        self._root_cn = cn
    def set_root_password(self, pw):
        self._root_password = pw
    def set_tmpdir(self, path):
        self._tmpdir = path
    def set_slapd_debug_level(self, level):
        self._slapd_debug_level = level
    def set_debug(self):
        self._log.setLevel(logging.DEBUG)
        self.set_slapd_debug_level('Any')

    # getters
    def get_url(self):
        return "ldap://%s:%d/" % self.get_address()
    def get_address(self):
        if self._port == 0:
            self._port = find_available_tcp_port(LOCALHOST)
        return (LOCALHOST, self._port)
    def get_dn_suffix(self):
        return self._dn_suffix
    def get_root_dn(self):
        return "cn=" + self._root_cn + "," + self.get_dn_suffix()
    def get_root_password(self):
        return self._root_password
    def get_tmpdir(self):
        return self._tmpdir

    def __del__(self):
        self.stop()

    def configure(self, cfg):
        """
        Appends slapd.conf configuration lines to cfg.
        Also re-initializes any backing storage.
        Feel free to subclass and override this method.
        """

        # Global
        cfg.append("include " + quote(self.PATH_SCHEMA_CORE))
        cfg.append("allow bind_v2")

        # Database
        ldif_dir = mkdirs(os.path.join(self.get_tmpdir(), "ldif-data"))
        delete_directory_content(ldif_dir) # clear it out
        cfg.append("database ldif")
        cfg.append("directory " + quote(ldif_dir))

        cfg.append("suffix " + quote(self.get_dn_suffix()))
        cfg.append("rootdn " + quote(self.get_root_dn()))
        cfg.append("rootpw " + quote(self.get_root_password()))

    def _write_config(self):
        """Writes the slapd.conf file out, and returns the path to it."""
        path = os.path.join(self._tmpdir, "slapd.conf")
        ldif_dir = mkdirs(self._tmpdir)
        if os.access(path, os.F_OK):
            self._log.debug("deleting existing %s", path)
            os.remove(path)
        self._log.debug("writing config to %s", path)
        file(path, "w").writelines([line + "\n" for line in self._config])
        return path

    def start(self):
        """
        Starts the slapd server process running, and waits for it to come up. 
        """
        if self._proc is None:
            ok = False
            config_path = None
            try:
                self.configure(self._config)
                self._test_configuration()
                self._start_slapd()
                self._wait_for_slapd()
                ok = True
                self._log.debug("slapd ready at %s", self.get_url())
                self.started()
            finally:
                if not ok:
                    if config_path:
                        try: os.remove(config_path)
                        except os.error: pass
                    if self._proc:
                        self.stop()

    def _start_slapd(self):
        # Spawns/forks the slapd process
        config_path = self._write_config()
        self._log.info("starting slapd")
        self._proc = subprocess.Popen([self.PATH_SLAPD, 
                "-f", config_path, 
                "-h", self.get_url(), 
                "-d", str(self._slapd_debug_level),
                ])
        self._proc_config = config_path

    def _wait_for_slapd(self):
        # Waits until the LDAP server socket is open, or slapd crashed
        s = socket.socket()
        while 1:
            if self._proc.poll() is not None:
                self._stopped()
                raise RuntimeError("slapd exited before opening port")
            try:
               self._log.debug("Connecting to %s", repr(self.get_address()))
               s.connect(self.get_address())
               s.close()
               return
            except socket.error:
               time.sleep(1)

    def stop(self):
        """Stops the slapd server, and waits for it to terminate"""
        if self._proc is not None:
            self._log.debug("stopping slapd")
            if hasattr(self._proc, 'terminate'):
                self._proc.terminate()
            else:
                import posix, signal
                posix.kill(self._proc.pid, signal.SIGHUP)
                #time.sleep(1)
                #posix.kill(self._proc.pid, signal.SIGTERM)
                #posix.kill(self._proc.pid, signal.SIGKILL)
            self.wait()

    def restart(self):
        """
        Restarts the slapd server; ERASING previous content.
        Starts the server even it if isn't already running.
        """
        self.stop()
        self.start()

    def wait(self):
        """Waits for the slapd process to terminate by itself."""
        if self._proc:
            self._proc.wait()
            self._stopped()

    def _stopped(self):
        """Called when the slapd server is known to have terminated"""
        if self._proc is not None:
            self._log.info("slapd terminated")
            self._proc = None
            try: 
                os.remove(self._proc_config)
            except os.error: 
                self._log.debug("could not remove %s", self._proc_config)

    def _test_configuration(self):
        config_path = self._write_config()
        try:
            self._log.debug("testing configuration")
            verboseflag = "-Q"
            if self._log.isEnabledFor(logging.DEBUG):
                verboseflag = "-v"
            p = subprocess.Popen([
                self.PATH_SLAPTEST, 
                verboseflag, 
                "-f", config_path
            ])
            if p.wait() != 0:
                raise RuntimeError("configuration test failed")
            self._log.debug("configuration seems ok")
        finally:
            os.remove(config_path)

    def ldapadd(self, ldif, extra_args=[]):
        """Runs ldapadd on this slapd instance, passing it the ldif content"""
        self._log.debug("adding %s", repr(ldif))
        p = subprocess.Popen([self.PATH_LDAPADD, 
                "-x",
                "-D", self.get_root_dn(),
                "-w", self.get_root_password(),
                "-H", self.get_url()] + extra_args,
                stdin = subprocess.PIPE, stdout=subprocess.PIPE)
        p.communicate(ldif)
        if p.wait() != 0:
            raise RuntimeError("ldapadd process failed")

    def ldapsearch(self, base=None, filter='(objectClass=*)', attrs=[],
        scope='sub', extra_args=[]):
        if base is None: base = self.get_dn_suffix()
        self._log.debug("ldapsearch filter=%s", repr(filter))
        p = subprocess.Popen([self.PATH_LDAPSEARCH, 
                "-x",
                "-D", self.get_root_dn(),
                "-w", self.get_root_password(),
                "-H", self.get_url(),
                "-b", base,
                "-s", scope,
                "-LL",
                ] + extra_args + [ filter ] + attrs,
                stdout = subprocess.PIPE)
        output = p.communicate()[0]
        if p.wait() != 0:
            raise RuntimeError("ldapadd process failed")

        # RFC 2849: LDIF format
        # unfold
        lines = []
        for l in output.split('\n'):
            if l.startswith(' '):
                lines[-1] = lines[-1] + l[1:]
            elif l == '' and lines and lines[-1] == '':
                pass # ignore multiple blank lines
            else:
                lines.append(l)
        # Remove comments
        lines = [l for l in lines if not l.startswith("#")]

        # Remove leading version and blank line(s)
        if lines and lines[0] == '': del lines[0]
        if not lines or lines[0] != 'version: 1':
            raise RuntimeError("expected 'version: 1', got " + repr(lines[:1]))
        del lines[0]
        if lines and lines[0] == '': del lines[0]

        # ensure the ldif ends with a blank line (unless it is just blank)
        if lines and lines[-1] != '': lines.append('')

        objects = []
        obj = []
        for line in lines:
            if line == '': # end of an object
                if obj[0][0] != 'dn':
                    raise RuntimeError("first line not dn", repr(obj))
                objects.append((obj[0][1], obj[1:]))
                obj = []
            else:
                attr,value = line.split(':',2)
                if value.startswith(': '):
                    value = base64.decodestring(value[2:])
                elif value.startswith(' '):
                    value = value[1:]
                else:
                    raise RuntimeError("bad line: " + repr(line))
                obj.append((attr,value))
        assert obj == []
        return objects

    def started(self):
        """
        This method is called when the LDAP server has started up and is empty.
        By default, this method adds the two initial objects,
        the domain object and the root user object.
        """
        assert self.get_dn_suffix().startswith("dc=")
        suffix_dc = self.get_dn_suffix().split(',')[0][3:]
        assert self.get_root_dn().startswith("cn=")
        assert self.get_root_dn().endswith("," + self.get_dn_suffix())
        root_cn = self.get_root_dn().split(',')[0][3:]

        self._log.debug("adding %s and %s",
                self.get_dn_suffix(),
                self.get_root_dn())

        self.ldapadd("\n".join([
            'dn: ' + self.get_dn_suffix(),
            'objectClass: dcObject',
            'objectClass: organization',
            'dc: ' + suffix_dc,
            'o: ' + suffix_dc,
            '',
            'dn: ' + self.get_root_dn(),
            'objectClass: organizationalRole',
            'cn: ' + root_cn,
            ''
        ]))

Slapd.check_paths()

if __name__ == '__main__' and sys.argv == ['run']:
    logging.basicConfig(level=logging.DEBUG)
    slapd = Slapd()
    print("Starting slapd...")
    slapd.start()
    print("Contents of LDAP server follow:\n")
    for dn,attrs in slapd.ldapsearch():
        print("dn: " + dn)
        for name,val in attrs:
            print(name + ": " + val)
        print("")
    print(slapd.get_url())
    slapd.wait()

