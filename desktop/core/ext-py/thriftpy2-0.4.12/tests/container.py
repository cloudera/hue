# -*- coding: utf-8 -*-

"""This file is a demo for what the dynamiclly generated code would be like.
"""

from thriftpy2.thrift import (
    TPayload,
    TType,
)


class MixItem(TPayload):
    thrift_spec = {
        1: (TType.LIST, "list_map",
            (TType.MAP, (TType.STRING, TType.STRING))),
        2: (TType.MAP, "map_list",
            (TType.STRING, (TType.LIST, TType.STRING)))
    }
    default_spec = [("list_map", None), ("map_list", None)]
