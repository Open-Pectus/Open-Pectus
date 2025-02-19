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
      // {
      //   test: /editorWorker-es\.js$/,
      //   type: 'asset/resource',
      //   include: [
      //     resolve(__dirname, './node_modules/monaco-editor-wrapper/dist/workers'),
      //   ],
      // },
    ],
    // this is required for loading .wasm (and other) files. For context, see https://stackoverflow.com/a/75252098 and https://github.com/angular/angular-cli/issues/24617
    parser: {
      javascript: {
        url: true,
      },
    },
  },
  resolve: {
    extensions: ['.ts', '.js', '.json', '.ttf'],
    fallback: {vm: false, fs: false, module: false},
  },
  experiments: {
    topLevelAwait: true,
    // outputModule: true,
  },
  // output: {
  //   //   // module: true,
  //   workerChunkLoading: 'import',
  //   environment: {
  //     dynamicImportInWorker: true,
  //   },
  // },
};

export default config;
