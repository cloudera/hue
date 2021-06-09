---
title: Missing some color? How to improve or add your own SQL syntax Highlighter
author: Hue Team
type: post
date: 2019-10-31T10:42:47+00:00
url: /how-to-improve-or-add-your-own-sql-syntax-highlighter/
sf_thumbnail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
sf_detail_type:
  - none
sf_page_title:
  - 1
sf_page_title_style:
  - standard
sf_no_breadcrumbs:
  - 1
sf_page_title_bg:
  - none
sf_page_title_text_style:
  - light
sf_background_image_size:
  - cover
sf_social_sharing:
  - 1
sf_related_articles:
  - 1
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
ampforwp-amp-on-off:
  - default
categories:
  - Version 4
# - Version 4.6

---
Hue&#8217;s Editor [SQL functionalities][1] makes it much more easier to query your databases and datawarehouses. It was previously described about how to [improve or create your own SQL autocompleter][2] so that the Querying Experience gets even more effective. This post is about going one step further and improving the SQL syntax highlighting.

New keywords might not be properly colored highlighted in the editor. This is especially true when adding a new language. Here is how to fix that.

<a href="https://cdn.gethue.com/docs/dev/syntax_highlighting_missing.png" data-featherlight="image"><img class="aligncenter" src="https://cdn.gethue.com/docs/dev/syntax_highlighting_missing.png" alt="Missing highlighting" /></a>

<p style="text-align: center;">
  Missing highlighting for ‘REINDEX’ keyword
</p>

<a href="https://cdn.gethue.com/docs/dev/syntax_highlighting_updated.png" data-featherlight="image"><img class="aligncenter" src="https://cdn.gethue.com/docs/dev/syntax_highlighting_updated.png" alt="With highlighting" /></a>

<p style="text-align: center;">
  With correct highlighting
</p>

### Updating keywords {#updating-keywords}

The Editor is currently visually powered by [Ace][3]. The list of supported languages is found in the [mode][4] directory.

For each dialect, we have two files. e.g. with PostgreSQL:

<pre><code class="bash">pgsql.js
pgsql_highlight_rules.js
</code></pre>

The list of keywords is present in `*_highlight_rules.js` and can be updated there.

<pre><code class="javascript">var keywords = (
    "ALL|ALTER|REINDEX|..."
)
</code></pre>

Afterwards, run:

<pre><code class="bash">make ace
</code></pre>

And after refreshing the editor page, the updated mode will be activated.

### Adding new dialect {#adding-new-dialect}

To add a new dialect, it is recommended to copy the two files of the closest mode and rename all the names inside. For example, if we were creating a new `ksql` mode, `pgsql_highlight_rules.js` would become `ksql_highlight_rules.js` and we would rename all the references inside to `psql` to `ksql`. Same with `pgsql.js` to `ksql.js`. In particular, the name of the mode to be referenced later is in:

<pre><code class="javascript">KsqlHighlightRules.metaData = {
  fileTypes: ["ksql"],
  name: "ksql",
  scopeName: "source.ksql"
};
</code></pre>

Tip: inheritance of modes is supported by Ace, which make it handy for avoiding potential duplications.

In the Editor, the mapping between Ace’s modes and the type of snippets is happening in [editor_components.mako][5].

In the KSQL case we have:

<pre><code class="javascript">ksql: {
  placeHolder: '${ _("Example: SELECT * FROM stream, or press CTRL + space") }',
  aceMode: 'ace/mode/ksql',
  snippetIcon: 'fa-database',
  sqlDialect: true
},
</code></pre>

And cf. above [prerequisites][6], any interpreter snippet with `ksql` will pick-up the new highlighter:

<pre><code class="bash">[[[ksql]]]
    name = KSQL Analytics
    interface=ksql
</code></pre>

Note: after [HUE-8758][7] we will be able to have multiple interpreters on the same dialect (e.g. pointing to two different databases of the same type).

&nbsp;

Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> or <a href="https://twitter.com/gethue">@gethue</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!

Romain from the Hue Team

 [1]: https://docs.gethue.com/user/querying/
 [2]: https://docs.gethue.com/developer/development/#sql-parsers
 [3]: https://ace.c9.io/
 [4]: https://github.com/cloudera/hue/tree/master/tools/ace-editor/lib/ace/mode
 [5]: https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/templates/editor_components.mako#L2118
 [6]: http://localhost:1313/developer/development/#sql-parsers#prerequisites
 [7]: https://issues.cloudera.org/browse/HUE-8758
