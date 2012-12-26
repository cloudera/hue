
describe("WorkflowModel", function(){

  function create_three_step_workflow(workflow_id) {
    var workflow_model = new WorkflowModel({
      id: 1,
      name: "Test-Three-Step-Workflow",
      start: 1,
      end: 5
    });
    var registry = new Registry();
    var workflow = new Workflow({
      model: workflow_model,
      data: {
        "nodes":[{
            "description":"",
            "workflow":workflow_id,
            "child_links":[{
                "comment":"",
                "name":"to",
                "parent":1,
                "child":2
              },{
                "comment":"",
                "name":"related",
                "parent":1,
                "child":5
            }],
            "node_type":"start",
            "id":1,
            "name":"start"
          },{
            "id":2,
            "name":"Sleep-1",
            "workflow":workflow_id,
            "node_type":"mapreduce",
            "jar_path":"/user/hue/oozie/workspaces/lib/hadoop-examples.jar",
            "child_links":[{
                "comment":"",
                "name":"ok",
                "parent":2,
                "child":3
              },{
                "comment":"",
                "name":"error",
                "parent":2,
                "child":6
              }],
        },{
          "id":3,
          "name":"Sleep-2",
          "workflow":workflow_id,
          "node_type":"mapreduce",
          "jar_path":"/user/hue/oozie/workspaces/lib/hadoop-examples.jar",
          "child_links":[{
              "comment":"",
              "name":"ok",
              "parent":3,
              "child":4
            },{
              "comment":"",
              "name":"error",
              "parent":3,
              "child":6
            }],
        },{
          "id":4,
          "name":"Sleep-3",
          "workflow":workflow_id,
          "node_type":"mapreduce",
          "jar_path":"/user/hue/oozie/workspaces/lib/hadoop-examples.jar",
          "child_links":[{
              "comment":"",
              "name":"ok",
              "parent":4,
              "child":5
            },{
              "comment":"",
              "name":"error",
              "parent":4,
              "child":6
            }],
        },{
          "id":6,
          "name":"kill",
          "workflow":workflow_id,
          "node_type":"kill",
          "child_links":[],
          "message":"Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]",
        },{
          "id":5,
          "name":"end",
          "workflow":workflow_id,
          "node_type":"end",
          "child_links":[],
        }],
      },
      registry: registry
    });
    return workflow;
  }

  function create_pig_workflow(workflow_id) {
    var workflow_model = new WorkflowModel({
      id: 1,
      name: "Test-pig-Workflow",
      start: 1,
      end: 5
    });
    var registry = new Registry();
    var workflow = new Workflow({
      model: workflow_model,
      data: {
        "nodes":[{
            "description":"",
            "workflow":workflow_id,
            "child_links":[{
                "comment":"",
                "name":"to",
                "parent":1,
                "child":2
              },{
                "comment":"",
                "name":"related",
                "parent":1,
                "child":5
            }],
            "node_type":"start",
            "id":1,
            "name":"start"
          },{
            "id":2,
            "name":"Pig-1",
            "workflow":workflow_id,
            "node_type":"pig",
            "script_path":"test.pig",
            "child_links":[{
                "comment":"",
                "name":"ok",
                "parent":2,
                "child":3
              },{
                "comment":"",
                "name":"error",
                "parent":2,
                "child":4
              }],
        },{
          "id":4,
          "name":"kill",
          "workflow":workflow_id,
          "node_type":"kill",
          "child_links":[],
          "message":"Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]",
        },{
          "id":3,
          "name":"end",
          "workflow":workflow_id,
          "node_type":"end",
          "child_links":[],
        }],
      },
      registry: registry
    });
    return workflow;
  }

  describe("Workflow operations", function(){
    var json = '{"id":1,"name":"Test-pig-Workflow","start":1,"end":5,"description":"","schema_version":0.4,"deployment_dir":"","is_shared":true,"parameters":"[]","job_xml":"","nodes":[{"description":"","workflow":1,"child_links":[{"comment":"","name":"to","parent":1,"child":2},{"comment":"","name":"related","parent":1,"child":5}],"node_type":"start","id":1,"name":"start"},{"id":2,"name":"Pig-1","workflow":1,"node_type":"pig","script_path":"test.pig","child_links":[{"comment":"","name":"ok","parent":2,"child":3},{"comment":"","name":"error","parent":2,"child":4}],"description":"","files":"[]","archives":"[]","job_properties":"[]","prepares":"[]","job_xml":"","params":"[]"},{"id":4,"name":"kill","workflow":1,"node_type":"kill","child_links":[],"message":"Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]","description":""},{"id":3,"name":"end","workflow":1,"node_type":"end","child_links":[],"description":""}]}';
    var node = null;
    var viewModel = create_pig_workflow(1);
    viewModel.rebuild();

    it("Ensure serialized data sent to server is proper", function() {
      expect(viewModel.toJSON()).toEqual(json);
    });

    it("Ensure data received from server can be loaded", function() {
      viewModel.reload($.parseJSON(json.replace('test.pig','test1.pig')));
      expect(viewModel.id()).toEqual(1);
      expect(viewModel.name()).toEqual('Test-pig-Workflow');
      expect(viewModel.start()).toEqual(1);
      expect(viewModel.description()).toEqual("");
      expect(viewModel.schema_version()).toEqual(0.4);
      expect(viewModel.deployment_dir()).toEqual("");
      expect(viewModel.is_shared()).toEqual(true);
      expect(viewModel.parameters().length).toEqual(0);
      expect(viewModel.job_xml()).toEqual("");
      expect(viewModel.nodes().length).toEqual(3);
      expect(viewModel.nodes()[1].script_path()).toEqual('test1.pig');
    });
  });

  describe("Node APIs", function(){
    var node = null;
    var viewModel = create_three_step_workflow(2);
    viewModel.rebuild();

    it("Should be able to detach a node", function() {
      node = viewModel.nodes()[2];
      node.detach();
      viewModel.rebuild();
      expect(viewModel.nodes().length).toEqual(4);
    });

    it("Should be able to append a node", function() {
      viewModel.nodes()[1].append(node);
      viewModel.rebuild();
      expect(viewModel.nodes().length).toEqual(5);
    });

    it("Should be able to fail when appending the same node", function() {
      viewModel.nodes()[1].append(node);
      viewModel.rebuild();
      expect(viewModel.nodes().length).toEqual(5);
    });
  });

  // describe("Node movement", function(){
  //   it("Should be able to move a node up", function() {

  //   });

  //   it("Should be able to move a node down", function() {

  //   });

  //   it("Should be able to create a fork", function() {

  //   });

  //   it("Should be able to create a decision", function() {

  //   });
  // });

  // describe("Node operations", function(){
  //   it("Should be able to edit a node", function() {
  //     $('.edit-node-link')[0].click();
  //     expect($("#node-modal").length).toBeGreaterThan(0);
  //   });

  //   it("Should be able to create a node", function() {
  //     $('.new-node-link[data-node-type=mapreduce]')[0].click();
  //     expect($("#node-modal").length).toBeGreaterThan(0);
  //   });

  //   it("Should be able to clone a node", function() {
  //     $('.clone-node-link')[0].click();
  //     expect($("#node-modal").length).toBeGreaterThan(0);
  //   });

  //   it("Should be able to remove a node", function() {
  //     $('.delete-node-btn')[0].click();
  //     expect($("#node-modal").length).toBeGreaterThan(0);
  //   });
  // });
});
