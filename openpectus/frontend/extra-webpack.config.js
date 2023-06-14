// solve: __dirname is not defined in ES module scope
import {fileURLToPath} from 'url';
import {dirname, resolve} from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);


const config = {
  module: {
    rules: [
      {
        // adapted from https://github.com/Microsoft/monaco-editor/issues/886#issuecomment-1188678096 and https://github.com/TypeFox/monaco-languageclient-ng-example/blob/main/custom-webpack.config.js
        test: /\.css$/,
        include: [
          resolve(__dirname, './node_modules/monaco-editor'),
          resolve(__dirname, './node_modules/vscode'),
        ],
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
      {
        test: /\.wasm$/,
        type: 'asset/inline',
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
      path: resolve(__dirname, './node_modules/path-browserify'),
    },
  },
  experiments: {
    topLevelAwait: true,
  },
};

export default config;
