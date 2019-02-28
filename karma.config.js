module.exports = function(config) {
  config.set({
    basePath: 'desktop/core/src/desktop/js',
    frameworks: ['jasmine'],
    files: ['**/spec/*[sS]pec.js'],
    preprocessors: {
      '**/spec/*[sS]pec.js': ['webpack']
    },
    reporters: ['progress'],
    port: 9876,
    colors: true,
    logLevel: config.LOG_ERROR,
    autoWatch: true,
    browsers: ['ChromeHeadless'], // 'Chrome'
    singleRun: false,
    webpack: {
      module: {
        rules: [
          {
            test: /\.js$/i,
            exclude:/(node_modules)/,
            loader:'babel-loader',
            options: {
              presets:['@babel/preset-env']
            }
          }
        ]
      }
    },
    webpackMiddleware: {
      noInfo: true,
      stats: 'errors-only'
    }
  })
};
