# Hue Chart

This is an Helm chart to easily start a Hue service.


## Install

    cd tools/kubernetes/helm/hue

View the configuration [values.yaml](values.yaml), edit if needed and run:

    helm install hue -n hue


And follow-up the instructions printed on the screen for conneting to Hue.

By default you should see these running containers:

    kubectl get pods
    NAME                                          READY   STATUS    RESTARTS   AGE
    hue-4n2ck                                     1/1       Running   0          3h
    hue-postgres-5jg77                            1/1       Running   0          12d

## Un-install

    helm delete hue --purge
