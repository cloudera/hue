
module.exports = {
  devtool: 'source-map',
  mode: 'development',
  resolve: {
    extensions: ['.json', '.jsx', '.js', '.tsx', '.ts'],
    modules: ['node_modules', 'js']
  },
  entry: {
    app: ['./src/app.js']
  },
  optimization: {
    minimize: false,
  },
  output: {
    path: __dirname + '/dist/',
    filename: '[name].js'
  },
  module: {
    rules: [
      {
        test: /\.(ts|js)x?$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
        options: {
          presets: ['@babel/preset-env', '@babel/preset-typescript'],
          plugins: ['@babel/proposal-class-properties', '@babel/proposal-object-rest-spread']
        }
      }
    ]
  },
  plugins: []
};
