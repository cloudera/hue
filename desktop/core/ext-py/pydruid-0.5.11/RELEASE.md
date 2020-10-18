# How to craft a PyDruid release and ship to Pypi

Prep
* `git remote add druid-io git@github.com:druid-io/pydruid.git`

New minor release:
* branch off of master to minor `git checkout -b 0.X`
* pick cherries if any

New micro release:
* checkout existing minor release branch `git checkout 0.X`
* pick cherries

Finally:
* run tests
* update version in `setup.py` to `0.X.N`
* commit with commit message `0.X.N`
* `git tag 0.X.N`
* Push release to repo `git push druid-io 0.X 0.X.N`
* Push to pypi `python setup.py sdist upload`

Post changelog
* `./gen_changelog.sh 0.0.0...0.X.N`
