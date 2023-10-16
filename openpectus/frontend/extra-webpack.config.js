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
        use: ['style-loader', 'css-loader'],
        include: [
          resolve(__dirname, './node_modules/monaco-editor'),
          resolve(__dirname, './node_modules/vscode'),
        ],
      },
      {
        test: /\.(mp3|wasm|ttf)$/i,
        type: 'asset/resource',
      },
      {
        // This is just so that the msw handlers.ts can import a csv file for batch job csv file download mocking.
        test: /\.csv$/,
        use: 'raw-loader',
      },
    ],
    // this fixes the ttf and wasm url loading issue
    parser: {
      javascript: {
        url: true,
      },
    },
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
