# Copyright (C) 2011-2012 Yaco Sistemas (http://www.yaco.es)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django import template

from djangosaml2.conf import config_settings_loader
from djangosaml2.utils import available_idps

register = template.Library()


class IdPListNode(template.Node):
    def __init__(self, variable_name):
        self.variable_name = variable_name

    def render(self, context):
        conf = config_settings_loader()
        context[self.variable_name] = available_idps(conf)
        return ""


@register.tag
def idplist(parser, token):
    try:
        tag_name, as_part, variable = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires two arguments" % token.contents.split()[0]
        )
    if not as_part == "as":
        raise template.TemplateSyntaxError(
            '%r tag first argument must be the literal "as"' % tag_name
        )

    return IdPListNode(variable)
