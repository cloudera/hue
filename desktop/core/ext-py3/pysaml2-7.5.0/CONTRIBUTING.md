# Contributing guidelines


## Questions or Problems

Please, do not open issues for general support questions as we want to keep GitHub
issues for bug reports and feature requests. Instead, we recommend using our [mailing
list](https://lists.sunet.se/postorius/lists/idpy-discuss.lists.sunet.se/) or asking
support-related questions on the [Slack workspace](https://identity-python.slack.com/)
([invitation](https://join.slack.com/t/identity-python/shared_invite/enQtNzEyNjU1NDI1MjUyLTM2MWI5ZGNhMTk1ZThiOTIxNWY2OTY1ODVmMWNjMzUzMTYxNTY5MzE5N2RlYjExZTIyM2MwYjBjZGE4MGVlMTM)).

To save your and our time, we will systematically close all issues that are requests for
general support and redirect people to the channels above.


## Issues and Bugs

If you find a bug in the source code, you can help us by submitting an issue to our
GitHub Repository. Even better, you can submit a Pull Request with a fix.


## Feature Requests

You can request a new feature by submitting an issue to our GitHub Repository. If you
would like to implement a new feature, please consider the size of the change in order
to determine the right steps to proceed:

- For a Major Feature, first open an issue and outline your proposal so that it can be
  discussed. This process allows us to better coordinate our efforts, prevent
  duplication of work, and help you to craft the change so that it is successfully
  accepted into the project.

- Small Features can be crafted and directly submitted as a Pull Request.


## Improving Documentation

Should you have a suggestion for the documentation, you can open an issue and outline
the problem or improvement you have - however, creating the doc fix yourself is much
better!

If you want to help improve the docs, it's a good idea to let others know what you're
working on to minimize duplication of effort. Create a new issue (or comment on a
related existing one) to let others know what you're working on.

If you're making a small change (typo, phrasing) don't worry about filing an issue
first. Fork the repository in-place and make a quick change on the fly.

For large fixes, please build and test the documentation before submitting the PR to be
sure you haven't accidentally introduced any layout or formatting issues.


## Submission Guidelines


### Submitting an Issue

Before you submit an issue, please search the issue tracker.
An issue for your problem might already exist
and the discussion might inform you of workarounds readily available.

We want to fix all the issues as soon as possible, but before fixing a bug, we need to
reproduce and confirm it. In order to reproduce bugs, we require that you provide a
minimal reproduction. Having a minimal reproducible scenario gives us a wealth of
important information without going back and forth to you with additional questions.

A minimal reproduction allows us to quickly confirm a bug (or point out a coding problem)
as well as confirm that we are fixing the right problem.

We require a minimal reproduction to save maintainers' time and ultimately be able to
fix more bugs. Often, developers find coding problems themselves while preparing a
minimal reproduction. We understand that sometimes it might be hard to extract
essential bits of code from a larger codebase, but we really need to isolate the problem
before we can fix it.

Unfortunately, we are not able to investigate / fix bugs without a minimal reproduction,
so if we don't hear back from you, we are going to close an issue that doesn't have
enough information to be reproduced.


### Submitting a Pull Request (PR)

Before you submit your Pull Request (PR) consider the following guidelines:

1. Search [GitHub](../pulls) for an open or closed PR
   that relates to your submission. You don't want to duplicate existing efforts.

2. Be sure that an issue describes the problem you're fixing, or documents the design
   for the feature you'd like to add. Discussing the design upfront helps to ensure that
   we're ready to accept your work.

3. [Fork](https://docs.github.com/en/github/getting-started-with-github/fork-a-repo) the repo.

4. In your forked repository, make your changes in a new git branch:

   ```shell
   $ git checkout -b my-fix-branch main
   ```

5. Create your patch, **including appropriate test cases**.
   Remember to follow the [Coding Rules](#coding-rules).

6. Run the full test suite, as described in the [developer documentation][dev-doc],
   and ensure that all tests pass.

7. Commit your changes using a descriptive commit message.

   ```shell
   $ git commit --all
   ```
   Note: the optional commit `-a` command line option will automatically "add" and "rm" edited files.

8. Push your branch to GitHub:

    ```shell
    $ git push origin my-fix-branch
    ```

9. In GitHub, create a new pull request.


#### Addressing review feedback

If we ask for changes via code reviews then:

1. Make the required updates to the code.
2. Re-run the test suite to ensure tests are still passing.
3. Create a fixup commit and push to your GitHub repository. Update your Pull Request:

   ```shell
   $ git commit --all --fixup HEAD
   $ git push
   ```

   For more info on working with fixup commits see [here](docs/FIXUP_COMMITS.md).

That's it! Thank you for your contribution!


## Coding Rules

To ensure consistency throughout the source code,
keep these rules in mind as you are working:

* All features or bug fixes **must be tested** by one or more specs (unit-tests).
* All public API methods **must be documented**.
* We follow [Black's style guide](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html),
  and wrap all code at **120 characters**.
  Pre-configured tools to automatically lint and format code are available, see [DEVELOPER.md](DEVELOPER.md).
