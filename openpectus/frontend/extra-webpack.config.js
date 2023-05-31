const path = require('path');
const MONACO_DIR = path.join(__dirname, 'node_modules/monaco-editor');
const VSCODE_DIR = path.join(__dirname, 'node_modules/vscode')

module.exports = {
  module: {
    rules: [
      {
        // adapted from https://github.com/Microsoft/monaco-editor/issues/886#issuecomment-1188678096 and https://github.com/TypeFox/monaco-languageclient-ng-example/blob/main/custom-webpack.config.js
        test: /\.css$/,
        include: [MONACO_DIR, VSCODE_DIR],
        use: ['style-loader', {
          loader: 'css-loader',
          options: {
            url: false,
          },
        }],
      },
      {
        test: /\.(mp3|wasm|ttf)$/i,
        type: 'asset/resource',
      },
    ],
    // this fixes the ttf url loading issue
    // parser: {
    //   javascript: {
    //     url: true,
    //   },
    // },
  },
  resolve: {
    extensions: ['.ts', '.js'],
    fallback: {
      path: require.resolve('path-browserify'),
    },
  },
  experiments: {
    topLevelAwait: true,
  },
};
