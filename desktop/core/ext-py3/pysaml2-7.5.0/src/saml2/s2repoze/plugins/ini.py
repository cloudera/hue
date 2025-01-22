import ConfigParser

# from repoze.who.interfaces import IChallenger, IIdentifier, IAuthenticator
from repoze.who.interfaces import IMetadataProvider
from zope.interface import implements


class INIMetadataProvider:

    implements(IMetadataProvider)

    def __init__(self, ini_file, key_attribute):

        self.users = ConfigParser.ConfigParser()
        self.users.readfp(open(ini_file))
        self.key_attribute = key_attribute

    def add_metadata(self, _environ, identity):
        # logger = environ.get('repoze.who.logger','')

        key = identity.get("repoze.who.userid")
        try:
            if self.key_attribute:
                for sec in self.users.sections():
                    if self.users.has_option(sec, self.key_attribute):
                        if key in self.users.get(sec, self.key_attribute):
                            identity["user"] = dict(self.users.items(sec))
                            break
            else:
                identity["user"] = dict(self.users.items(key))
        except ValueError:
            pass


def make_plugin(ini_file, key_attribute=""):
    return INIMetadataProvider(ini_file, key_attribute)
