# Set of Hue scripts to help manage hue.  While some of these are self contained, the most important
# ones have library calls to the lib directory.  You must download the entire git repo for these
# to work.  Also note, they all make use of Hue's configuration and the /proc directory.  This
# means these scripts MUST be run as ROOT.

git clone https://github.com/cmconner156/hue_scripts /opt/cloudera/hue_scripts
cd /opt/cloudera/hue_scripts
./script_runner

#This shows the available scripts in [custom_scripts] section, the rest are normal hue commands.
#

[root@nightly516-1 hue_scripts]# ./script_runner
Usage: script_runner subcommand [options] [args]

Options:
  -v VERBOSITY, --verbosity=VERBOSITY
                        Verbosity level; 0=minimal output, 1=normal output,
                        2=verbose output, 3=very verbose output
  --settings=SETTINGS   The Python path to a settings module, e.g.
                        "myproject.settings.main". If this isn't provided, the
                        DJANGO_SETTINGS_MODULE environment variable will be
                        used.
  --pythonpath=PYTHONPATH
                        A directory to add to the Python path, e.g.
                        "/home/djangoprojects/myproject".
  --traceback           Raise on exception
  --version             show program's version number and exit
  -h, --help            show this help message and exit

Type 'script_runner help <subcommand>' for help on a specific subcommand.

Available subcommands:

[auth]
    changepassword
.......
[custom_commands]
    backend_test_curl
    change_owner_of_docs
    delete_user
    estimate_concurrent_users
    hue_desktop_document_cleanup
    list_groups
    promote_to_superuser
    remove_doc2_without_content_object
    remove_duplicate_user_preferences
    remove_orphaned_docs
    rename_duplicate_users
    run_hive_impala_query
    share_all_workflows
......


#Commands:

script_runner backend_test_curl

- This will test all of the REST API backend services to make sure they are running.  This includes HTTPFS, Resource Manager, Job History Server, Oozie, Solr.  Then outputs the matching curl commands to test outside of Hue.

script_runner change_owner_of_docs --olduser cconner --newuser cconner1

- This will change the owner of any documents owned by oldusuer to newuser.

script_runner delete_user --username cconner

- This will delete the user specified by uusername.

script_runner estimate_concurrent_users --last1h

- This will check the access logs and try to estimate the number of active users over the last hour or given timeframe.

script_runner list_groups

- This will show all of the groups that exist in Hue.

script_runner promote_to_superuser --username cconner

- This will promote a non superuser to superuser.

script_runner remove_doc2_without_content_object

- This will remove bad doc2 objects that do not have the content object.

script_runner remove_duplicate_user_preferences

- This will remove duplicate entries in the table desktop_userpreferences.

script_runner remove_orphaned_docs 

- This will remove broken docs that do not have an owner.

script_runner rename_duplicate_users

- If you end up with duplicate usernames somehow, this will rename the most recently created one to prevent data loss, but fix errors.

script_runner run_hive_impala_query --impala --user cconner --query "select * from sample_07"

- This will run a query againsit hive or impala using Hue code, but outside the Hue process.  It will iimpersonate the specified user.  This is good for determining if an issue is caused by Hue or the backend service.

script_runner share_all_workflows --owner cconner --sharegroups test1,test2 --permissioins read,write

- This will share workflows from --owner to a comma separated list of shareusers or sharegroups and a list of permissionis specified by --permissions.

hue_download_watcher.sh

- This script can be used to capture info surrounding downloads from Hue.

hue_clean_duplicate_permissions.sh

- This script is old, but it would have cleaned up duplicate entries for HuePermission objects

extract_archive_in_hdfs.sh

- Debug version of the same extraction script in Hue source.
