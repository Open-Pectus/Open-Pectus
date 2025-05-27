import { WrapperConfig } from 'monaco-editor-wrapper';
import { Logger } from 'monaco-languageclient/tools';
import { useWorkerFactory } from 'monaco-languageclient/workerFactory';
import { LogLevel } from 'vscode';
import { UtilMethods } from '../../shared/util-methods';

export class MonacoWrapperConfig {
  static buildWrapperUserConfig(htmlContainer: HTMLElement, text: string, unitId?: string, isMethodEditor = true): WrapperConfig {
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
            'editor.lineNumbersMinChars': UtilMethods.isMobile ? 1 : 3,
            'editor.minimap': {
              enabled: UtilMethods.isDesktop,
            },
            'editor.lightbulb.enabled': true,
            'editor.experimental.asyncTokenization': true,
            'editor.foldingStrategy': 'indentation',
            'editor.wordBasedSuggestions': false,
            'editor.codeLens': false,
            // "editor.quickSuggestions": false
          }),
        },
      },
      extensions: !isMethodEditor ? [] : [{
        config: {
          name: 'pcode',
          version: '0.0.0',
          publisher: 'openpectus',
          engines: {vscode: '0.10.x'},
          categories: ['Programming Languages'],
          contributes: {
            grammars: [{
              language: 'pcode',
              scopeName: 'source.pcode',
              path: './pcode.tmLanguage.json',
            }],
            languages: [{
              id: 'pcode',
              aliases: ['PCODE', 'pcode'],
              extensions: ['.pcode'],
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
            text,
            fileExt: 'pcode',
          },
        },
        monacoWorkerFactory: this.configureMonacoWorkers,
      },
      languageClientConfigs: {
        'pcode': {
          clientOptions: {
            documentSelector: ['pcode'],
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
