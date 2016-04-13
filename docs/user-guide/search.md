
<link rel="stylesheet" href="docbook.css" type="text/css" media="screen" title="no title" charset="utf-8"></link>

# Solr Search


The Solr Search application, which is based on  [Apache Solr](http://lucene.apache.org/solr/), allows you to perform keyword searches across Hadoop data. A wizard lets you style the result snippets, specify facets to group the results, sort the results, and highlight result fields.

## Solr Search Installation and Configuration

Solr Search is one of the applications installed as part of Hue. For information about installing and configuring Hue, see the Hue Installation
manual.

## Starting  Solr Search

Click the ** Solr Search** icon
(![image](images/icon_search_24.png)) in the navigation bar at the top of
the Hue browser page. **Solr Search** opens to the  [Collection Manager](#collectionManager). If there are no collections, the [Import Collections and Cores](#importCollection) dialog displays.

<a id="collectionManager"></a>
## Collection Manager

In Collection Manager you import, copy, and delete [collections](http://wiki.apache.org/solr/SolrCloud#A_little_about_SolrCores_and_Collections).

### Displaying the Collection Manager
When you start Solr Search, the Collection Manager displays. You navigate to the Collection Manager by clicking **Collection manager** in the Search page or the Template Editor.

###  Filtering Collections

When you type in the Filter field, the list of collections is dynamically filtered to display only those rows
containing text that matches the specified substring.

<a id="importCollection"></a>
### Importing Collections 

1. If there are existing collections, click the ![image](images/import.png) **Import** button at the top right. The Import Collections and Cores dialog displays.
1. Check the checkboxes next to the collections to import.
1. Click **Import Selected**. The collection is added to the Collection Manager.

### Editing Collection Properties
1. In the Collection Manager, click a collection.
1. In the **COLLECTION** area on the left, click **Properties**.
1. Edit a property and click **Save**.


### Searching a Collection

1. In the Collection Manager, click **Search page** or click **Search it** in the Collection area on the left. The Search page displays.
1. Select a collection from the **Search in** drop-down list.
1. Type a search string in the **Search...** text box.
1. Press **Enter** or click the ![image](images/eyeglass.png)  icon.

-  If you have defined [facets](#facets), click a facet to display only those results in the group defined by the facet.
-  If you have defined [sorting fields](#sorting), select from the **Sort by** drop-down list to sort the results.
-  Click ![image](images/clear.png) to clear the search string.

## Styling Search Results

Do one of the following:

- In the Collection Manager, click a collection.
- In the Search page, select a collection from the **Search in** drop-down list and click ** Customize this collection**.  The Template Editor displays.

### Template Editor

The Template Editor provides four features:

- [Snippet editor](#snippetEditor) - Specify the layout of the search result snippet, which fields appear in the snippet, and style the results.
- [Facet editor](#facetEditor) - Define buckets in which to group results.
- [Sort editor](#sortEditor) - Specify on which fields and order the results are sorted. 
- [Highlighting editor](#highlightingEditor) - Enable highlighting of search fields. 

<a id="snippetEditor"></a>
#### Snippet Editor

1. In the Snippet Editor, click a tab to choose the method for editing the search snippet fields and styling:
1. - **Visual editor** - Click ![image](images/layoutChooser.png) to choose an overall layout for the snippet.
1. - - Select the fields and functions from the drop-down lists on the right and click ![image](images/add.png). 
1. - - Select fields, right-click, and select **Cut** and **Paste** to place the fields on the canvas. 
1. - - Select fields and apply styling using the buttons on top.
1. - **Source** - 
1. - - Select the data fields and functions from the drop-down lists on the right.
1. - - Specify layout and styling using HTML tags.
1. - **Preview** - Preview the snippet.
1. - **Advanced** - Specify styles for CSS classes specified in the Source tab.
1. Click **Save**.

<a id="facetEditor"></a>
#### Facet Editor

By default, faceting  search result fields is disabled. Click **Enabled** to enable faceting.

1. In the Template Editor, click **2. Facets**. You can move between the facet tabs by clicking each **Step** tab, or by clicking **Back** and **Next**.
1. In the General tab, specify 
1. - **Limit** - the maximum number of values for each facet.
1. - **Mincount** - the minimum number of search results that fall into a group for the facet to display on the Search page.
1. In the Field, Range, and Date Facet tabs,  specify the facet properties and click ![image](images/add.png) **Add**.
1. In the Facets Order tab, drag and drop the facet to specify the order in they appear in the Search page.
1. Click **Save**. When you display the Search page, the facets display on the left.

<a id="sortEditor"></a>
#### Sorting Editor 

By default, sorting on search result fields is disabled. Click **Enabled** to enable sorting.

1. In the Template Editor, click **3. Sorting**. 
1. In the Field drop-down, select a field. Optionally specify a label for the field. 
1. The default order is ascending. Click the arrows to change the order.
1. Click  ![image](images/add.png) **Add**.
1. Click **Save**. When you display search results, the results are sorted by the fields in the order that  they appear left to right. 

<a id="highlightingEditor"></a>
#### Highlighting Editor 

By default,highlighting search result fields is disabled. Click **Enabled** to enable highlighting.

1. In the Template Editor, click **3. Highlighting**. 
1. Select the fields to be highlighted.
1. Click **Save**. When you display search results, the selected fields are displayed with the style of the **em** class defined in the Advanced tab of the [Snippet editor](#snippetEditor). 





