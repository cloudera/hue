# Hue Website Chart

This is an Helm chart to easily manage the Hue websites, gethue, docs, cdn, forum.

## Install

    cd tools/kubernetes/helm/website

View the configuration [values.yaml](values.yaml), edit if needed and run:

    helm install website -n website --namespace hue

[values.yaml](values.yaml) contains the most important parameters in the `hue` section with for example which database to use. The `ini`
section let you add any extra [regular parameter](https://docs.gethue.com/latest/administrator/configuration/server/).

Then follow-up the instructions printed on the screen for getting the URL to connect to the sites.

## Uninstall

    helm delete website --purge --namespace hue
