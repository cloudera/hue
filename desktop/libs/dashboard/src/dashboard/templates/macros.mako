## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
<%!
import re
import urllib

from itertools import izip

from django.utils.translation import ugettext as _


# <http://github.com/mzsanford/twitter-text-java>

AT_SIGNS = ur'[@\uff20]'
UTF_CHARS = ur'a-z0-9_\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u00ff'
SPACES = ur'[\u0020\u00A0\u1680\u180E\u2002-\u202F\u205F\u2060\u3000]'

LIST_PRE_CHARS = ur'([^a-z0-9_]|^)'
LIST_END_CHARS = ur'([a-z0-9_]{1,20})(/[a-z][a-z0-9\x80-\xFF-]{0,79})?'
LIST_REGEX = re.compile(LIST_PRE_CHARS + '(' + AT_SIGNS + '+)' + LIST_END_CHARS, re.IGNORECASE)

USERNAME_REGEX = re.compile(ur'\B' + AT_SIGNS + LIST_END_CHARS, re.IGNORECASE)
REPLY_REGEX = re.compile(ur'^(?:' + SPACES + ur')*' + AT_SIGNS + ur'([a-z0-9_]{1,20}).*', re.IGNORECASE)

HASHTAG_EXP = ur'(^|[^0-9A-Z&/]+)(#|\uff03)([0-9A-Z_]*[A-Z_]+[%s]*)' % UTF_CHARS
HASHTAG_REGEX = re.compile(HASHTAG_EXP, re.IGNORECASE)

PRE_CHARS = ur'(?:[^/"\':!=]|^|\:)'
DOMAIN_CHARS = ur'([\.-]|[^\s_\!\.\/])+\.[a-z]{2,}(?::[0-9]+)?'
PATH_CHARS = ur'(?:[\.,]?[%s!\*\'\(\);:=\+\$/%s#\[\]\-_,~@])' % (UTF_CHARS, '%')
QUERY_CHARS = ur'[a-z0-9!\*\'\(\);:&=\+\$/%#\[\]\-_\.,~]'

PATH_ENDING_CHARS = r'[%s\)=#/]' % UTF_CHARS
QUERY_ENDING_CHARS = '[a-z0-9_&=#]'

URL_REGEX = re.compile('((%s)((https?://|www\\.)(%s)(\/%s*%s?)?(\?%s*%s)?))'
                     % (PRE_CHARS, DOMAIN_CHARS, PATH_CHARS,
                        PATH_ENDING_CHARS, QUERY_CHARS, QUERY_ENDING_CHARS), re.IGNORECASE)

IANA_ONE_LETTER_DOMAINS = ('x.com', 'x.org', 'z.com', 'q.net', 'q.com', 'i.net')


MAX_URL_LENGTH = 30

def parse_urls(match):
      mat = match.group(0)

      # Fix a bug in the regex concerning www...com and www.-foo.com domains
      domain = match.group(5)
      if domain[0] in '.-':
          return mat

      # Only allow IANA one letter domains that are actually registered
      if len(domain) == 5 \
         and domain[-4:].lower() in ('.com', '.org', '.net') \
         and not domain.lower() in IANA_ONE_LETTER_DOMAINS:

          return mat

      # Check for urls without http(s)
      pos = mat.find('http')
      if pos != -1:
          pre, url = mat[:pos], mat[pos:]
          full_url = url

      # Find the www and force http://
      else:
          pos = mat.lower().find('www')
          pre, url = mat[:pos], mat[pos:]
          full_url = 'http://%s' % url

      return '%s%s' % (pre, format_url(full_url, shorten_url(escape(url))))

def parse_users(match):
      # Don't parse lists here
      if match.group(2) is not None:
          return match.group(0)

      mat = match.group(0)

      return format_username(mat[0:1], mat[1:])

def parse_lists(match):
      # Don't parse usernames here
      if match.group(4) is None:
          return match.group(0)

      pre, at_char, user, list_name = match.groups()
      list_name = list_name[1:]

      return '%s%s' % (pre, format_list(at_char, user, list_name))

def parse_tags(match):
      mat = match.group(0)

      # Fix problems with the regex capturing stuff infront of the #
      tag = None
      for i in u'#\uff03':
          pos = mat.rfind(i)
          if pos != -1:
              tag = i
              break

      pre, text = mat[:pos], mat[pos + 1:]

      return '%s%s' % (pre, format_tag(tag, text))

def shorten_url(text):
    if len(text) > MAX_URL_LENGTH and MAX_URL_LENGTH != -1:
      text = text[0:MAX_URL_LENGTH - 3]
      amp = text.rfind('&')
      close = text.rfind(';')
      if amp != -1 and (close == -1 or close < amp):
        text = text[0:amp]
      return text + '...'
    else:
      return text

def format_tag(tag, text):
    return '<a href="http://search.twitter.com/search?q=%s" target="_blank">%s%s</a>' \
              % (urllib.quote('#' + text.encode('utf-8')), tag, text)

def format_username(at_char, user):
    return '<a href="http://twitter.com/%s" target="_blank">%s%s</a>' \
             % (user, at_char, user)

def format_list(at_char, user, list_name):
    return '<a href="http://twitter.com/%s/%s" target="_blank">%s%s/%s</a>' \
             % (user, list_name, at_char, user, list_name)

def format_url(url, text):
    return '<a href="%s" target="_blank">%s</a>' % (escape(url), text)

def highlight(word, text):
    search = re.compile(r'\b(%s)\b' % word, re.I)
    return search.sub('<strong>\\1</strong>', text)

def escape(text)  :
  return ''.join({'&': '&amp;', '"': '&quot;',
                  '\'': '&apos;', '>': '&gt;',
                  '<': '&lt;'}.get(c, c) for c in text)
%>


<%def name="pairwise(iterable)">
  ##"s -> (s0,s1), (s2,s3), (s4, s5), ..."
  <%
    a = iter(iterable)
    return izip(a, a)
  %>
</%def>

<%def name="parseLinks(text)">
  <%
    html = URL_REGEX.sub(parse_urls, text)
    html = USERNAME_REGEX.sub(parse_users, html)
    html = LIST_REGEX.sub(parse_lists, html)
    html = HASHTAG_REGEX.sub(parse_tags, html)
    if solr_query['q']:
      html = highlight(solr_query['q'], html)
    return html
  %>
</%def>


<%def name="tweet_result(result)">
<tr>
  <td style="word-wrap: break-word;">
    <div class="content">
      <div class="stream-item-header">
        <small class="time">
          <a href="https://twitter.com/${ result.get('user_screen_name', '') }/status/${ result.get('id', '') }" target="_blank" data-dt="${ result.get('created_at', '') }" rel="tooltip" data-placement="left" title="${ result.get('created_at', '') }"></a>
        </small>
        <a target="_blank" href="https://twitter.com/${ result.get('user_screen_name', '') }" class="account-group">
          <img src="http://twitter.com/api/users/profile_image/${ result.get('user_screen_name', '') }" class="avatar"
              data-placement="left" rel="popover"  data-content="Location: ${ result.get('user_location', '') }
          <br/>User tweets #: ${ result.get('user_statuses_count', '') }
           <br/>User followers #: ${ result.get('user_followers_count', '') }" title="@${ result.get('user_screen_name', '') }" data-trigger="hover">
          <strong class="fullname">${ result.get('user_name', '') }</strong>
         <span>&rlm;</span><span class="username">@${ result.get('user_screen_name', '') }</span>
        </a>
      </div>
      <div class="text" data-link="https://twitter.com/${ result.get('user_screen_name', '') }/status/${ result.get('id', '') }">
        ${ parseLinks(result.get('text', ''))  | n,unicode }
        %if result.get('retweet_count', ''):
          <div class="retweeted">
            ${_('Retweeted %s times') % result.get('retweet_count', '') }
          </div>
        %endif
      </div>

      <div class="stream-item-footer">
        <ul class="tweet-actions">
          <li class="action">
            <a href="https://twitter.com/intent/tweet?in_reply_to=${ result.get('id', '') }" target="_blank">
              <i class="icon fa fa-reply"></i>
              <b>${_('Reply')}</b>
            </a>
          </li>
          <li class="action">
            <a href="https://twitter.com/intent/retweet?tweet_id=${ result.get('id', '') }" target="_blank">
              <i class="icon fa fa-retweet"></i>
              <b>${_('Retweet')}</b>
            </a>
          </li>
        </ul>
      </div>
    </div>
   </div>
  </td>
</tr>
</%def>
