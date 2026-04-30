import { EditorApp } from 'monaco-languageclient/editorApp';
import { MonacoVscodeApiConfig, MonacoVscodeApiWrapper } from 'monaco-languageclient/vscodeApiWrapper';
import { LanguageClientConfig, LanguageClientWrapper } from 'monaco-languageclient/lcwrapper';
import { useWorkerFactory, Worker } from 'monaco-languageclient/workerFactory';

export class MonacoWrapper {
  static isInitialized = false;
  private static apiWrapper?: Promise<MonacoVscodeApiWrapper>;
  private static languageClientWrapper?: Promise<LanguageClientWrapper>;

  static buildEditorApp(fileUriPrefix: string): EditorApp {
    return new EditorApp({
      codeResources: {
        modified: {
          text: '',
          uri: `/workspace/${fileUriPrefix}/${crypto.randomUUID()}.pcode`,
        },
      },
    });
  }

  static buildVsCodeApi(languageId: string, unitId?: string): Promise<MonacoVscodeApiWrapper> {
    if(MonacoWrapper.apiWrapper !== undefined) return MonacoWrapper.apiWrapper;
    const config: MonacoVscodeApiConfig = {
      $type: 'extended' as const,
      viewsConfig: {
        $type: 'EditorService'
      },
      // advanced: {
      //   enableExtHostWorker: true,
      // },
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
          'editor.wordBasedSuggestions': 'off',
          'editor.codeLens': false,
          'scm.diffDecorations': 'none',
          'editor.lineDecorationsWidth': 12,
          'workbench.activityBar.visible': false,
          'editor.renderLineHighlightOnlyWhenFocus': true,
          'editor.folding': false,
          'editor.scrollBeyondLastColumn': 1,
          'editor.scrollBeyondLastLine': false,
          'editor.stickyScroll.enabled': false,
          'editor.suggest.preview': true,
        }),
      },
      monacoWorkerFactory: MonacoWrapper.configureMonacoWorkers,
      // monacoWorkerFactory: configureDefaultWorkerFactory,
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
              extensions: ['pcode'],
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
    };
    const apiWrapper = new MonacoVscodeApiWrapper(config);
    MonacoWrapper.apiWrapper = apiWrapper.start().then(() => apiWrapper);
    return MonacoWrapper.apiWrapper;
  }

  static buildLanguageClient(languageId: string, unitId?: string): Promise<LanguageClientWrapper> {
    if(MonacoWrapper.languageClientWrapper !== undefined) return MonacoWrapper.languageClientWrapper;
    const config: LanguageClientConfig = {
      languageId: languageId,
      // automaticallyInit: false,
      // automaticallyStart: false,
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
    };
    const apiWrapper = new LanguageClientWrapper(config);
    MonacoWrapper.languageClientWrapper = apiWrapper.start().then(() => apiWrapper);
    return MonacoWrapper.languageClientWrapper;
  }

  // adapted from https://github.com/TypeFox/monaco-languageclient/blob/70f92b740a06f56210f91464d694b5e5d4dc87db/packages/examples/src/common/client/utils.ts
  // later based on node_modules/monaco-languageclient/src/worker/index.ts
  private static configureMonacoWorkers(logger: any) { // any because I can't import the interface
    useWorkerFactory({
      workerLoaders: {
        'TextMateWorker': () => new Worker('/assets/monaco-workers/textmate.js', {type: 'module'}),
        'editorWorkerService': () => new Worker('/assets/monaco-workers/editorService.js', {type: 'module'}),
        // 'extensionHostWorkerMain': () => new Worker('/assets/monaco-workers/extensionHost.js', {type: 'module'}),
        OutputLinkDetectionWorker: undefined,
        LanguageDetectionWorker: undefined,
        NotebookEditorWorker: undefined,
        LocalFileSearchWorker: undefined,
      },
      logger,
    });
  };
}
