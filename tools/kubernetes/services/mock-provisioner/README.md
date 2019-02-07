# Provisioning Service

A quick and dirty provisioning service to manage the lifecycle of Impala clusters.  See
[provisioner.yaml](./provisioner.yaml) for the Altus-style API specification.  In a proper
implementation this would be split into an Altus API gateway and backend provisioning service.

## Development

```sh
npm install
node server.js
```

## Deployment

