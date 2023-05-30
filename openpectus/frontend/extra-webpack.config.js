// const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin');

const path = require('path');
const MONACO_DIR = path.join(__dirname, 'node_modules/monaco-editor');

module.exports = {
  // plugins: [new MonacoWebpackPlugin()],
  module: {
    rules: [
      {
        // adapted from https://github.com/Microsoft/monaco-editor/issues/886#issuecomment-1188678096
        test: /\.css$/,
        include: MONACO_DIR,
        use: ['style-loader', {
          loader: 'css-loader',
          options: {
            url: false,
          },
        }],
      },
    ],
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
