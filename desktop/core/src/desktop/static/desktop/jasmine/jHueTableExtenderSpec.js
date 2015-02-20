describe("jHueTableExtender plugin", function () {

  beforeEach(function () {
    jasmine.getFixtures().fixturesPath = 'static/jasmine/';
    loadFixtures('jHueTableExtenderFixture.html');
    $(".resultTable").dataTable({
      "bPaginate":false,
      "bLengthChange":false,
      "bInfo":false
    });
    $(".resultTable").jHueTableExtender({
      fixedHeader:true,
      firstColumnTooltip:true
    });
  });

  it("should create the hidden navigator element", function () {
    expect($("#jHueTableExtenderNavigator")).toExist();
    expect($("#jHueTableExtenderNavigator")).toBeHidden();
  });

});