# Hue Website Chart

This is an Helm chart to easily manage the Hue websites, gethue, docs, cdn, forum.

## Install

    cd tools/kubernetes/helm/website

View the configuration [values.yaml](values.yaml), edit if needed and run:

    helm install website website --namespace gethue

[values.yaml](values.yaml) contains the most important parameters in the `hue` section with for example which database to use. The `ini`
section let you add any extra [regular parameter](https://docs.gethue.com//administrator/configuration/server/).

Then follow-up the instructions printed on the screen for getting the URL to connect to the sites.

    kubectl get pods -ngethue
    NAME                         READY   STATUS    RESTARTS   AGE
    docs-5d6485d457-l6j95        1/1     Running   0          67s
    website-5c6fbf8f4b-glh9v     1/1     Running   0          67s
    website-jp-964f9cc57-2x68f   1/1     Running   0          67s


## Uninstall

    helm delete website --purge --namespace gethue

## Domain name

See the NGINX section in the [Hue chart README](tools/kubernetes/helm/hue/README.md).
