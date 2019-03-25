---
title: "Dashboard"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 3
---

Dashboards are an interactive way to explore your data quickly and easily. No programming is required and the analysis is done by drag & drops and clicks.

Read more about [Dashboards](http://gethue.com/search-dashboards/).

## Concepts

Simply drag & drop widgets that are interconnected together. This is great for exploring new datasets or monitoring without having to type.

### Importing

Any CSV file can be dragged & dropped and ingested into an index in a few clicks via the Data Import Wizard [link]. The indexed data is immediately queryable and its facets/dimensions will be very fast to explore.

### Browsing

The Collection browser got polished in the last releases and provide more information on the columns. The left metadata assist of Hue 4 makes it handy to list them and peak at their content via the sample popup.

### Querying

The search box support live prefix filtering of field data and comes with a Solr syntax autocomplete in order to make the querying intuitive and quick. Any field can be inspected for its top values of statistic. This analysis happens very fast as the data is indexed.

## Databases

### Solr

#### Autocomplete

The top search bar offers a [full autocomplete](http://gethue.com/intuitively-discovering-and-exploring-a-wine-dataset-with-the-dynamic-dashboards/) on all the values of the index.

#### More Like This
The “More like This” feature lets you selected fields you would like to use to find similar records. This is a great way to find similar issues, customers, people... with regard to a list of attributes.

### SQL

Any configured SQL source can be queried via the dashboards.

## Reports

This is work in progress but dashboards will soon offer a classic reporting option.
