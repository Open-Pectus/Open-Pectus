import { AfterViewInit, ChangeDetectionStrategy, Component, ElementRef, Input, OnDestroy, ViewChild } from '@angular/core';
import '@codingame/monaco-vscode-json-default-extension';
import getLanguagesServiceOverride from '@codingame/monaco-vscode-languages-service-override';
import getModelServiceOverride from '@codingame/monaco-vscode-model-service-override';
import getTextmateServiceOverride from '@codingame/monaco-vscode-textmate-service-override';
import '@codingame/monaco-vscode-theme-defaults-default-extension';
import getThemeServiceOverride from '@codingame/monaco-vscode-theme-service-override';
import { concatLatestFrom } from '@ngrx/effects';
import { Store } from '@ngrx/store';
import { buildWorkerDefinition } from 'monaco-editor-workers';
import { editor as MonacoEditor, KeyCode, languages, Range, Uri } from 'monaco-editor/esm/vs/editor/editor.api.js'; // importing as 'monaco-editor' causes issues: https://github.com/CodinGame/monaco-vscode-api/issues/162
import { initServices, MonacoLanguageClient } from 'monaco-languageclient';
import { combineLatest, filter, firstValueFrom, Observable, Subject, take, takeUntil } from 'rxjs';
import { CloseAction, ErrorAction, MessageTransports } from 'vscode-languageclient/lib/common/client';
import { toSocket, WebSocketMessageReader, WebSocketMessageWriter } from 'vscode-ws-jsonrpc';
import { createConfiguredEditor, createModelReference } from 'vscode/monaco';
import { MethodLine } from '../../api';
import { UtilMethods } from '../../shared/util-methods';
import { MethodEditorActions } from './ngrx/method-editor.actions';
import { MethodEditorSelectors } from './ngrx/method-editor.selectors';

buildWorkerDefinition('./assets/monaco-editor-workers/workers', window.location.origin, false);

const startedLineClassName = 'started-line';
const executedLineClassName = 'executed-line';
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
  @Input() readOnlyEditor = false;
  @ViewChild('editor', {static: true}) editorElement!: ElementRef<HTMLDivElement>;
  private componentDestroyed = new Subject<void>();
  private editor?: MonacoEditor.IStandaloneCodeEditor;
  private readonly languageId = 'json';
  private methodContent = this.store.select(MethodEditorSelectors.methodContent);
  private monacoServicesInitialized = this.store.select(MethodEditorSelectors.monacoServicesInitialized);
  private executedLineIds = this.store.select(MethodEditorSelectors.executedLineIds);
  private injectedLineIds = this.store.select(MethodEditorSelectors.injectedLineIds);
  private startedLineIds = this.store.select(MethodEditorSelectors.startedLineIds);
  private lineIds = this.store.select(MethodEditorSelectors.lineIds);
  private methodLines = this.store.select(MethodEditorSelectors.methodLines);
  private storeModelChangedFromHere = false;
  private editorModelChangedFromStore = false;

  constructor(private store: Store) {}

  async ngAfterViewInit() {
    await this.initServices();
    this.registerLanguages();
    this.editor = await this.setupEditor();
    this.setupWebSocket(`ws://localhost:30000/sampleServer`);

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
      userServices: {
        ...getThemeServiceOverride(),
        ...getTextmateServiceOverride(),
        ...getModelServiceOverride(),
        ...getLanguagesServiceOverride(),
      },
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

  private async setupEditor() {
    const editor = await this.constructEditor();
    this.setupOnEditorChanged(editor);
    this.setupOnStoreModelChanged(editor);
    this.setupInjectedLines(editor);
    this.setupStartedAndExecutedLines(editor);

    return editor;
  }

  private async constructEditor() {
    const uri = Uri.parse('/tmp/model.json');
    const methodContent = await firstValueFrom(this.methodContent);
    const modelRef = await createModelReference(uri, methodContent);
    // noinspection JSUnresolvedReference
    modelRef.object.setLanguageId(this.languageId);

    // noinspection JSUnresolvedReference
    const editor = createConfiguredEditor(this.editorElement.nativeElement, {
      model: modelRef.object.textEditorModel,
      fontSize: 18,
      glyphMargin: false,
      fixedOverflowWidgets: true,
      lineNumbersMinChars: UtilMethods.isMobile ? 1 : 3,
      minimap: {
        enabled: UtilMethods.isDesktop,
      },
    });
    this.componentDestroyed.pipe(take(1)).subscribe(() => {
      modelRef.object.dispose();
      modelRef.dispose();
      editor.dispose();
    });
    return editor;
  }

  private setupOnEditorChanged(editor: MonacoEditor.IStandaloneCodeEditor) {
    editor.onDidChangeModelContent(() => {
      if(this.editorModelChangedFromStore) return;
      setTimeout(() => { // setTimeout to allow for line id decorations to be placed before this is executed
        const model = editor.getModel();
        if(model === null) return;
        const linesContents = model.getLinesContent();

        const lines = linesContents.map<MethodLine>((lineContent, index) => {
          const decorations = model.getLineDecorations(index + 1);
          const idDecoration = decorations.find(decoration => decoration.options.className?.startsWith(lineIdClassNamePrefix));
          const id = idDecoration?.options.className?.substring(lineIdClassNamePrefix.length);
          const isExecuted = decorations.find(decoration => decoration.options.className === executedLineClassName) !== undefined;
          const isInjected = decorations.find(decoration => decoration.options.className === injectedLineClassName) !== undefined;
          return {
            id: id ?? crypto.randomUUID(),
            content: lineContent,
            is_executed: isExecuted,
            is_injected: isInjected,
          };
        });
        this.storeModelChangedFromHere = true;
        this.store.dispatch(MethodEditorActions.linesChanged({lines}));
        this.storeModelChangedFromHere = false;
      });
    });
  }

  // Sets up both edits to content and line id decorations, because it's important that they happen right after each other and in this order.
  private setupOnStoreModelChanged(editor: MonacoEditor.IStandaloneCodeEditor) {
    const lineIdsDecorationCollection = editor.createDecorationsCollection();
    this.methodLines.pipe(
      filter(() => !this.storeModelChangedFromHere),
      takeUntil(this.componentDestroyed),
    ).subscribe(methodLines => {
      // Apply edits
      const methodContent = methodLines.map(line => line.content).join('\n');
      const preEditSelection = editor.getSelection();

      this.editorModelChangedFromStore = true;
      editor.getModel()?.applyEdits([{range: new Range(0, 0, Number.MAX_VALUE, Number.MAX_VALUE), text: methodContent}]);
      this.editorModelChangedFromStore = false;

      if(preEditSelection !== null) editor.setSelection(preEditSelection);

      // Set line id decorations
      const lineIds = methodLines.map(line => line.id);
      const lineIdDecorations = lineIds.map<MonacoEditor.IModelDeltaDecoration>((lineId, index) => {
        const lineNumber = index + 1;
        return {
          range: new Range(lineNumber, 0, lineNumber, 0),
          options: {
            className: lineIdClassNamePrefix + lineId,
            shouldFillLineOnLineBreak: false,
            stickiness: MonacoEditor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
          },
        };
      });
      lineIdsDecorationCollection.set(lineIdDecorations);
    });
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

  private setupStartedAndExecutedLines(editor: MonacoEditor.IStandaloneCodeEditor) {
    const startedAndExecutedLinesDecorationCollection = this.setupDecoratingStartedAndExecutedLines(editor);
    if(this.readOnlyEditor) {
      editor.updateOptions({readOnly: true, readOnlyMessage: {value: 'You cannot edit an already executed program.'}});
    } else {
      this.setupLockingStartedAndExecutedLines(editor, startedAndExecutedLinesDecorationCollection);
    }
  }

  private setupLockingStartedAndExecutedLines(editor: MonacoEditor.IStandaloneCodeEditor,
                                              startedAndExecutedLineDecorations: MonacoEditor.IEditorDecorationsCollection) {
    const lockEditorIfSelectionIntersectsExecutedLines = () => {
      const selectionInLockedRange = editor.getSelections()?.some(selection => {
        return startedAndExecutedLineDecorations.getRanges()
          .flatMap(range => UtilMethods.getNumberRange(range.startLineNumber, range.endLineNumber))
          .some(lockedLineNumber => {
            return selection.intersectRanges(new Range(lockedLineNumber, 0, lockedLineNumber + 1, 0));
          });
      });
      editor.updateOptions({readOnly: selectionInLockedRange, readOnlyMessage: {value: 'Cannot edit lines already started or executed.'}});
    };
    editor.onDidChangeCursorSelection(lockEditorIfSelectionIntersectsExecutedLines);
    this.executedLineIds.pipe(takeUntil(this.componentDestroyed)).subscribe(lockEditorIfSelectionIntersectsExecutedLines);

    // Block specifically delete/backspace when at the ending/starting edge of the line before/after the locked line.
    editor.onKeyDown(event => {
      const isBackspace = event.keyCode === KeyCode.Backspace;
      const isDelete = event.keyCode === KeyCode.Delete;
      if(!isBackspace && !isDelete) return;
      const selectionInLockedRange = editor.getSelections()?.some(selection => {
        return startedAndExecutedLineDecorations.getRanges()
          .flatMap(range => UtilMethods.getNumberRange(range.startLineNumber, range.endLineNumber))
          .some(lockedLineNumber => {
            const previousLineLength = editor?.getModel()?.getLineLength(Math.max(1, lockedLineNumber - 1)) ?? 0;
            const lockedRange = isDelete
                                ? new Range(lockedLineNumber - 1, previousLineLength + 1, lockedLineNumber, 0)
                                : new Range(lockedLineNumber, 0, lockedLineNumber + 1, 1);
            return selection.intersectRanges(lockedRange);
          });
      });
      if(selectionInLockedRange) {
        event.stopPropagation();
        event.preventDefault();
      }
    });
  }

  private setupDecoratingStartedAndExecutedLines(editor: MonacoEditor.IStandaloneCodeEditor) {
    const startedAndExecutedLinesDecorationsCollection = editor.createDecorationsCollection();
    const createDecoration = (lineIds: string[], lineClassName: string, hoverMessage: string) => (executedLineId: string) => {
      const lineNumber = lineIds.findIndex(lineId => lineId === executedLineId) + 1;
      if(lineNumber === undefined) throw Error(`could not find line id decoration with id ${executedLineId}`);
      return {
        range: new Range(lineNumber, 0, lineNumber, 0),
        options: {
          isWholeLine: true,
          className: lineClassName,
          hoverMessage: {value: hoverMessage},
          shouldFillLineOnLineBreak: false,
          stickiness: MonacoEditor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
        },
      };
    };

    combineLatest([this.startedLineIds, this.executedLineIds]).pipe(
      concatLatestFrom(() => this.lineIds),
      takeUntil(this.componentDestroyed),
    ).subscribe(([[startedLineIds, executedLineIds], lineIds]) => {
      const executedLinesDecorations = executedLineIds.map<MonacoEditor.IModelDeltaDecoration>(
        createDecoration(lineIds, executedLineClassName, 'This line has been executed and is no longer editable.'),
      );
      const startedLinesDecorations = startedLineIds.map<MonacoEditor.IModelDeltaDecoration>(
        createDecoration(lineIds, startedLineClassName, 'This line has been started and is no longer editable.'),
      );
      startedAndExecutedLinesDecorationsCollection.set([...executedLinesDecorations, ...startedLinesDecorations]);
    });
    return startedAndExecutedLinesDecorationsCollection;
  }

  private decorateInjectedLines(editor: MonacoEditor.IStandaloneCodeEditor) {
    const injectedLinesDecorationCollection = editor.createDecorationsCollection();
    this.injectedLineIds.pipe(
      concatLatestFrom(() => this.lineIds),
      takeUntil(this.componentDestroyed),
    ).subscribe(([injectedLineIds, lineIds]) => {
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
            stickiness: MonacoEditor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges,
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
