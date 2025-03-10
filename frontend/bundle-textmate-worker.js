// solve: __dirname is not defined in ES module scope
import {fileURLToPath} from 'url';
import {dirname, resolve} from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export default {
  entry: './node_modules/@codingame/monaco-vscode-textmate-service-override/worker.js',
  output: {
    filename: 'textmate.worker.js',
    path: resolve(__dirname, './src/assets/monaco-workers'),
    chunkLoading: false, // if this is true, webpack will produce code trying to access global `document` variable, which will fail at runtime due to this being a web worker
  },
  mode: 'production',
  performance: {
    hints: false,
  },
};
