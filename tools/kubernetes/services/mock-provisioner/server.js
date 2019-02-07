// Quick and dirty provisioning service.

const util = require("util");
const express = require("express");
const morgan = require('morgan');
const bodyParser = require("body-parser");
const validator = require("swagger-express-validator");
const yaml = require("js-yaml");
const fs = require("fs");
const model = require("./model");
const Prometheus = require('prom-client');


// Get api spec, or throw exception on error
let schema = null;
try {
  schema = yaml.safeLoad(fs.readFileSync("provisioner.yaml", "utf8"));
} catch (e) {
  console.error(e);
  process.exit(1);
}

const app = express();
app.use(bodyParser.json());
app.use(morgan('tiny'));

const opts = {
  schema,
  validateRequest: true,
  validateResponse: true,
  requestValidationFn: (req, data, errors) => {
    console.error(
      `failed request validation: ${req.method} ${
        req.originalUrl
      }\n ${util.inspect(errors)}`
    );
  },
  responseValidationFn: (req, data, errors) => {
    console.error(
      `failed response validation: ${req.method} ${
        req.originalUrl
      }\n ${util.inspect(errors)}`
    );
  }
};
app.use(validator(opts));


app.post("/dw/createCluster", async (req, res) => {
  res.json(await model.createCluster(req.body));
});

app.post("/dw/describeCluster", async (req, res) => {
  res.json(await model.describeCluster(req.body));
});

app.post("/dw/listClusters", async (req, res) => {
  res.json({
    clusters: await model.listClusters(req.body)
  });
});

app.post("/dw/updateCluster", async (req, res) => {
  res.json(await model.updateCluster(req.body));
});

app.post("/dw/deleteCluster", async (req, res) => {
  res.json(await model.deleteCluster(req.body));
});

app.get("/", async (req, res) => {
  res.json({app: "cloudera-dw-provisioner", version: "0.1"});
});

// Proxying metrics until natively supported by Impala
app.get('/metrics', async (req, res) => {
  await model.getClusterMetrics(req.body);

  res.set('Content-Type', Prometheus.register.contentType)
  res.end(Prometheus.register.metrics())
})

return app.listen(4747, "0.0.0.0", () =>
  console.log("provisioning service listening on 0.0.0.0:4747")
);
