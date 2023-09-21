import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, Input, OnDestroy, ViewChild } from '@angular/core';
import { Store } from '@ngrx/store';
import { buildWorkerDefinition } from 'monaco-editor-workers';
import { editor, editor as MonacoEditor, languages, Range, Uri } from 'monaco-editor/esm/vs/editor/editor.api.js'; // importing as 'monaco-editor' causes issues: https://github.com/CodinGame/monaco-vscode-api/issues/162
import { initServices, MonacoLanguageClient } from 'monaco-languageclient';
import { combineLatest, firstValueFrom, Observable, Subject, take, takeUntil } from 'rxjs';
import { CloseAction, ErrorAction, MessageTransports } from 'vscode-languageclient/lib/common/client';
import { toSocket, WebSocketMessageReader, WebSocketMessageWriter } from 'vscode-ws-jsonrpc';
import 'vscode/default-extensions/json';
import 'vscode/default-extensions/theme-defaults';
import { createConfiguredEditor, createModelReference } from 'vscode/monaco';
import { MethodLine } from '../../api';
import { UtilMethods } from '../../shared/util-methods';
import { MethodEditorActions } from './ngrx/method-editor.actions';
import { MethodEditorSelectors } from './ngrx/method-editor.selectors';
import TrackedRangeStickiness = editor.TrackedRangeStickiness;

buildWorkerDefinition('./assets/monaco-editor-workers/workers', window.location.origin, false);

const lockedLineClassName = 'locked-line';
const injectedLineClassName = 'injected-line';
const lineIdClassNamePrefix = 'line-id-';

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
  private methodContent = this.store.select(MethodEditorSelectors.methodContent);
  private monacoServicesInitialized = this.store.select(MethodEditorSelectors.monacoServicesInitialized);
  private lockedLineIds = this.store.select(MethodEditorSelectors.lockedLineIds);
  private injectedLineIds = this.store.select(MethodEditorSelectors.injectedLineIds);
  private lineIds = this.store.select(MethodEditorSelectors.lineIds);

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
    const modelRef = await createModelReference(uri, await firstValueFrom(this.methodContent));
    modelRef.object.setLanguageId(this.languageId);

    const editor = createConfiguredEditor(this.editorElement.nativeElement, {
      model: modelRef.object.textEditorModel,
      fontSize: 18,
      glyphMargin: false,
      fixedOverflowWidgets: true,
    });

    editor.onDidChangeModelContent(() => {
      const model = editor.getModel();
      if(model === null) return;
      const linesContents = model.getLinesContent();

      const lines = linesContents.map<MethodLine>((lineContent, index) => {
        const decorations = model.getLineDecorations(index + 1);
        const idDecoration = decorations.find(decoration => decoration.options.className?.startsWith(lineIdClassNamePrefix));
        const id = idDecoration?.options.className?.substring(lineIdClassNamePrefix.length);
        const isLocked = decorations.find(decoration => decoration.options.className === lockedLineClassName) !== undefined;
        const isInjected = decorations.find(decoration => decoration.options.className === injectedLineClassName) !== undefined;
        return {
          id: id ?? crypto.randomUUID(),
          content: lineContent,
          is_locked: isLocked,
          is_injected: isInjected,
        };
      });
      this.store.dispatch(MethodEditorActions.linesChanged({lines}));
    });

    this.componentDestroyed.pipe(take(1)).subscribe(() => {
      modelRef.object.dispose();
      modelRef.dispose();
      editor.dispose();
    });

    const idDecorationsCollection = this.setupDecorateLinesWithIds(editor);
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
    const lockedLinesDecorations = this.decorateLockedLines(editor);
    this.lockLinesViaReadOnlyEditor(editor, lockedLinesDecorations);
  }

  private lockLinesViaReadOnlyEditor(editor: MonacoEditor.IStandaloneCodeEditor,
                                     lockedLineDecorations: MonacoEditor.IEditorDecorationsCollection) {
    editor.onDidChangeCursorSelection(_ => {
      const selectionInLockedRange = editor.getSelections()?.some(selection => {
        return lockedLineDecorations.getRanges()
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
    combineLatest([this.lockedLineIds, this.lineIds]).pipe(takeUntil(this.componentDestroyed)).subscribe(([lockedLineIds, lineIds]) => {
      const lockedLinesDecorations = lockedLineIds.map<MonacoEditor.IModelDeltaDecoration>(lockedLineId => {
        const lineNumber = lineIds.findIndex(lineId => lineId === lockedLineId) + 1;
        if(lineNumber === undefined) throw Error(`could not find line id decoration with id ${lockedLineId}`);
        return {
          range: new Range(lineNumber, 0, lineNumber, 0),
          options: {
            isWholeLine: true,
            className: lockedLineClassName,
            hoverMessage: {value: 'This line has been executed and is no longer editable.'},
            shouldFillLineOnLineBreak: false,
            stickiness: TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
          },
        };
      });
      lockedLinesDecorationsCollection.set(lockedLinesDecorations);
    });
    return lockedLinesDecorationsCollection;
  }

  private decorateInjectedLines(editor: MonacoEditor.IStandaloneCodeEditor) {
    const injectedLinesDecorationCollection = editor.createDecorationsCollection();
    combineLatest([this.injectedLineIds, this.lineIds]).pipe(takeUntil(this.componentDestroyed)).subscribe(([injectedLineIds, lineIds]) => {
      const injectedLinesDecorations = injectedLineIds.map<MonacoEditor.IModelDeltaDecoration>(injectedLineId => {
        const lineNumber = lineIds.findIndex(lineId => lineId === injectedLineId) + 1;
        return {
          range: new Range(lineNumber, 0, lineNumber, 0),
          options: {
            className: injectedLineClassName,
            isWholeLine: true,
            hoverMessage: {value: 'This line has been injected and is not part of the methodContent.'},
            linesDecorationsClassName: 'codicon-export codicon',
            shouldFillLineOnLineBreak: false,
            stickiness: TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
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

  private setupDecorateLinesWithIds(editor: MonacoEditor.IStandaloneCodeEditor) {
    const lineIdsDecorationCollection = editor.createDecorationsCollection();
    this.lineIds.pipe(takeUntil(this.componentDestroyed)).subscribe(lineIds => {
      const lineIdDecorations = lineIds.map<MonacoEditor.IModelDeltaDecoration>((lineId, index) => {
        const lineNumber = index + 1;
        return {
          range: new Range(lineNumber, 0, lineNumber, 0),
          options: {
            className: lineIdClassNamePrefix + lineId,
            shouldFillLineOnLineBreak: false,
            stickiness: TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
          },
        };
      });
      lineIdsDecorationCollection.set(lineIdDecorations);
    });
    return lineIdsDecorationCollection;
  }
}
