![alt text](https://raw.githubusercontent.com/cloudera/hue/master/docs/images/hue_logo.png "Hue Logo")


The Hue project gladly welcomes any patches or [pull requests](https://github.com/cloudera/hue/pulls)!

This document contains instructions on how to get involved with Hue, and our development process. The team also follows this [logic](http://gethue.com/the-hue-team-development-process/).

In any case, feel free to ask on [hue-user](http://groups.google.com/a/cloudera.org/group/hue-user), here or [@gethue](https://twitter.com/gethue).

# Getting Started

Have a look at [how to build Hue](https://github.com/cloudera/hue#getting-started).

## Example of bug, patch and review

* [List of pull requests](https://github.com/cloudera/hue/pulls)
* [HUE-2617 [metastore] Return partition results in reverse order by default](https://issues.cloudera.org/browse/HUE-2617)

List of [Easy bugs](https://issues.cloudera.org/secure/IssueNavigator.jspa?mode=hide&requestId=10431).

## Bug Tracking

Hue uses [JIRA](https://issues.cloudera.org/browse/HUE) as its bug tracking system.

## Submitting an improvement

### Reviews

Hue blog posts about using Review Board: [How to do Code Reviews](http://gethue.com/rbtools-example-how-do-easily-do-code-reviews-with-review-board/).

Currently, the Hue project is very flexible on how to do code reviews:

* Review Board
Create an account on Hus's [Review Board](https://review.cloudera.org/groups/hue).
Post the patch against the "hue-rw" repository. Enter "hue" in the "groups" field.
Example: [https://review.cloudera.org/r/4019/](https://review.cloudera.org/r/4019/)

* Github Diff or Pull request
Again, for small changes, if you have the fix in a commit in your own github fork, you can just post the [pull request](https://github.com/cloudera/hue/pulls)

* JIRA Attachment
For small changes, you can attach the patch in the JIRA.

### Commit

A Hue committer will commit your patch when it is is ready after being reviewed.

Example of [commit](https://github.com/cloudera/hue/commit/968d58c72119e4055bb081ba023e02b8ac8534dd).


## Coding Style

A general rule is to follow the on-going style of the code context.

* Python: Follow [PEP 8](http://www.python.org/dev/peps/pep-0008/), with the exception of using 2 spaces per indent level. Line width is 100 characters.
* JavaScript: Follow the style in this [file](https://github.com/cloudera/hue/blob/master/apps/oozie/src/oozie/static/oozie/js/bundle-editor.ko.js#L18).


### Tests

Please run the tests. Se the [Getting started](https://github.com/cloudera/hue#getting-started) then [testing](http://cloudera.github.io/hue/latest/sdk/sdk.html#testing).

### Patch Format

Generate the patch using @git format-patch@ with a message looking like:

<pre>
HUE-NNNN [APP_NAME] The JIRA summary line

Optional details on the commit *after* a blank line.
This section can span multiple lines.

Or have multiple paragraphs.
</pre>

Example of [format](https://github.com/cloudera/hue/commit/ab09a825f71ae9817f07befc520a4d0bd85f88f0).
