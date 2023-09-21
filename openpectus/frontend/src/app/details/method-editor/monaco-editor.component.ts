import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, Input, OnDestroy, ViewChild } from '@angular/core';
import { Store } from '@ngrx/store';
import { buildWorkerDefinition } from 'monaco-editor-workers';
import { editor as MonacoEditor, languages, Range, Uri } from 'monaco-editor/esm/vs/editor/editor.api.js'; // importing as 'monaco-editor' causes issues: https://github.com/CodinGame/monaco-vscode-api/issues/162
import { initServices, MonacoLanguageClient } from 'monaco-languageclient';
import { firstValueFrom, Observable, Subject, take, takeUntil } from 'rxjs';
import { CloseAction, ErrorAction, MessageTransports } from 'vscode-languageclient/lib/common/client';
import { toSocket, WebSocketMessageReader, WebSocketMessageWriter } from 'vscode-ws-jsonrpc';
import 'vscode/default-extensions/json';
import 'vscode/default-extensions/theme-defaults';
import { createConfiguredEditor, createModelReference } from 'vscode/monaco';
import { UtilMethods } from '../../shared/util-methods';
import { MethodEditorActions } from './ngrx/method-editor.actions';
import { MethodEditorSelectors } from './ngrx/method-editor.selectors';

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
  private readonly languageId = 'json';
  private methodEditorContent = this.store.select(MethodEditorSelectors.content);
  private monacoServicesInitialized = this.store.select(MethodEditorSelectors.monacoServicesInitialized);

  constructor(private store: Store) {}

  async ngAfterViewInit() {
    await this.initServices();
    this.registerLanguages();
    this.editor = await this.createEditor();
    this.setupWebSocket(`ws://localhost:3000/sampleServer`);

    this.editorSizeChange?.pipe(takeUntil(this.componentDestroyed)).subscribe(() => this.editor?.layout());
    window.onresize = () => this.editor?.layout();
    this.store.dispatch(MethodEditorActions.monacoEditorComponentInitialized());
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
    this.store.dispatch(MethodEditorActions.monacoEditorComponentDestroyed());
  }

  private async initServices() {
    const alreadyInitialized = await firstValueFrom(this.monacoServicesInitialized);
    if(alreadyInitialized) return;
    await initServices({
      enableTextmateService: true,
      enableThemeService: true,
      enableModelService: true,
      enableLanguagesService: true,
      debugLogging: false,
    });
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
    const modelRef = await createModelReference(uri, await firstValueFrom(this.methodEditorContent));
    modelRef.object.setLanguageId(this.languageId);

    const editor = createConfiguredEditor(this.editorElement.nativeElement, {
      model: modelRef.object.textEditorModel,
      fontSize: 18,
      glyphMargin: false,
      fixedOverflowWidgets: true,
    });

    editor.onDidChangeModelContent(() => {
      const model = editor.getModel()?.getValue();
      if(model === undefined) return;
      this.store.dispatch(MethodEditorActions.modelChanged({model}));
    });

    this.componentDestroyed.pipe(take(1)).subscribe(() => {
      modelRef.object.dispose();
      modelRef.dispose();
      editor.dispose();
    });

    this.setupInjectedLines(editor);
    this.setupLockedLines(editor);

    return editor;
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

  private getLineNumberFunction(injectedLines: number[]) {
    return (lineNumber: number) => {
      if(injectedLines.includes(lineNumber)) return '';
      const injectedLinesBeforeThis = injectedLines.filter(injectedLineNumber => injectedLineNumber < lineNumber);
      const lineNumberWithoutInjectedLines = lineNumber - injectedLinesBeforeThis.length;
      return lineNumberWithoutInjectedLines.toString();
    };
  }

  private setupLockedLines(editor: MonacoEditor.IStandaloneCodeEditor) {
    const decorations = this.decorateLockedLines(editor);
    this.lockLinesViaReadOnlyEditor(editor, decorations);
  }

  private lockLinesViaReadOnlyEditor(editor: MonacoEditor.IStandaloneCodeEditor, decorations: MonacoEditor.IEditorDecorationsCollection) {
    editor.onDidChangeCursorSelection(_ => {
      const selectionInLockedRange = editor.getSelections()?.some(selection => {
        return decorations.getRanges()
          .flatMap(range => UtilMethods.getNumberRange(range.startLineNumber, range.endLineNumber))
          .some(lockedLineNumber => {
            return selection.intersectRanges(new Range(lockedLineNumber, 0, lockedLineNumber + 1, 0));
          });
      });
      editor.updateOptions({readOnly: selectionInLockedRange, readOnlyMessage: {value: 'Cannot edit lines already executed.'}});
    });
  }

  private decorateLockedLines(editor: MonacoEditor.IStandaloneCodeEditor) {
    const lockedLinesDecorationsCollection = editor.createDecorationsCollection();
    this.store.select(MethodEditorSelectors.lockedLines).pipe(takeUntil(this.componentDestroyed)).subscribe(lockedLineNumbers => {
      const lockedLinesDecorations = lockedLineNumbers.map<MonacoEditor.IModelDeltaDecoration>(lockedLineNumber => {
        return {
          range: new Range(lockedLineNumber, 0, lockedLineNumber, Number.MAX_VALUE),
          options: {
            isWholeLine: true,
            className: 'locked-line',
            hoverMessage: {value: 'This line has been executed and is no longer editable.'},
            shouldFillLineOnLineBreak: false,
          },
        };
      });
      lockedLinesDecorationsCollection.set(lockedLinesDecorations);
    });
    return lockedLinesDecorationsCollection;
  }

  private decorateInjectedLines(editor: MonacoEditor.IStandaloneCodeEditor) {
    const injectedLinesDecorationCollection = editor.createDecorationsCollection();
    this.store.select(MethodEditorSelectors.injectedLines).pipe(takeUntil(this.componentDestroyed)).subscribe(injectedLineNumbers => {
      const injectedLinesDecorations = injectedLineNumbers.map<MonacoEditor.IModelDeltaDecoration>(lineNumber => {
        return {
          range: new Range(lineNumber, 0, lineNumber, Number.MAX_VALUE),
          options: {
            className: 'injectedLine',
            isWholeLine: true,
            hoverMessage: {value: 'This line has been injected and is not part of the method.'},
            linesDecorationsClassName: 'codicon-export codicon',
            shouldFillLineOnLineBreak: false,
          },
        };
      });
      injectedLinesDecorationCollection.set(injectedLinesDecorations);
    });
    return injectedLinesDecorationCollection;
  }

  private setupInjectedLines(editor: MonacoEditor.IStandaloneCodeEditor) {
    const decorations = this.decorateInjectedLines(editor);
    decorations.onDidChange(() => {
      const lineNumbers = decorations.getRanges().flatMap(range => UtilMethods.getNumberRange(range.startLineNumber, range.endLineNumber));
      editor.updateOptions({lineNumbers: this.getLineNumberFunction(lineNumbers)});
    });
  }
}
