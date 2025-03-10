// solve: __dirname is not defined in ES module scope
import {fileURLToPath} from 'url';
import {dirname, resolve} from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export default {
  entry: './node_modules/@codingame/monaco-vscode-editor-api/esm/vs/editor/editor.worker.js',
  output: {
    filename: 'editor.worker.js',
    path: resolve(__dirname, './src/assets/monaco-workers'),
  },
  mode: 'production',
  performance: {
    hints: false,
  },
};
