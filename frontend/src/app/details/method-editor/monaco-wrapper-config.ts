import { WrapperConfig } from 'monaco-editor-wrapper';
import { Logger } from 'monaco-languageclient/tools';
import { useWorkerFactory } from 'monaco-languageclient/workerFactory';
import { LogLevel } from 'vscode';

export class MonacoWrapperConfig {
  static buildWrapperConfig(htmlContainer: HTMLElement, text?: string, unitId?: string): WrapperConfig {
    const uuid = crypto.randomUUID();
    return {
      $type: 'extended',
      htmlContainer,
      logLevel: LogLevel.Warning,
      vscodeApiConfig: {
        // vscodeApiInitPerformExternally: true,
        // enableExtHostWorker: true,
        userConfiguration: {
          json: JSON.stringify({
            'editor.fontSize': 18,
            'editor.glyphMargin': false,
            'editor.fixedOverflowWidgets': true,
            'editor.lineNumbersMinChars': 1,
            'editor.minimap.enabled': false,
            'editor.lightbulb.enabled': true,
            'editor.experimental.asyncTokenization': true,
            'editor.foldingStrategy': 'indentation',
            'editor.wordBasedSuggestions': false,
            'editor.codeLens': false,
            'scm.diffDecorations': 'none',
            'editor.lineDecorationsWidth': 12,
            'workbench.activityBar.visible': false,
            'editor.renderLineHighlightOnlyWhenFocus': true,
            'editor.folding': false,
            'editor.scrollBeyondLastColumn': 1,
            'editor.scrollBeyondLastLine': false,
            // "editor.quickSuggestions": false
          }),
        },
      },
      // Only one editor should initialize the extensions, otherwise we get an error.
      // Currently, there's always only one method editor on screen, and possible other editors which are not a method editor.
      extensions: [{
        config: {
          name: `${uuid}pcode`,
          version: '0.0.0',
          publisher: 'openpectus',
          engines: {vscode: '0.10.x'},
          categories: ['Programming Languages'],
          contributes: {
            grammars: [{
              language: `${uuid}pcode`,
              scopeName: 'source.pcode',
              path: './pcode.tmLanguage.json',
            }],
            languages: [{
              id: `${uuid}pcode`,
              aliases: ['PCODE', 'pcode'],
              extensions: [`${uuid}pcode`],
              mimetypes: ['application/pcode'],
              configuration: './pcode.language-configuration.json',
            }],
          },
        },
        filesOrContents: new Map<string, string | URL>([
          ['./pcode.language-configuration.json', new URL(`/api/lsp/pcode.language-configuration.json`, window.location.origin)],
          ['./pcode.tmLanguage.json', new URL(`/api/lsp/engine/${unitId}/pcode.tmLanguage.json`, window.location.origin)],
        ]),
      }],
      editorAppConfig: {
        codeResources: {
          modified: {
            text: text ?? '',
            fileExt: `${uuid}pcode`,
          },
        },
        monacoWorkerFactory: this.configureMonacoWorkers,
      },
      languageClientConfigs: {
        [`${uuid}pcode`]: {
          clientOptions: {
            documentSelector: [`${uuid}pcode`],
            initializationOptions: {
              engineId: unitId,
            },
          },
          connection: {
            options: {
              $type: 'WebSocketUrl',
              url: `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/api/lsp/websocket`,
              // startOptions: {
              //   onCall: () => {
              //     console.log('Connected to socket.');
              //   },
              //   reportStatus: false,
              // },
              // stopOptions: {
              //   onCall: () => {
              //     console.log('Disconnected from socket.');
              //   },
              //   reportStatus: false,
              // },
            },
          },
        },
      },
    } satisfies WrapperConfig;
  };

  // adapted from https://github.com/TypeFox/monaco-languageclient/blob/70f92b740a06f56210f91464d694b5e5d4dc87db/packages/examples/src/common/client/utils.ts
  static configureMonacoWorkers(logger?: Logger) {
    useWorkerFactory({
      workerLoaders: {
        'TextEditorWorker': () => new Worker('/assets/monaco-workers/editor.js', {type: 'module'}),
        'editorWorkerService': () => new Worker('/assets/monaco-workers/editorService.js', {type: 'module'}),
        'TextMateWorker': () => new Worker('/assets/monaco-workers/textmate.js', {type: 'module'}),
        OutputLinkDetectionWorker: undefined,
        LanguageDetectionWorker: undefined,
        NotebookEditorWorker: undefined,
        LocalFileSearchWorker: undefined,
      },
      logger,
    });
  };
}
