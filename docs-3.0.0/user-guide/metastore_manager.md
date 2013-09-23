<link rel="stylesheet" href="docbook.css" type="text/css" media="screen" title="no title" charset="utf-8"></link>

<h1>Metastore Manager</h1>
<p>The Metastore Manager application enables you to manage the databases,
tables, and partitions of the
<a href="http://archive.cloudera.com/cdh4/cdh/4/hive/">Hive</a> metastore shared by
the (<a href="../beeswax.html">Beeswax</a> and <a href="../impala.html">Cloudera Impala Query
UI</a>) applications. You can use Metastore
Manager to perform the following operations:</p>
<ul>
<li>Databases<ul>
<li><a href="#selectDatabase">Select a database</a></li>
<li><a href="#createDatabase">Create a database</a></li>
<li><a href="#dropDatabase">Drop databases</a></li>
</ul>
</li>
<li>
<p>Tables</p>
<ul>
<li><a href="#createTables">Create tables</a></li>
<li><a href="#browseTables">Browse tables</a></li>
<li><a href="#importDataIntoTables">Import data into a table</a></li>
<li><a href="#dropTables">Drop tables</a></li>
<li><a href="#viewTableLocation">View the location of a table</a></li>
</ul>
</li>
</ul>
<h2>Metastore Manager Installation and Configuration</h2>
<p>Metastore Manager is one of the applications installed as part of Hue.
For information about installing and configuring Hue, see the Hue Installation
manual.</p>
<h2>Starting Metastore Manager</h2>
<p>Click the <strong>Metastore Manager</strong> icon
(<img alt="image" src="images/icon_table_browser_24.png" />) in the navigation bar at
the top of the Hue browser page.</p>
<h3>Installing Sample Tables</h3>
<p><img alt="image" src="images/note.jpg" /> <strong>Note</strong>: You must be a superuser to perform
this task.</p>
<ol>
<li>Click <img alt="image" src="images/quick_start.png" />. The Quick Start Wizard
    opens.</li>
<li>Click <strong>Step 2: Examples</strong>.</li>
<li>Click <strong>Beeswax (Hive UI)</strong> or <strong>Cloudera Impala Query UI</strong>.</li>
</ol>
<h3>Importing Data</h3>
<p>If you want to import your own data instead of installing the sample
tables, follow the procedure in <a href="#createTables">Creating Tables</a>.</p>
<p><a id="selectDatabase"></a>
Selecting a Database</p>
<hr />
<ol>
<li>In the pane on the left, select the database from the DATABASE
    drop-down list.</li>
</ol>
<p><a id="createDatabase"></a>
Creating a Database</p>
<hr />
<ol>
<li>Click <img alt="image" src="images/databases.png" />.</li>
<li>
<ol>
<li>Specify a database name and optional description. Database names
    are not case-sensitive. Click <strong>Next</strong>.</li>
<li>Do one of the following:<ul>
<li>Keep the default location in the Hive warehouse folder.</li>
<li>Specify an external location within HDFS:<ol>
<li>Uncheck the <strong>Location</strong> checkbox.</li>
<li>In the External location field, type a path to a folder
    on HDFS or click <img alt="image" src="images/browse.png" /> to browse
    to a folder and click <strong>Select this folder</strong>.</li>
</ol>
</li>
</ul>
</li>
</ol>
<p>Click <strong>Create a new database</strong>.</p>
<ol>
<li>Click the <strong>Create Database</strong> button.</li>
</ol>
</li>
</ol>
<p><a id="selectDatabase"></a>
Dropping Databases</p>
<hr />
<ol>
<li>Click <img alt="image" src="images/databases.png" />.</li>
<li>In the list of databases, check the checkbox next to one or more
    databases.</li>
<li>Click the <img alt="image" src="images/trash.png" /> Drop button.</li>
<li>Confirm whether you want to delete the databases.</li>
</ol>
<p><a id="createTables"></a>
Creating Tables</p>
<hr />
<p>Although you can create tables by executing the appropriate Hive HQL DDL
query commands, it is easier to create a table using the Metastore
Manager table creation wizard.</p>
<p>There are two ways to create a table: from a file or manually. If you
create a table from a file, the format of the data in the file will
determine some of the properties of the table, such as the record and
file formats. The data from the file you specify is imported
automatically upon table creation. When you create a file manually, you
specify all the properties of the table, and then execute the resulting
query to actually create the table. You then import data into the table
as an additional step.</p>
<p><strong>From a File</strong></p>
<ol>
<li>In the ACTIONS pane in the Metastore Manager window, click <strong>Create
    a new table from a file</strong>. The table creation wizard starts.</li>
<li>Follow the instructions in the wizard to create the table. The basic
    steps are:<ul>
<li>Choose your input file. The input file you specify must exist.
    Note that you can choose to have Beeswax create the table
    definition only based on the import file you select, without
    actually importing data from that file.</li>
<li>Specify the column delimiter.</li>
<li>Define your columns, providing a name and selecting the type.</li>
</ul>
</li>
<li>
<p>Click <strong>Create Table</strong> to create the table. The new table's metadata
    displays on the right side of the <strong>Table Metadata</strong> window. At this
    point, you can view the metadata or a sample of the data in the
    table. From the ACTIONS pane you can import new data into the table,
    browse the table, drop it, or go to the File Browser to see the
    location of the data.</p>
</li>
</ol>
<p><strong>Manually</strong></p>
<ol>
<li>In the ACTIONS pane in the Metastore Manager window, click <strong>Create
    a new table manually</strong>. The table creation wizard starts.</li>
<li>Follow the instructions in the wizard to create the table. The basic
    steps are:<ul>
<li>Name the table.</li>
<li>Choose the record format.</li>
<li>Configure record serialization by specifying delimiters for
    columns, collections, and map keys.</li>
<li>Choose the file format.</li>
<li>Specify the location for your table's data.</li>
<li>Specify the columns, providing a name and selecting the type for
    each column.</li>
<li>Specify partition columns, providing a name and selecting the
    type for each column.</li>
</ul>
</li>
<li>
<p>Click <strong>Create table</strong>. The Table Metadata window displays.</p>
</li>
</ol>
<p><a id="browseTables"></a>
Browsing Tables</p>
<hr />
<p><strong>To browse table data:</strong></p>
<p>In the Table List window, check the checkbox next to a table name and
click <strong>Browse Data</strong>. The table's data displays in the Query Results
window.</p>
<p><strong>To browse table metadata:</strong></p>
<p>Do one of the following:</p>
<ul>
<li>In the Table List window, click a table name.</li>
<li>
<p>Check the checkbox next to a table name and click <strong>View</strong>.</p>
</li>
<li>
<p>The table's metadata displays in the <strong>Columns</strong> tab. You can view
    the table data by selecting the <strong>Sample</strong> tab.</p>
</li>
<li>If the table is partitioned, you can view the partition columns by
    clicking the <strong>Partition Columns</strong> tab and display the partitions by
    clicking <strong>Show Partitions(n)</strong>, where n is the number of partitions
    in the ACTIONS pane on the left.</li>
</ul>
<p><a id="importDataIntoTables"></a>
Importing Data into a Table</p>
<hr />
<p>When importing data, you can choose to append or overwrite the table's
data with data from a file.</p>
<ol>
<li>In the Table List window, click the table name. The Table Metadata
    window displays.</li>
<li>In the ACTIONS pane, click <strong>Import Data</strong>.</li>
<li>For <strong>Path</strong>, enter the path to the file that contains the data you
    want to import.</li>
<li>Check <strong>Overwrite existing data</strong> to replace the data in the
    selected table with the imported data. Leave unchecked to append to
    the table.</li>
<li>Click <strong>Submit</strong>.</li>
</ol>
<p><a id="dropTables"></a>
Dropping Tables</p>
<hr />
<ol>
<li>In the Table List window, click the table name. The Table Metadata
    window displays.</li>
<li>In the ACTIONS pane, click <strong>Drop Table</strong>.</li>
<li>Click <strong>Yes</strong> to confirm the deletion.</li>
</ol>
<p><a id="viewTableLocation"></a>
Viewing a Table's Location</p>
<hr />
<ol>
<li>In the Table List window, click the table name. The Table Metadata
    window displays.</li>
<li>Click <strong>View File Location</strong>. The file location of the selected
    table displays in its directory in the File Browser window.</li>
</ol>