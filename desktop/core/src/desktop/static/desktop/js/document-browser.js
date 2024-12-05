(function () {
  if (ko.options) {
    ko.options.deferUpdates = true;
  }

  $(document).ready(function () {
    var options = {
      user: 'admin',
      superuser: 'True' === 'True',
      i18n: {
        errorFetchingTableDetails: 'An error occurred fetching the table details. Please try again.',
        errorFetchingTableFields: 'An error occurred fetching the table fields. Please try again.',
        errorFetchingTableSample: 'An error occurred fetching the table sample. Please try again.',
        errorRefreshingTableStats: 'An error occurred refreshing the table stats. Please try again.',
        errorLoadingDatabases: 'There was a problem loading the databases. Please try again.',
        errorLoadingTablePreview: 'There was a problem loading the table preview. Please try again.'
      }
    };

    var viewModel = new HomeViewModel(options);

    var loadUrlParam = function () {
      if (window.location.pathname.indexOf('/home') > -1) {
        if (hueUtils.getParameter('uuid')) {
          viewModel.openUuid(hueUtils.getParameter('uuid'));
        } else if (hueUtils.getParameter('path')) {
          viewModel.openPath(hueUtils.getParameter('path'));
        } else if (viewModel.activeEntry() && viewModel.activeEntry().loaded()) {
          var rootEntry = viewModel.activeEntry();
          while (rootEntry && !rootEntry.isRoot()) {
            rootEntry = rootEntry.parent;
          }
          viewModel.activeEntry(rootEntry);
        } else {
          viewModel.activeEntry().load(function () {
            if (viewModel.activeEntry().entries().length === 1 && viewModel.activeEntry().entries()[0].definition().type === 'directory') {
              viewModel.activeEntry(viewModel.activeEntry().entries()[0]);
              viewModel.activeEntry().load();
            }
          });
        }
      }
    };
    window.onpopstate = loadUrlParam;
    loadUrlParam();

    viewModel.activeEntry.subscribe(function (newEntry) {
      var filterType = window.location.pathname.indexOf('/home') > -1 && hueUtils.getParameter('type') != '' ? 'type=' + hueUtils.getParameter('type') : '';
      if (typeof newEntry !== 'undefined' && newEntry.definition().uuid && !newEntry.isRoot()) {
        if (hueUtils.getParameter('uuid') === '' || hueUtils.getParameter('uuid') !== newEntry.definition().uuid){
          hueUtils.changeURL('/hue/home/?uuid=' + newEntry.definition().uuid + '&' + filterType);
        }
      } else if (typeof newEntry === 'undefined' || newEntry.isRoot()) {
        var url = '/hue/home/' + (filterType ? '?' + filterType : '');
        if (window.location.pathname + window.location.search !== url) {
          hueUtils.changeURL(url);
        }
      }
    });

    ko.applyBindings(viewModel, $('#homeComponents')[0]);
  });
})();