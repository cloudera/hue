describe("jHueTableScroller plugin", function () {

  var defaultTableOriginalHeight = 0;
  var minHeightTableOriginalHeight = 0;

  beforeEach(function () {
    jasmine.getFixtures().fixturesPath = 'static/jasmine/';
    loadFixtures('jHueTableScrollerFixture.html');

    defaultTableOriginalHeight = $("#defaultTable").height();
    minHeightTableOriginalHeight = $("#minHeightTable").height();

    $(".table").dataTable({
      "bPaginate":false,
      "bLengthChange":false,
      "bInfo":false
    });
    $(".dataTables_wrapper").jHueTableScroller();
  });

  it("should make the default table scroll with min height enabled", function () {
    expect($("#defaultTable").parent(".dataTables_wrapper").height()).toBeLessThan(defaultTableOriginalHeight);
    expect($("#defaultTable").parent(".dataTables_wrapper").height()).toBe(500);
  });

  it("should set a specific minimum height when data-tablescroller-min-height is specified", function () {
    expect($("#minHeightTable").parent(".dataTables_wrapper").height()).toBeLessThan(minHeightTableOriginalHeight);
    expect($("#minHeightTable").parent(".dataTables_wrapper").height()).toBeGreaterThan($("#defaultTable").parent(".dataTables_wrapper").height());
  });

  it("should disable a minimum height when data-tablescroller-disable-min-height is specified", function () {
    expect($("#disableMinHeightTable").parent(".dataTables_wrapper").height()).not.toEqual(500)
  });

  it("should disable the plugin when data-tablescroller-disable is specified", function () {
    expect($("#disableTable").parent(".dataTables_wrapper").css("overflow-y")).toBe("visible");
  });

});