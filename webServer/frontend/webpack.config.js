var path = require('path');
module.exports = {
  
  entry: path.resolve(__dirname, './app/main.ts'),
  output: {
    path: path.resolve(__dirname, 'dist/'),
    filename:  "bundle.js"
  },
  module: {
    loaders: [
      { test: /\.ts$/,   use: ['awesome-typescript-loader', 'angular2-template-loader'] },
      { test: /\.html$/, use: 'raw-loader' },
      { test: /\.css$/,  use: 'raw-loader' },
      { test: /\.json$/, use: 'json-loader' }
    ]
  },
  resolve: {
    // you can now require('file') instead of require('file.coffee')
    extensions: ['*', '.ts', '.js', '.json', '.html'] 
  }

};
