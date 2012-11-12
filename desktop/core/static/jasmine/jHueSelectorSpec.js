describe("jHueSelector plugin", function () {

  beforeEach(function () {
    jasmine.getFixtures().fixturesPath = 'static/jasmine/';
    loadFixtures('jHueSelectorFixture.html');
    $("#sampleList").jHueSelector();
  });

  it("should hide the original element", function () {
    expect($("#sampleList")).toBeHidden();
  });

});