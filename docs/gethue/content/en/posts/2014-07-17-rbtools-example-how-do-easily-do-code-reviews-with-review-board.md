---
title: 'Hue Development Process - How to do code changes and reviews with Review Board and Git'
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

**December 2020**: GitHub pull requests are now prefered https://docs.gethue.com/developer/development/#development-process

**Note:**

During the development process if you are facing any problem then, it is recommended to check your issues at https://discourse.gethue.com/ and https://github.com/cloudera/hue/issues?q=is%3Aissue+. If the solution is not found then, feel free to create an issue at https://github.com/cloudera/hue/issues.

Here is a tutorial about how to use the code review tool [Review Board](https://www.reviewboard.org/) for a better productivity!

# Setup

Hue project uses Review Board and Pull Requests for code reviews. For more complex patches it's advisable to use RB than a plain pull request on github. The advantage of Pull Request is that the CI (syntax check, tests…) automatically runs for you. Along with the web app, a command line tool named RBTool is used to make things easier.

Create accounts in https://review.cloudera.org, https://issues.cloudera.org/browse/HUE and https://github.com and share the usernames

Then, join the 'hue' group in your account https://review.cloudera.org/account/preferences/#groups

Then [download](https://www.reviewboard.org/downloads/rbtools/) the Review Board tools and install it.

If you've never used git and github before, there are bunch of things you need to [do](https://kbroman.org/github_tutorial/pages/first_time.html) before going further.

Now, clone cloudera/hue:

    git clone https://github.com/cloudera/hue

Then, go inside your git repository:

    romain@runreal:~/projects/hue$ rbt setup-repo

    Enter the Review Board server URL: https://review.cloudera.org

    Use the Git repository 'hue' (git://github.com/cloudera/hue.git)? [Yes/No]: yes

    Create '/home/romain/projects/hue/.reviewboardrc' with the following?

    REVIEWBOARD_URL = "https://review.cloudera.org"

    REPOSITORY = "hue"

    BRANCH = "master"

    [Yes/No]: yes

    Config written to /home/romain/projects/hue/.reviewboardrc

Create a new branch with the jira id (HUE-XXX) as the branch name:

    git checkout master
    git pull --rebase origin master
    git checkout -b HUE-XXX

Then make your changes in code:

    git add <file>
    git diff --cached
    git commit -m "HUE-XXX <Ticket summary>"

# Post a review

We have wrapped up the typical submission in a dedicated [tools/scripts/hue-review](https://github.com/cloudera/hue/blob/master/tools/scripts/hue-review) script prefilled with all the details of the commits:

Now we post the review:

    tools/scripts/hue-review HEAD~1..HEAD <reviewers> "HUE-XXX [component] <Ticket summary>" --bugs-closed=HUE-XXX

* Above command must return the review link as given in below example.
* Goto the review link and varify details & press publish. All the reviewers will be informed with an email.

eg:

    tools/scripts/hue-review HEAD~1..HEAD romain,enricoberti,erickt "HUE-2123 [beeswax] Handle cancel state properly" -bugs-closed=HUE-2123

    Review request #4501 posted.

    https://review.cloudera.org/r/4501


Et voila! Here is our review https://review.cloudera.org/r/4501.

**Note**:

If you have more than one diff, update `HEAD~1..HEAD` accordingly (e.g. `HEAD~2..HEAD`)

Now go to the ticket and add a comment with content

* Ticket summary
* Review @ review link

# Update a review

Modify the previous commit diff:

    git add <file>
    git commit --amend

Update the review:

    rbt post -u -r <Review-board-id> HEAD~1..HEAD

Again, go to the review link and varify details & press publish.

# Ship It

Once we get ship it from at least one reviewer, we can push the changes to master

    git rebase origin/master
    git push origin HEAD:ci-commit-master-<yourname>

* The push will auto run the tests and push it to master
* It can be seen on https://circleci.com/gh/cloudera/workflows/hue
  * Two builds would be made - One for Python 2.7 and another for Python 3.6
  * If successful, the change would be auto merged to master
  * On failure, we will get a mail
  * Runs usually take 10-20 min
* Once merged mark the review as submitted - **Close > Submitted**
* Add the commit link to the ticket and mark it as resolved

**Note**:

For lightweight issues, Github [pull requests](https://github.com/cloudera/hue/pulls) are also welcomed! To learn how pull request works please refer this [link](https://github.com/asmeurer/git-workflow).

# Sump-up

We hope that Review Board and these commands will make your life easier and encourage you to [contribute to Hue](https://github.com/cloudera/hue/blob/master/CONTRIBUTING.md) 😉

As usual feel free to send feedback on the [hue-user](http://groups.google.com/a/cloudera.org/group/hue-user) list or [@gethue](https://twitter.com/gethue)!
