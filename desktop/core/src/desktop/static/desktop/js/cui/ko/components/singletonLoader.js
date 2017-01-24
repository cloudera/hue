import ko            from 'knockout';

let instance = null;

class SingletonLoader {
  constructor() {
    if (!instance) {
      instance = this;

      var $singletonLoader = $('<div>').addClass('cui-singleton-loader');
      $singletonLoader.appendTo(document.body);
    }

    return instance;
  }

  getContainer() {
    return $('.cui-singleton-loader');
  }

  applyBindings() {
    ko.applyBindings({}, this.getContainer()[0]);
  }
}

module.exports = new SingletonLoader();
