// solve: __dirname is not defined in ES module scope
import {fileURLToPath} from 'url';
import {dirname, resolve} from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// paths now based on node_modules/monaco-languageclient/src/worker/index.ts
export default {
  entry: {
    textmate: './node_modules/@codingame/monaco-vscode-textmate-service-override/worker',
    editorService: './node_modules/@codingame/monaco-vscode-editor-api/esm/vs/editor/editor.worker.js',
    // extensionHost: './node_modules/@codingame/monaco-vscode-api/workers/extensionHost.worker'
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
