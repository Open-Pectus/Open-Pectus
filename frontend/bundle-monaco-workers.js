// solve: __dirname is not defined in ES module scope
import {fileURLToPath} from 'url';
import {dirname, resolve} from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export default {
  entry: {
    editor: './node_modules/@codingame/monaco-vscode-editor-api/esm/vs/editor/editor.worker.js',
    textmate: './node_modules/@codingame/monaco-vscode-textmate-service-override/worker.js',
  },
  output: {
    filename: '[name].js',
    path: resolve(__dirname, './src/assets/monaco-workers'),
    chunkLoading: false, // if this is true (default), webpack will produce code trying to access global `document` variable for the textmate worker, which will fail at runtime due to being a worker
  },
  mode: 'production',
  performance: {
    hints: false,
  },
};
