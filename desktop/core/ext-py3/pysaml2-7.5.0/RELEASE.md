## Release instructions

When releasing a new version, the following steps should be taken:

1. Make sure the package metadata in `pyproject.toml` is up-to-date.

    ```
    poetry check
    ```

2. Make sure all automated tests pass:

    ```
    poetry run pytest
    ```

3. Bump the version of the package

    ```
    poetry version -- X.Y.Z
    ```

4. Update the [CHANGELOG.md]

5. Commit and sign the changes:

    ```
    git add -u  # CHANGELOG.md pyproject.toml
    git commit -v -s -m "Release version X.Y.Z"
    ```

6. Create a signed release [tag]:

    ```
    git tag -a -s vX.Y.Z -m "Version X.Y.Z"
    ```

7. Push the changes and the release to Github:

    ```
    git push --follow-tags
    ```

8. Publish the release on PyPI:

    ```
    poetry publish --build
    ```

9. Send an email to the pysaml2 list announcing this release


  [VERSION]: https://github.com/IdentityPython/pysaml2/blob/master/VERSION
  [CHANGELOG.md]: https://github.com/IdentityPython/pysaml2/blob/master/CHANGELOG.md
  [docutils]: http://docutils.sourceforge.net/
  [branch]: https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell
  [tag]: https://git-scm.com/book/en/v2/Git-Basics-Tagging#_annotated_tags
