
const uuid = require('uuid/v4');
const Client = require('kubernetes-client').Client;
const config = require('kubernetes-client').config;
var client;
try {
  client = new Client({ config: config.fromKubeconfig(), version: '1.10' });
} catch(error) {
  client = new Client({ config: config.getInCluster(), version: '1.10' });
}

const Command = require('./command.js');
const Prometheus = require('prom-client');
const request = require("request");
var configuration = require('./config');


const TENANT = "12a0079b-1591-4ca0-b721-a446bda74e67"

// Store in memory for now.
const clusters = {};

// Basic CRUD operations, no validation, no pagination, etc.
const model = {};

//impala_queries_open_running
//impala_queries_open_queued
//impala_queries_closed_failed
//...
const impalaQueriesMetrics = new Prometheus.Gauge({
  name: 'impala_queries',
  help: 'Query metrics',
  labelNames: ['datawarehouse', 'status']
});
const impalaQueriesCounter = new Prometheus.Gauge({
  name: 'impala_queries_count',
  help: 'Query metrics',
  labelNames: ['datawarehouse']
});


function createCluster(options) {
  const cluster = Object.assign({}, {
    cdhVersion: "CDH6.3",
    hdfsNamenodeHost: "hdfs-namenode",
    hdfsNamenodePort: 9820, // 8020
    // metastore.uris=thrift://spark2-envelope515-1.gce.cloudera.com:9083,hdfs.namenode.host=spark2-envelope515-1.gce.cloudera.com,hdfs.namenode.port=8020
    workerCpuCores: 2,
    workerMemoryInGib: 4,
    workerReplicas: 1,
    workerAutoResize: false,
    workercurrentCPUUtilizationPercentage: 0
  }, options);

  cluster.name = cluster.clusterName;
  cluster.crn = `crn:altus:dataware:k8s:${TENANT}:cluster:${cluster.clusterName}/${uuid()}`;
  cluster.creationDate = new Date().toISOString();
  cluster.status = "STARTING";
  cluster.workerReplicasOnline = 0;
  endpointHost = "impala-coordinator-" + cluster.clusterName;
  cluster.coordinatorEndpoint = {privateHost: endpointHost, publicHost: endpointHost, port: 21050};

  return cluster;
}


model.createCluster = async function(options) {
  console.log("Create cluster: " + JSON.stringify(options));
  const cluster = createCluster(options);

  clusters[cluster.crn] = cluster;

  await Command.runCommand(`helm install impala-engine --set-string registry=${configuration.registry},tag=${configuration.registryImpalaTag},name=${cluster.clusterName},worker.replicas=${cluster.workerReplicas},hdfs.namenode.host=${cluster.hdfsNamenodeHost},hdfs.namenode.port=${cluster.hdfsNamenodePort} -n ${cluster.clusterName} --repo=${configuration.helmRepo}`);

  return {"cluster": cluster};
};

async function updateClusterStatus(cluster) {
  if (cluster.status == 'TERMINATED') {
    return
  }

  var statefulset;
  try {
   // TODO: use labels
    statefulset = await client.apis.apps.v1.namespaces('default').deployments("impala-worker-" + cluster.clusterName).get()
  }
  catch(error) {
   console.log(error);
   // If killed manually?
    //if (clusters.status == 'TERMINATING') {
      cluster.status = 'TERMINATED';
      cluster.workerReplicasOnline = 0;
      return
    //}
  }

  if (statefulset == null) {
    cluster.status = "STARTING";
    cluster.workerReplicasOnline = 0;
    return
  }

  status = statefulset.body.status;
  if (status.readyReplicas == null) {
    // Statefulset when just launched will have undefined ready replicas.
    return
  }

  if ((cluster.status == "SCALING_UP" || cluster.status == "SCALING_DOWN") && status.replicas != cluster.workerReplicas) {
    // We are still in progress updating the cluster, don't update the status until statefulset replicas are updated.
    return
  }

  if (status.replicas == status.readyReplicas) {
    cluster.status = "ONLINE";
  }

  if (cluster.workerAutoResize) {
    const hpa = await client.apis.autoscaling.v1.namespaces('default').horizontalpodautoscalers("impala-worker-" + cluster.clusterName).get()
    hpaStatus = hpa.body.status;
    // TODO: polish a bit status when hpa not fully running yet
    cluster.workerReplicasOnline = hpaStatus.currentReplicas;
    cluster.workerReplicas = hpaStatus.currentCPUUtilizationPercentage >= 0 ? hpaStatus.desiredReplicas : hpaStatus.currentReplicas;
    cluster.workercurrentCPUUtilizationPercentage = hpaStatus.currentCPUUtilizationPercentage >= 0 ? hpaStatus.currentCPUUtilizationPercentage : "N/A";
  } else {
    cluster.workerReplicasOnline = status.readyReplicas;
  }
}

model.describeCluster = async function(options) {
  console.log("Describe cluster: " + JSON.stringify(options));
  const cluster = clusters[options.clusterName];
  if (cluster != undefined) {
    updateClusterStatus(cluster);
    return {"cluster": cluster};
  } // TODO else

  return {}
}


model.listClusters = async function(options) {
  var promises = [];
  var clusterNames = [];

  for (var crn in clusters) {
    promises.push(updateClusterStatus(clusters[crn]));
    clusterNames.push(clusters[crn].name);
  }

  var statefulsets = await client.apis.apps.v1.namespaces('default').statefulsets().get(); // Also append DW clusters created outside of provisioner

  statefulsets.body.items.forEach(function(statefulset) {
    var name = statefulset['metadata']['name'].substring("impala-coordinator-".length);
    if (statefulset['metadata']['name'].startsWith("impala-coordinator-") && clusterNames.indexOf(name) == -1) {
      var cluster = createCluster({clusterName: name});
      cluster.status = 'ONLINE';
      cluster.crn = cluster.name // For now crn is the cluster name
      clusters[cluster.crn] = cluster;
    }
  });

  Promise.all(promises);

  return Object.values(clusters);
}

model.updateCluster = async function(options) {
  console.log("Update cluster: " + JSON.stringify(options));

  var cluster = clusters[options.clusterName];
  var command = "";

  if (options.updateClusterAutoResizeChanged) {
    cluster.workerAutoResize = options.updateClusterAutoResize;
    if (options.updateClusterAutoResize) {
      cluster.workerAutoResizeMin = options.updateClusterAutoResizeMin;
      cluster.workerAutoResizeMax = options.updateClusterAutoResizeMax;
      cluster.workerAutoResizeCpu = options.updateClusterAutoResizeCpu;
      command = `kubectl autoscale deployment impala-worker-${cluster.clusterName} --min=${options.updateClusterAutoResizeMin} --max=${options.updateClusterAutoResizeMax} --cpu-percent=${options.updateClusterAutoResizeCpu}`;
    } else {
      command = `kubectl delete hpa impala-worker-${cluster.clusterName}`;
    }
    // TODO: check SCALING UP/DOWN status too
  } else {
    if (cluster.workerReplicas != options.workerReplicas) {
      let originalReplicas = cluster.workerReplicas;
      cluster.workerReplicas = options.workerReplicas;
      if (cluster.workerReplicas > originalReplicas) {
        cluster.status = "SCALING_UP";
      } else if (cluster.workerReplicas < originalReplicas) {
        cluster.status = "SCALING_DOWN";
      }
      await Command.runCommand(`helm upgrade ${cluster.clusterName} impala-engine --set-string registry=${configuration.registry},tag=${configuration.registryImpalaTag},name=${cluster.clusterName},worker.replicas=${cluster.workerReplicas},hdfs.namenode.host=${cluster.hdfsNamenodeHost},hdfs.namenode.port=${cluster.hdfsNamenodePort} --repo=${configuration.helmRepo}`);
    }
  }

  if (command) {
    await Command.runCommand(command);
  }

  return {"cluster": cluster};
}

model.deleteCluster = async function(options) {
  console.log("Delete cluster: " + JSON.stringify(options));
  const cluster = clusters[options.clusterName];
  cluster.status = "TERMINATING";

  await Command.runCommand(`helm delete --purge ${cluster.clusterName}`);
  if (options.workerAutoResize) {
    await Command.runCommand(`kubectl delete hpa impala-worker-${cluster.clusterName}`);
  }

  return;
}


model.getClusterMetrics = async function(options) {
  console.log("Metric cluster: " + JSON.stringify(options));

  var metrics = null;

  Object.keys(clusters).forEach(function(key) {
    var cluster = clusters[key];
    console.log("Scrapping: " + key);
    if (cluster.status != "TERMINATED") {
      request({
        url: `http://${cluster.coordinatorEndpoint.privateHost}:25000/metrics?json=true`,
        json: true
      }, function (error, response, body) {
       console.log("Scapped: " + error + " " + response);
       if (!error && response.statusCode === 200) {
          metrics = body.metric_group.child_groups.filter(group => group.name == "impala-server")[0].metrics;

          var metric = metrics.filter(metric => metric.name == "impala-server.num-queries-registered")[0];
          impalaQueriesMetrics.labels(cluster.clusterName, 'num-queries-registered').set(metric.value);

          var metric = metrics.filter(metric => metric.name == "impala-server.num-queries")[0];
          impalaQueriesCounter.labels(cluster.clusterName).set(metric.value);
        }
      });
    }
  });

  return {"metrics": metrics};
}

module.exports = model;
