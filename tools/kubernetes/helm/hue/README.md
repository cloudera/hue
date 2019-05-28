# Hue Chart

This is an Helm chart to easily start a Hue service.


## Install

    cd tools/kubernetes/helm/hue

View the configuration [values.yaml](values.yaml), edit if needed and run:

    helm install hue -n hue

[values.yaml](values.yaml) contains the most important parameters in the `hue` section with for example which database to use. The `ini`
section let you add any extra [regular parameter](https://docs.gethue.com/latest/administrator/configuration/server/).


Then follow-up the instructions printed on the screen for getting the URL to connect to Hue.

By default you should see these running containers:

    kubectl get pods
    NAME                                          READY   STATUS    RESTARTS   AGE
    hue-4n2ck                                     1/1       Running   0          3h
    hue-postgres-5jg77                            1/1       Running   0          12d

## Uninstall

    helm delete hue --purge
