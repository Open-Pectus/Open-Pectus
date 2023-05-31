import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, Input, OnDestroy, ViewChild } from '@angular/core';
import { Store } from '@ngrx/store';
import { editor as MonacoEditor, languages, Range, Uri } from 'monaco-editor';
import { buildWorkerDefinition } from 'monaco-editor-workers';
import { initServices, MonacoLanguageClient } from 'monaco-languageclient';
import { Observable, Subject, take, takeUntil } from 'rxjs';
import { CloseAction, ErrorAction, MessageTransports } from 'vscode-languageclient/lib/common/client';
import { toSocket, WebSocketMessageReader, WebSocketMessageWriter } from 'vscode-ws-jsonrpc';
import { createConfiguredEditor, createModelReference } from 'vscode/monaco';
import { DetailsActions } from '../ngrx/details.actions';

buildWorkerDefinition('./assets/monaco-editor-workers/workers', window.location.origin, false);

@Component({
  selector: 'app-monaco-editor',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div #editor class="w-full h-full"></div>
  `,
  styleUrls: ['monaco-editor.component.scss'],
})
export class MonacoEditorComponent implements AfterViewInit, OnDestroy {
  @Input() editorSizeChange?: Observable<void>;
  @ViewChild('editor', {static: true}) editorElement!: ElementRef<HTMLDivElement>;
  private componentDestroyed = new Subject<void>();
  private editor?: MonacoEditor.IStandaloneCodeEditor;
  private initDone = false;
  private readonly languageId = 'json';

  constructor(private store: Store) {}

  async ngAfterViewInit() {
    await this.initServices();
    this.registerLanguages();
    this.editor = await this.createEditor();
    this.setupWebSocket(`ws://localhost:3000/sampleServer`);

    this.editorSizeChange?.pipe(takeUntil(this.componentDestroyed)).subscribe(() => this.editor?.layout());
    window.onresize = () => this.editor?.layout();
    this.store.dispatch(DetailsActions.methodEditorInitialized({model: this.editor.getModel()?.getValue() ?? ''}));
  }

  createLanguageClient(transports: MessageTransports): MonacoLanguageClient {
    return new MonacoLanguageClient({
      name: 'Sample Language Client',
      clientOptions: {
        // use a language id as a document selector
        documentSelector: [this.languageId],
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

  ngOnDestroy() {
    this.componentDestroyed.next();
  }

  private setupWebSocket(url: string) {
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
      this.componentDestroyed.pipe(take(1)).subscribe(() => {
        setTimeout(() => languageClient.stop().then(), 100);
      });
      reader.onClose(() => languageClient.stop());
    };
  }

  private registerLanguages() {
    languages.register({
      id: this.languageId,
      extensions: ['.json', '.jsonc'],
      aliases: ['JSON', 'json'],
      mimetypes: ['application/json'],
    });
  }

  private async createEditor() {
    const uri = Uri.parse('/tmp/model.json');
    const modelRef = await createModelReference(uri, this.createDefaultJsonContent());
    modelRef.object.setLanguageId(this.languageId);
    const injectedLines: number[] = [3, 5];

    // const editor = MonacoEditor.create(this.editorElement.nativeElement, {
    //   model: MonacoEditor.createModel(this.createDefaultJsonContent(), 'json', Uri.parse('inmemory://model.json')),
    //   fontSize: 20,
    //   lineNumbers: this.getLineNumberFunction(injectedLines),
    // });

    const editor = createConfiguredEditor(this.editorElement.nativeElement, {
      model: modelRef.object.textEditorModel,
      fontSize: 20,
      lineNumbers: this.getLineNumberFunction(injectedLines),
    });

    editor.onDidChangeModelContent(() => {
      const model = editor.getModel()?.getValue();
      if(model === undefined) return;
      this.store.dispatch(DetailsActions.methodEditorModelChanged({model}));
    });

    this.componentDestroyed.pipe(take(1)).subscribe(() => {
      editor.getModel()?.dispose();
      editor.dispose();
    });

    this.decorateInjectedLines(injectedLines, editor);

    return editor;
  }

  private getLineNumberFunction(injectedLines: number[]) {
    return (lineNumber: number) => {
      if(injectedLines.includes(lineNumber)) return '';
      const injectedLinesBeforeThis = injectedLines.filter(injectedLineNumber => injectedLineNumber < lineNumber);
      const lineNumberWithoutInjectedLines = lineNumber - injectedLinesBeforeThis.length;
      return lineNumberWithoutInjectedLines.toString();
    };
  }

  private decorateInjectedLines(injectedLines: number[], editor: MonacoEditor.IStandaloneCodeEditor) {
    const decorationIds: string[] = [];
    injectedLines.forEach(lineNumber => {
      const decorationId = editor.deltaDecorations([], [
        {
          range: new Range(lineNumber, 0, lineNumber, 0),
          options: {
            // after: {content: 'fdas'},
            // before: {content: 'dfsa'},
            className: 'injectedLine',
            isWholeLine: true,
            hoverMessage: {value: 'This line has been injected and is not part of the method.'},
          },
        },
        {
          range: new Range(lineNumber, 0, lineNumber, 0),
          options: {
            linesDecorationsClassName: 'codicon-export codicon',
          },
        },
      ]);
      decorationIds.push(...decorationId);
    });

    // console.log(decorationIds);
    // editor.removeDecorations([decorationIds[1]]);
  }

  private createDefaultJsonContent() {
    return `{
  "some key": "some value",
  "injected": "line",
  "another key": "another value",
  "another injected": "line"
}`;
  }

  private async initServices() {
    if(!this.initDone) {
      await initServices({
        enableThemeService: true,
        enableModelEditorService: true,
        modelEditorServiceConfig: {
          useDefaultFunction: true,
        },

        debugLogging: true,
      });
      this.initDone = true;
    }
  }
}
