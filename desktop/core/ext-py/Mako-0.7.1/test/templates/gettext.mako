<%page args="x, y=_('Page arg 1'), z=_('Page arg 2')"/>
<%!
import random
def gettext(message): return message
_ = gettext
def ungettext(s, p, c):
    if c == 1:
        return s
    return p
top = gettext('Begin')
%>
<%
   # TRANSLATOR: Hi there!
   hithere = _('Hi there!')

   # TRANSLATOR: you should not be seeing this in the .po
   rows = [[v for v in range(0,10)] for row in range(0,10)]

   hello = _('Hello')
%>
<div id="header">
  ${_('Welcome')}
</div>
<table>
    % for row in (hithere, hello, _('Yo')):
        ${makerow(row)}
    % endfor
    ${makerow(count=2)}
</table>


<div id="main">

## TRANSLATOR: Ensure so and
## so, thanks
  ${_('The')} fuzzy ${ungettext('bunny', 'bunnies', random.randint(1, 2))}
</div>

<div id="footer">
  ## TRANSLATOR: Good bye
  ${_('Goodbye')}
</div>
 
<%def name="makerow(row=_('Babel'), count=1)">
    <!-- ${ungettext('hella', 'hellas', count)} -->
    % for i in range(count):
      <tr>
      % for name in row:
          <td>${name}</td>\
      % endfor
      </tr>
    % endfor
</%def>

<%def name="comment()">
  <!-- ${caller.body()} -->
</%def>

<%block name="foo">
    ## TRANSLATOR: Ensure so and
    ## so, thanks
      ${_('The')} fuzzy ${ungettext('bunny', 'bunnies', random.randint(1, 2))}
</%block>

<%call expr="comment">
  P.S.
  ## TRANSLATOR: HTML comment
  ${_('Goodbye, really!')}
</%call>

<!-- ${_('P.S. byebye')} -->

<div id="end">
  <a href="#top">
    ## TRANSLATOR: you won't see this either
 
    ${_('Top')}
  </a>
</div>

<%def name="panel()">

${_(u'foo')} <%self:block_tpl title="123", name="_(u'baz')">

${_(u'bar')}

</%self:block_tpl>

</%def>
