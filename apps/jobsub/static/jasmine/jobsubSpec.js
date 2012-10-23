
describe("JobSubModel", function(){
  var viewModel;

  function getSampleDesign(id, canSubmit, canDelete){
    return {
      "url_params":"/fake/params/url/"+id,
      "description":"[Sample] Jasmine Job "+id,
      "last_modified":1350993390 + id,
      "can_delete":canDelete,
      "owner":"jasmine",
      "url_edit":"/fake/edit/url/"+id,
      "url_submit":"/fake/submit/url/"+id,
      "id":id,
      "can_submit":canSubmit,
      "name":"jasmine_job_"+id,
      "url_clone":"/fake/clone/url/"+id,
      "url_delete":"/fake/delete/url/"+id,
      "type":"mapreduce"
    }
  }


  var sampleDesigns = [
    getSampleDesign(1, true, true),
    getSampleDesign(2, false, true),
    getSampleDesign(3, false, false)
  ];

  beforeEach(function(){
    viewModel = new JobSubModel(sampleDesigns);
    ko.applyBindings(viewModel);
  });

  it("should render the design table on applyBindings", function(){
    expect($("#designs tr").length).toEqual(viewModel.designs().length);
  });

  describe("When clicking select all", function(){

    it("should select first all designs and deselect them all", function(){
      viewModel.selectAll();
      expect(viewModel.selectedDesigns().length).toEqual(viewModel.designs().length);
      viewModel.selectAll();
      expect(viewModel.selectedDesigns().length).toEqual(0);
    });

    it("should add a css class to the 'Select All' checkbox", function(){
      viewModel.selectAll();
      expect($("#selectAll").hasClass("icon-ok")).toBeTruthy();
    });

    it("should disable the action buttons", function(){
      viewModel.selectAll();
      expect($(".btn:enabled").length).toEqual(0);
    });

  });

  describe("When selecting a design", function(){

    it("should return a selectedDesign", function(){
      viewModel.designs()[0].selected(true);
      expect(viewModel.selectedDesign().name).toEqual(viewModel.designs()[0].name);
    });

    it("should always enable the clone button", function(){
      viewModel.designs()[0].selected(true);
      expect($(".btn:enabled:contains('Clone')").length).toEqual(1);
      viewModel.designs()[0].selected(false);
      expect($(".btn:enabled:contains('Clone')").length).toEqual(0);
      viewModel.designs()[1].selected(true);
      expect($(".btn:enabled:contains('Clone')").length).toEqual(1);
    });

    it("should enable the submit button if canSubmit is true", function(){
      viewModel.designs()[0].selected(true);
      expect($(".btn:enabled:contains('Submit')").length).toEqual(1);
      viewModel.designs()[0].selected(false);
      viewModel.designs()[1].selected(true);
      expect($(".btn:enabled:contains('Submit')").length).toEqual(0);
    });

    it("should enable the edit button if canSubmit is true", function(){
      viewModel.designs()[0].selected(true);
      expect($(".btn:enabled:contains('Edit')").length).toEqual(1);
      viewModel.designs()[0].selected(false);
      viewModel.designs()[1].selected(true);
      expect($(".btn:enabled:contains('Edit')").length).toEqual(0);
    });

    it("should enable the delete button if canDelete is true", function(){
      viewModel.designs()[1].selected(true);
      expect($(".btn:enabled:contains('Delete')").length).toEqual(1);
      viewModel.designs()[1].selected(false);
      viewModel.designs()[2].selected(true);
      expect($(".btn:enabled:contains('Delete')").length).toEqual(0);
    });

  });
});