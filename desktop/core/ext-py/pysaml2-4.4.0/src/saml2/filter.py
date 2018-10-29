__author__ = 'roland'

class Filter(object):
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        pass


class AllowDescriptor(Filter):
    def __init__(self, allow):
        """

        :param allow: List of allowed descriptors
        :return:
        """
        super(AllowDescriptor, self).__init__()
        self.allow = allow

    def __call__(self, entity_descriptor):
        # get descriptors
        _all = []
        for desc in list(entity_descriptor.keys()):
            if desc.endswith("_descriptor"):
                typ, _ = desc.rsplit("_", 1)
                if typ in self.allow:
                    _all.append(typ)
                else:
                    del entity_descriptor[desc]

        if not _all:
            return None
        else:
            return  entity_descriptor
