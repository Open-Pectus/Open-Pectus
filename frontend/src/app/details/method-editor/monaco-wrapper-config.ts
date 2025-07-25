import { WrapperConfig } from 'monaco-editor-wrapper';
import { Logger } from 'monaco-languageclient/tools';
import { useWorkerFactory } from 'monaco-languageclient/workerFactory';
import { LogLevel } from 'vscode';

export class MonacoWrapperConfig {
  static isInitialized = false;

  static buildWrapperConfig(htmlContainer: HTMLElement, unitId?: string): WrapperConfig {
    const isInitialized = MonacoWrapperConfig.isInitialized;
    MonacoWrapperConfig.isInitialized = true;

    // These two variables exist to help keep track of what should match and what is unrelated, even though their value is identical.
    const languageId = 'pcode';
    const extension = 'pcode';

    const specificConfig = {
      $type: 'extended' as const,
      htmlContainer,
      logLevel: LogLevel.Warning,
      editorAppConfig: {
        codeResources: {
          modified: {
            text: '',
            uri: `/workspace/${crypto.randomUUID()}.pcode`,
          },
        },
        monacoWorkerFactory: this.configureMonacoWorkers,
      },
    } satisfies WrapperConfig;

    if(isInitialized) return specificConfig;

    // if multiple editors are on screen, only one of those should initialize this
    const sharedConfig = {
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
            'editor.wordBasedSuggestions': "off",
            'editor.codeLens': false,
            'scm.diffDecorations': 'none',
            'editor.lineDecorationsWidth': 12,
            'workbench.activityBar.visible': false,
            'editor.renderLineHighlightOnlyWhenFocus': true,
            'editor.folding': false,
            'editor.scrollBeyondLastColumn': 1,
            'editor.scrollBeyondLastLine': false,
            'editor.stickyScroll.enabled': false,
            "editor.suggest.preview": true,
          }),
        },
      },
      extensions: [{
        config: {
          name: 'pcode',
          version: '0.0.0',
          publisher: 'openpectus',
          engines: {vscode: '0.10.x'},
          categories: ['Programming Languages'],
          contributes: {
            // no grammar for recent run where there's no unitId and no url to get the tmLanguage.json from
            grammars: unitId === undefined ? [] : [{
              language: languageId,
              scopeName: 'source.pcode',
              path: './pcode.tmLanguage.json',
            }],
            languages: [{
              id: languageId,
              aliases: ['PCODE', 'pcode'],
              extensions: [extension],
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
      languageClientConfigs: {
        automaticallyInit: false,
        automaticallyStart: false,
        configs: {
          'pcode': {
            clientOptions: {
              documentSelector: [languageId],
              initializationOptions: {
                engineId: unitId,
              },
            },
            connection: {
              options: {
                $type: 'WebSocketUrl',
                url: `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/api/lsp/websocket`,
                // startOptions: { onCall: () => { console.log('Connected to socket.'); }, reportStatus: false,},
                // stopOptions: { onCall: () => { console.log('Disconnected from socket.'); }, reportStatus: false, },
              },
            },
          },
        },
      },
    } satisfies Partial<WrapperConfig>;

    return {...specificConfig, ...sharedConfig};
  };

  // adapted from https://github.com/TypeFox/monaco-languageclient/blob/70f92b740a06f56210f91464d694b5e5d4dc87db/packages/examples/src/common/client/utils.ts
  static configureMonacoWorkers(logger?: Logger) {
    useWorkerFactory({
      workerLoaders: {
        'TextEditorWorker': () => new Worker('/assets/monaco-workers/editor.js', {type: 'module'}),
        'TextMateWorker': () => new Worker('/assets/monaco-workers/textmate.js', {type: 'module'}),
        // 'editorWorkerService': () => new Worker('/assets/monaco-workers/editorService.js', {type: 'module'}),
        OutputLinkDetectionWorker: undefined,
        LanguageDetectionWorker: undefined,
        NotebookEditorWorker: undefined,
        LocalFileSearchWorker: undefined,
      },
      logger,
    });
  };
}
