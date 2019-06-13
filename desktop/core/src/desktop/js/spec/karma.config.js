module.exports = function(config) {
  config.set({
    basePath: '../',
    frameworks: ['jasmine-ajax', 'jasmine'],
    files: ['**/spec/*[sS]pec.js'],
    preprocessors: {
      '**/spec/*[sS]pec.js': ['webpack']
    },
    reporters: ['spec'],
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
            exclude: /(node_modules)/,
            loader: 'babel-loader',
            options: {
              presets: ['@babel/preset-env']
            }
          },
          { type: 'javascript/auto', include: /\.json$/, loaders: ['json-loader'] }
        ]
      }
    },
    webpackMiddleware: {
      noInfo: true,
      stats: 'errors-only'
    }
  });
};
