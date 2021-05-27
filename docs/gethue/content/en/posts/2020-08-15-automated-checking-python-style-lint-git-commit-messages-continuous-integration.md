---
title: Automatically checking the Python style and title format of Git commits
author: Romain
type: post
date: 2020-08-15T00:00:00+00:00
url: /automated-checking-python-style-and-title-format-of-git-commits-continuous-integration/
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
  - Development
#  - Version 4.8

---

Hi Query Engineers,

The investment in Continuous Integration (CI) and automation continues in order to help scale the resource and quality of the Hue project. This past year saw a lot of improvements with:

* An integrated [commit flow](https://gethue.com/improving-the-developer-productivity-with-some-continuous-integration/) automatically run by [Circle CI](https://circleci.com/gh/cloudera/hue)
* gethue.com and demo.gethue.com websites [link checking](https://gethue.com/checking-dead-links-automatically-continuous-integration/)
* JavaScript styling and artifacts [licensing check](/automated-checking-javascript-licenses-absolute-paths-continuous-integration/)

Here is the latest about how to automatically check that the **coding convention of the Python** API is followed by everybody as well as the **format of the git commit titles**.

## Python linting

Hue is leveraging [Pylint](https://www.pylint.org/) which is an open source program for checking coding standards. It comes with a series of rules that can be selected and customized in a `.pylintrc` file.

To discover early if the changes in a commit adhere to the convention, most of the Code Editor can understand the Pylint configuration with some plugins. This is handy for seeing the error early directly in your editor, which most of the time will even offer to fix it for you.

![Pylint indentation visual check](https://cdn.gethue.com/uploads/2020/08/pylint-indent.png)

## One step at the time

As Hue is a mature project of 10+ years and its code base size is mostly consisting in 50% of Python, it could be too much of a burden to fix all the code styling issues right away. This is why, an incrementat strategy was approached:

* Only lint the files that were updated in your new local commits (it will lint the full content of the file, not just the diff)
* Start only with a minimal styling convention (only basic rules, more rules to add later as the basics are finished)
  * C0326 (bad-whitespace)
  * W0311 (bad-indentation)
  * C0301 (line-too-long)


The command to run [check_for_python_lint.sh](https://github.com/cloudera/hue/blob/master/tools/ci/check_for_python_lint.sh):

    tools/ci/check_for_python_lint.sh

Will then locally output the lines with failing checks:

    [10/Aug/2020 16`:22:17 -0700] runpylint    INFO     Running pylint with args: /home/romain/projects/hue/build/env/bin/pylint --rcfile=/home/romain/projects/hue/desktop/.pylintrc --disable=all --enable=C0301,C0326,W0311 --load-plugins=pylint_django -f parseable apps/beeswax/src/beeswax/api.py desktop/core/src/desktop/management/commands/runpylint.py
    ************* Module beeswax.api
    apps/beeswax/src/beeswax/api.py:144: [C0326(bad-whitespace), ] Exactly one space required after :
          {1:1}
            ^
    apps/beeswax/src/beeswax/api.py:236: [C0326(bad-whitespace), ] Exactly one space required before assignment
        response['status']= 0
                          ^
    apps/beeswax/src/beeswax/api.py:239: [C0326(bad-whitespace), ] Exactly one space required before assignment
        response['status']= 0
                          ^
    apps/beeswax/src/beeswax/api.py:436: [C0326(bad-whitespace), ] Exactly one space required before assignment
        response['message']= str(e)
                          ^
    apps/beeswax/src/beeswax/api.py:678: [C0301(line-too-long), ] Line too long (156/150)
    ************* Module desktop.management.commands.runpylint
    desktop/core/src/desktop/management/commands/runpylint.py:66: [C0301(line-too-long), ] Line too long (255/150)
    desktop/core/src/desktop/management/commands/runpylint.py:70: [C0326(bad-whitespace), ] Exactly one space required around assignment
        a={1:   3}
        ^
    desktop/core/src/desktop/management/commands/runpylint.py:70: [C0326(bad-whitespace), ] Exactly one space required after :
        a={1:   3}
            ^
    desktop/core/src/desktop/management/commands/runpylint.py:72: [W0311(bad-indentation), ] Bad indentation. Found 8 spaces, expected 6

    ------------------------------------------------------------------
    Your code has been rated at 9.86/10 (previous run: 9.88/10, -0.02)


The styling configuration is saved in the [.pylintrc](https://github.com/cloudera/hue/blob/master/.pylintrc).

Then, to make it available automatically to all the new changes, hook it in the `run python lints` section of the [config.yml](https://github.com/cloudera/hue/blob/master/.circleci/config.yml#L109) of CircleCi which is then easily integrated into the Hue CI:

    - run:
        name: run python lints
        command: |
          cd ~/repo

          ./tools/ci/check_for_python_lint.sh /usr/share/hue


![ci pyling success no change](https://cdn.gethue.com/uploads/2020/08/ci-pylint-success.png)

## Git Commit Format check

Similarly to coding convention, having everybody follow the same language for commit titles saves time in the long run.

To keep things simple, only two formats were picked:
* The traditional Hue one with a Jira number
* A github pull request with the standard id at the end

Both needs to have a category within brackets to describe the main area of the change. e.g. [docs], [hive], [docker], [ui]...

Example of valid messages:

    HUE-9374 [impala] Use 26000 as default for thrift-over-http
    [livy] Add numExecutors options (#1238)

And some invalid ones (it is easy to have many combinations):

    [impala] Use 26000 as default for thrift-over-http
    Use 26000 as default for thrift-over-http (#1238)
    HUE-9374 Use 26000 as default for thrift-over-http
    Add numExecutors options


The check logic is part of the `commit-msg` [Git hooks](https://github.com/cloudera/hue/blob/master/tools/githooks).

For checking git commit message format automatically locally, just copy the hooks:

    cp tools/githooks/* .git/hooks
    chmod +x .git/hooks/*

And here is the script running the checks only on your new commits not yet pushed to the master branch:

    ./tools/ci/check_for_commit_message.sh

And then to 100% automated it, also add it to the CI:

    - run:
      name: run commit title format check
      command: |
          cd ~/repo

          ./tools/ci/check_for_commit_message.sh

![ci git title format fail](https://cdn.gethue.com/uploads/2020/08/ci-commit-format-check-fail.png)


And that's it, more development time saved for later!

What is your favorite CI process? Any feedback? Feel free to comment here or on [@gethue](https://twitter.com/gethue)!

Romain from the Hue Team
