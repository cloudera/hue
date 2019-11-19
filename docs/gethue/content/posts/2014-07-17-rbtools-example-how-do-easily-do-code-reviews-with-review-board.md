---
title: 'RBTools example: How do easily do code reviews with Review Board and post-review'
author: admin
type: post
date: 2014-07-17T18:57:27+00:00
url: /rbtools-example-how-do-easily-do-code-reviews-with-review-board/
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
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
sf_remove_promo_bar:
  - 1
slide_template:
  - default
categories:
  - Development

---
**Note:** This script has been merged into Hue as 'tools/script/hue-review'.

Here is a tutorial about how to use the code review tool <a href="https://www.reviewboard.org/" target="_blank" rel="noopener noreferrer">Review Board</a> for a better productivity!

# Setup

First, join the 'hue' group in your account <a href="https://review.cloudera.org/account/preferences/" target="_blank" rel="noopener noreferrer">https://review.cloudera.org/account/preferences/</a>!

Then install the Review Board tools:

{{< highlight bash >}}sudo pip install -allow-all-external RBTools{{< /highlight >}}

Point it to your git repository:

{{< highlight bash >}}romain@runreal:~/projects/hue$ rbt setup-repo

Enter the Review Board server URL: https://review.cloudera.org

Use the Git repository 'hue' (git://github.com/cloudera/hue.git)? [Yes/No]: yes

Create '/home/romain/projects/hue/.reviewboardrc' with the following?

REVIEWBOARD_URL = "https://review.cloudera.org"

REPOSITORY = "hue"

BRANCH = "master"

[Yes/No]: yes

Config written to /home/romain/projects/hue/.reviewboardrc

{{< /highlight >}}

# Post a review

We have wrapped up the typical submission in a dedicated 'tools/scripts/hue-review' script prefilled with all the details of the commits:

{{< highlight bash >}}vim tools/scripts/hue-review{{< /highlight >}}

{{< highlight bash >}}function hue-review {

#!/usr/bin/env bash

if [ $# -lt 3 ]; then

echo "Usage: hue-review rev-list reviewer(s) summary ..." 1>&2

exit 1

fi

RBT=\`which rbt\`

if [ "$?" -ne "0" ]; then

echo "Please install rbt from https://www.reviewboard.org/" 1&>2

exit 1

fi

REVLIST=$1;

REVRANGE=${REVLIST//\.\./:};

REVIEWER=$2;

SUMMARY=$3;

shift 3;

exec $RBT post -o -description="$(git whatchanged $REVLIST)" -target-groups=hue -target-people="$REVIEWER" -summary="$SUMMARY" $REVLIST $@

}

{{< /highlight >}}

If you use a Mac:

{{< highlight bash >}}

#!/usr/bin/env bash

if [ $# -lt 3 ]; then

echo "Usage: hue-review rev-list reviewer(s) summary ..." 1>&2

exit 1

fi

RBT=\`which rbt\`

if [ "$?" -ne "0" ]; then

echo "Please install rbt from https://www.reviewboard.org/" 1>&2

exit 1

fi

REVLIST=$1;

REVRANGE=${REVLIST//\.\./:};

REVIEWER=$2;

SUMMARY=$3;

shift 3;

exec $RBT post \

-o \

-description="$(git whatchanged $REVLIST)" \

-target-groups=hue \

-target-people="$REVIEWER" \

-summary="$SUMMARY" \

$@ \

$REVLIST

{{< /highlight >}}

Then:

{{< highlight bash >}}source /home/romain/.bashrc{{< /highlight >}}

or put it in your PATH.

Now we post the review:

{{< highlight bash >}}tools/scripts/hue-review HEAD~1..HEAD romain,enricoberti,erickt "HUE-2123 [beeswax] Handle cancel state properly" -bugs-closed=HUE-2123

Review request #4501 posted.

https://review.cloudera.org/r/4501/

{{< /highlight >}}

Et voila! Here is our review <a href="https://review.cloudera.org/r/4501/" target="_blank" rel="noopener noreferrer">https://review.cloudera.org/r/4501/</a>.

**Note**:

If you have more than one diff, update `HEAD~1..HEAD` accordingly (e.g. `HEAD~2..HEAD`)

# Update a review

Modify the previous commit diff:

{{< highlight bash >}}git commit -a -amend

... Update a file ...

[master 9c7c7af] HUE-2123 [beeswax] Handle cancel state properly

3 files changed, 10 insertions(+), 4 deletions(-)

{{< /highlight >}}

Update the review:

{{< highlight bash >}}rbt post -u -r 6092 HEAD~1..HEAD

Review request #6092 posted. {{< /highlight >}}

# Sump-up

We hope that Review Board and these commands will make your life easier and encourage you to <a href="https://github.com/cloudera/hue/wiki/Contribute-to-HUE" target="_blank" rel="noopener noreferrer">contribute to Hue</a> 😉

As usual feel free to send feedback on the [hue-user][1] list or [@gethue][2]!

 [1]: http://groups.google.com/a/cloudera.org/group/hue-user
 [2]: https://twitter.com/gethue
