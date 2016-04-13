
# Check for missing licence files
# http://creadur.apache.org/rat/apache-rat/index.html 

# Dump with RAT into a file
# For apps, desktop/core/src, desktop/libs
java -jar apache-rat-0.9.jar -d build/release/prod/hue-2.5.0/apps   -E tools/rat/.rat-excludes  > dump.txt

# Then grep and filter ou false positive
egrep "^  /home.*py$" dump.txt | egrep -v "migrations|gen-py|management|examples"

