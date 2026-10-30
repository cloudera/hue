+++
title = "User"
date = 2019-03-13T18:27:26-07:00
weight = 3
chapter = false
pre = "<b>2. </b>"
+++

This section describes the main functionalities from an end user point of view.

Hue is a single-page interface that lets you find, explore, and query data without losing your context.

See the [connectors page](/administrator/configuration/connectors/#databases) for the list of supported databases and data warehouses.

## Typical workflow

1. **Find or import your data.** Use the left assist panel to browse your data without leaving the Editor. The top search looks through your saved queries and the tables, columns, and databases of connected [data catalogs](/user/browsing/#data-catalogs). If the data does not exist yet, [import it](/user/browsing/#importing-data).
2. **Query your data.** The [Editor](/user/querying/#editor) autocompletes SQL, highlights syntax errors, and shows inline documentation. The right assist panel shows table previews and the language reference. Refine your results, then download them as CSV or XLS, or export them to a file system or a table.

## Applications

* **Editor**: Write and run SQL queries with autocomplete and query assistance.
* **Browsers**: Search, preview, and act on tables, files, and jobs.
* **Dashboard**: Explore your data interactively with drag and drop, without programming. Enabled by default.
* **Scheduler**: Build workflows and schedule them to run regularly. It requires the Oozie app to be configured by your administrator.

Each app of Hue can be extended to support your own languages or apps as detailed in the [developer guide](/developer/).
