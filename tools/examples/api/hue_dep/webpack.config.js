
module.exports = {
  devtool: 'source-map',
  mode: 'development',
  resolve: {
    extensions: ['.json', '.jsx', '.js'],
    modules: [
      'node_modules',
      'js'
    ]
  },
  entry: {
    app: ['./src/app.js']
  },
  optimization: {
    minimize: false,
  },
  output: {
    path:  __dirname + '/dist/',
    filename: '[name].js'
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: 'babel-loader'
      }
    ]
  },
  plugins: []
};
