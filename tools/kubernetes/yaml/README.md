
# How to install

    kubectl apply -f hue/

# How to uninstall

    kubectl delete -f hue/

# If using Workers

    kubectl create -f celery/
    kubectl create -f redis/
