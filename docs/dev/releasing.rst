The version used in the Maven projects needs to be set by hand in the
following files:
- maven/pom.xml
- desktop/libs/hadoop/java/pom.xml
- desktop/libs/*/setup.py

In the case of maven/pom.xml, change the first <version> tag. In the
other cases, change the <version> tag within the <parent> tag.

In addition, when running a release, all of these will need to be
changed to remove "-SNAPSHOT". This will eventually be automated via
the Maven release plugin, but is by hand for the moment. For release
builds, you will also need to change MAVEN_VERSION in Makefile.vars to
not include "-SNAPSHOT".
