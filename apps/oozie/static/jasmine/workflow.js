
describe("WorkflowModel", function(){

  function create_three_step_workflow() {
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
            "workflow":1,
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
            "workflow":1,
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
          "workflow":1,
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
          "workflow":1,
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
          "workflow":1,
          "node_type":"kill",
          "child_links":[],
          "message":"Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]",
        },{
          "id":5,
          "name":"end",
          "workflow":1,
          "node_type":"end",
          "child_links":[],
        }],
      },
      registry: registry
    });
    return workflow;
  }

  describe("Node APIs", function(){
    var node = null;
    var viewModel = create_three_step_workflow();
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
