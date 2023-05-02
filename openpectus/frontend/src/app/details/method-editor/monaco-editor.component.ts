import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, ViewChild } from '@angular/core';
import { editor as MonacoEditor, languages, Range, Uri } from 'monaco-editor';
import { buildWorkerDefinition } from 'monaco-editor-workers';
import { MonacoLanguageClient, MonacoServices } from 'monaco-languageclient';
import { CloseAction, ErrorAction, MessageTransports } from 'vscode-languageclient/lib/common/client';
import { toSocket, WebSocketMessageReader, WebSocketMessageWriter } from 'vscode-ws-jsonrpc';
import getDialogsServiceOverride from 'vscode/service-override/dialogs';
import getNotificationServiceOverride from 'vscode/service-override/notifications';
import { StandaloneServices } from 'vscode/services';

StandaloneServices.initialize({
  ...getNotificationServiceOverride(),
  ...getDialogsServiceOverride(),
});

buildWorkerDefinition('./assets/monaco-editor-workers/workers', window.location.origin, false);

@Component({
  selector: 'app-monaco-editor',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div #editor class="w-full h-full"></div>
  `,
})
export class MonacoEditorComponent implements AfterViewInit {
  @ViewChild('editor', {static: true}) editorElement!: ElementRef<HTMLDivElement>;

  ngAfterViewInit() {
    this.registerLanguages();
    this.createEditor();
    this.setupMonacoLanguageClient();
  }

  setupMonacoLanguageClient() {
    // install Monaco language client services
    MonacoServices.install();

    // create the web socket
    const url = `ws://localhost:3000/sampleServer`;
    const webSocket = new WebSocket(url);

    webSocket.onopen = () => {
      const socket = toSocket(webSocket);
      const reader = new WebSocketMessageReader(socket);
      const writer = new WebSocketMessageWriter(socket);
      const languageClient = this.createLanguageClient({
        reader,
        writer,
      });
      languageClient.start().then();
      reader.onClose(() => languageClient.stop());
    };
  }

  createLanguageClient(transports: MessageTransports): MonacoLanguageClient {
    return new MonacoLanguageClient({
      name: 'Sample Language Client',
      clientOptions: {
        // use a language id as a document selector
        documentSelector: ['json'],
        // disable the default error handler
        errorHandler: {
          error: () => ({action: ErrorAction.Continue}),
          closed: () => ({action: CloseAction.DoNotRestart}),
        },
      },
      // create a language client connection from the JSON RPC connection on demand
      connectionProvider: {
        get: () => {
          return Promise.resolve(transports);
        },
      },
    });
  }

  private registerLanguages() {
    languages.register({
      id: 'json',
      extensions: ['.json', '.jsonc'],
      aliases: ['JSON', 'json'],
      mimetypes: ['application/json'],
    });
  }

  private createEditor() {
    const modelValue = `{
  "some key": "some value",
  "injected": "line",
  "another key": "another value",
  "another injected": "line"
}`;

    const injectedLines: number[] = [3, 5];
    const lineNumberFn = (lineNumber: number) => {
      if(injectedLines.includes(lineNumber)) return '';
      const injectedLinesBeforeThis = injectedLines.filter(injectedLineNumber => injectedLineNumber < lineNumber);
      const lineNumberWithoutInjectedLines = lineNumber - injectedLinesBeforeThis.length;
      return lineNumberWithoutInjectedLines.toString();
    };

    const editor = MonacoEditor.create(this.editorElement.nativeElement, {
      model: MonacoEditor.createModel(modelValue, 'json', Uri.parse('inmemory://model.json')),
      fontSize: 20,
      lineNumbers: lineNumberFn,
    });

    const decorationIds: string[] = [];
    injectedLines.forEach(lineNumber => {
      const decorationId = editor.deltaDecorations([], [
        {
          range: new Range(lineNumber, 0, lineNumber, 0),
          options: {
            // after: {content: 'fdas'},
            before: {content: 'dfsa'},
            className: 'injectedLine',
            isWholeLine: true,
            hoverMessage: {value: 'This line has been injected and is not part of the method.'},
          },
        },
        {
          range: new Range(lineNumber, 0, lineNumber, 0),
          options: {
            linesDecorationsClassName: 'codicon-export codicon flex items-center justify-center',
          },
        },
      ]);
      decorationIds.push(...decorationId);
    });

    console.log(decorationIds);
    // editor.removeDecorations([decorationIds[1]]);
  }
}
