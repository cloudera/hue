# django-auth-ldap

This is a Django authentication backend that authenticates against an LDAP
service. Configuration can be as simple as a single distinguished name template,
but there are many rich configuration options for working with users, groups,
and permissions.

This version is supported on Python 2.7 and 3.4+; and Django 1.8 and 1.10+.
Under Python 2, it requires [python-ldap][] >= 2.0; under Python 3, it uses
[pyldap][].

* Repository: https://bitbucket.org/illocution/django-auth-ldap
* Documentation: https://django-auth-ldap.readthedocs.io/
* Mailing list: https://groups.google.com/group/django-auth-ldap


## History and Status

As with so many efforts of this type, this is a minor side project that I spun
out of a private Django deployment. The BSD license, in many ways a formality,
is also a pretty accurate description of the project's motivation and status:
"Here's a thing I did. I found it useful, maybe you will too. Do whatever you
like with it."

Although this library has long done everything I need it to, I continue to
maintain it as a small contribution to the Django community. Important bugs I
try to process fairly quickly. Less urgent issues may queue up until I can break
away from other work.


## Contributing

If you'd like to report an issue or contribute a feature, but you're not sure
how to proceed, start with the [mailing list][]. This may clear up some
misunderstandings or provide a gut check on how feasible the idea is.

If you have something concrete you'd like to contribute, the best approach is to
send a well-formed pull request, complete with tests and documentation, as
needed. Pull requests that lack tests or documentation or that break existing
tests will probably not be taken very seriously. Pull requests should also be
focused: trying to do more than one thing in a single request will make it more
difficult to process.

If you have a bug or feature request that you can't or don't wish to fix or
implement, you can try [logging an issue][issues]. Serious bugs should get taken
care of quickly, but less urgent issues may or may not attract any attention. It
just depends on whether anyone else finds it interesting enough to do something
about.

There's no harm in creating an issue and then submitting a pull request to
resolve it. This can be a good way to start a conversation and can serve as an
anchor point if the initial pull request turns out not to be the best approach.

Here are a few dos and don'ts to help us all save some time.

* **Don't** move fast and break stuff.

* **Do** propose incremental fixes or improvements that solve well-defined
  problems with minimal collatoral effects.

* **Do** feel free to do a bit of syntactic cleanup, especially when it comes to
  leaving behind obsolete Python or Django versions. This project goes back at
  least to Python 2.3 and Django 1.0; youngins may find some lingering
  anachronisms disorienting.

* **Don't** do a bunch of semantic cleanup without a clear and compelling
  reason. The phrase "I don't see how this could break anything" is a confession
  of the ignorance and uncertainty under which we all labor, not a proof of
  correctness.

* **Do** reach out if you'd like a feature or change and you're not sure how to
  proceed.


## Development

To get set up for development, activate your virtualenv and use pip to install
from requirements-dev.txt:

    % pip install -r requirements-dev.txt

To run the tests:

    % django-admin test --settings tests.settings

To run the full test suite in a range of environments, run [tox][] from the root
of the project:

    % tox

This includes some static analysis to detect potential runtime errors and style
issues.


## Mercurial

django-auth-ldap uses [Mercurial][hg] for source control. If you're more
familiar with Git, Mercurial is similar in many ways, but there are a few
important differences to keep in mind.

Mercurial branches are more or less permanent and thus not very good for feature
work or pull requests. If you want to work on multiple features at once, use
[bookmarks][hg-bookmark] or [topics][hg-topic] instead (Bitbucket may not
recognize topics yet). The default bookmark is called ``@`` (similar to git's
master branch).

    % hg up @
    % hg bookmark new-feature
    (make changes)
    % hg ci
    % hg push -B new-feature

Local Mercurial clones and Bitbucket forks are all (typically)
[non-publishing][hg-non-publishing] repositories. This means that new
changesets remain in draft mode and can be modified in a safe and principled
manner with the [evolve][hg-evolve-ext] extension. I make heavy use of
[changeset evolution][hg-evolution] and frequently rely it to process pull
requests while keeping the history clean and linear.

If you're setting up Mercurial for the first time, I recommend you make sure you
have the latest version and install [hg-evolve][pypi-evolve] with it. Here's a
sample ~/.hgrc to get started:

    [ui]
    username = Your Name <youremail@example.com>
    ignore = ~/.hgignore
    style = phases

    [extensions]
    color =
    evolve =
    histedit =
    rebase =
    shelve =
    topic =

    [alias]
    glog = log --graph

You should also go to the Labs section of your bitbucket.org account settings
and turn on evolution support.

Changeset evolution is a big topic, but one of the most useful things to know is
that it's safe to amend existing draft changesets even if they've already been
shared with other non-publishing repositories:

    % hg up @
    % hg bookmark new-feature
    (make changes)
    % hg ci
    % hg push -B new-feature
    (incorporate feedback)
    % hg amend
    % hg push


[python-ldap]: https://pypi.python.org/pypi/python-ldap
[pyldap]: https://pypi.python.org/pypi/pyldap
[mailing list]: https://groups.google.com/group/django-auth-ldap 
[issues]: https://bitbucket.org/illocution/django-auth-ldap/issues?status=new&status=open
[tox]: https://tox.readthedocs.io/
[hg]: https://www.mercurial-scm.org/
[hg-bookmark]: https://www.mercurial-scm.org/wiki/Bookmarks
[hg-topic]: https://www.mercurial-scm.org/doc/evolution/tutorials/topic-tutorial.html
[hg-non-publishing]: https://www.mercurial-scm.org/wiki/Phases#Publishing_Repository
[hg-evolve-ext]: https://www.mercurial-scm.org/wiki/EvolveExtension
[hg-evolution]: https://www.mercurial-scm.org/doc/evolution/
[pypi-evolve]: https://pypi.python.org/pypi/hg-evolve
